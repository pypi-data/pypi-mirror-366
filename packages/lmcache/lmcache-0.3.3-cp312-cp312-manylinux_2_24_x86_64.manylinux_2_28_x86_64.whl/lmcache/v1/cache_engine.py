# SPDX-License-Identifier: Apache-2.0
# Standard
from collections import defaultdict
from typing import Dict, Generator, List, Optional, Union
import asyncio
import multiprocessing
import time

# Third Party
import torch

# First Party
from lmcache.config import LMCacheEngineMetadata
from lmcache.logging import init_logger
from lmcache.observability import LMCacheStatsLogger, LMCStatsMonitor
from lmcache.usage_context import InitializeUsageContext
from lmcache.utils import CacheEngineKey, _lmcache_nvtx_annotate
from lmcache.v1.config import LMCacheEngineConfig
from lmcache.v1.distributed_server import (
    DistributedServerInterface,
    NaiveDistributedServer,
)
from lmcache.v1.gpu_connector import (
    GPUConnectorInterface,
    VLLMBufferLayerwiseGPUConnector,
    VLLMPagedMemLayerwiseGPUConnector,
)
from lmcache.v1.lookup_server import LookupServerInterface, RedisLookupServer
from lmcache.v1.memory_management import AdHocMemoryAllocator  # noqa: E501
from lmcache.v1.memory_management import CuFileMemoryAllocator  # noqa: E501
from lmcache.v1.memory_management import (
    MemoryAllocatorInterface,
    MemoryFormat,
    MixedMemoryAllocator,
    NixlCPUMemoryAllocator,
)
from lmcache.v1.storage_backend.storage_manager import StorageManager
from lmcache.v1.token_database import (
    ChunkedTokenDatabase,
    SegmentTokenDatabase,
    TokenDatabase,
)

logger = init_logger(__name__)


class CacheEngineEndSignal:
    pass


class LMCacheEngine:
    """The main class for the cache engine.

    When storing the KV caches into the cache engine, it takes GPU KV
    caches from the serving engine and convert them into MemoryObjs that
    resides in the CPU. The MemoryObjs are then being stored into the
    StorageBackends in an asynchronous manner.

    When retrieving the KV caches from the cache engine, it fetches the
    MemoryObjs from the StorageBackends and convert them into GPU KV caches
    by GPUConnectors specialized for the serving engine.

    It also supports prefetching the KV caches from the StorageBackends.
    It relies on the StorageBackends to manage the requests of prefetching
    and real retrieval and avoid the conflicts.
    """

    def __init__(
        self,
        config: LMCacheEngineConfig,
        metadata: LMCacheEngineMetadata,
        memory_allocator: MemoryAllocatorInterface,
        token_database: TokenDatabase,
        gpu_connector: GPUConnectorInterface,
    ):
        logger.info(f"Creating LMCacheEngine with config: {config}")
        self.config = config
        self.metadata = metadata
        self.memory_allocator = memory_allocator
        self.token_database = token_database
        self.gpu_connector = gpu_connector

        self.enable_p2p = config.enable_p2p

        self.enable_controller = config.enable_controller

        # NOTE: Unix systems use fork by default
        multiprocessing.set_start_method("spawn", force=True)

        self.lookup_server: Optional[LookupServerInterface] = None
        if self.enable_p2p:
            self.lookup_server = RedisLookupServer(config)

        # avoid circular import
        # First Party
        from lmcache.v1.cache_controller import LMCacheWorker

        self.lmcache_worker: Optional[LMCacheWorker] = None
        if self.enable_controller:
            self.lmcache_worker = LMCacheWorker(config, metadata, self)

        self.storage_manager = StorageManager(
            config,
            metadata,
            self.memory_allocator,
            self.lmcache_worker,
            self.lookup_server,
        )

        # HACK: remove this in the future
        # NOTE (Jiayi): This is currently used to support
        # dropping the kv cache in nixl backend at decoder.
        self.remove_after_retrieve = (
            config.enable_nixl and config.nixl_role == "receiver"
        )

        self.distributed_server: Optional[DistributedServerInterface] = None

        if self.enable_p2p or self.enable_controller:
            self.distributed_loop = asyncio.get_event_loop()
            assert isinstance(self.storage_manager, StorageManager)
            self.distributed_server = NaiveDistributedServer(
                self.storage_manager,
                self.lookup_server,
                self.distributed_loop,
                config,
            )

        self.use_layerwise = config.use_layerwise
        self.num_layers = metadata.kv_shape[0]
        if self.use_layerwise:
            if config.enable_blending:
                self.fmt = MemoryFormat.KV_2TD
            else:
                self.fmt = MemoryFormat.KV_T2D

        self.lookup_cache = {}
        # request_id -> [pinned keys]
        self.lookup_pins = defaultdict(list)

        InitializeUsageContext(config.to_original_config(), metadata)
        self.stats_monitor = LMCStatsMonitor.GetOrCreate()

        self.post_inited = False

    def post_init(self, **kwargs) -> None:
        if not self.post_inited:
            logger.info("Post-initializing LMCacheEngine")
            self.gpu_connector.initialize_kvcaches_ptr(**kwargs)
            self.post_inited = True

    @_lmcache_nvtx_annotate
    @torch.inference_mode()
    def store(
        self,
        tokens: Optional[torch.Tensor] = None,
        hashes: Optional[List[int]] = None,
        offsets: Optional[List[int]] = None,
        mask: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> None:
        """Store the tokens/hashes and mask into the cache engine.

        :param Optional[torch.Tensor] tokens: The tokens of the corresponding KV caches.

        :param Optional[List[int]] hashes: The hashes of the corresponding KV caches.

        :param Optional[torch.Tensor] mask: The mask for the tokens. Should
            have the same length as tokens. And the mask should ALWAYS be like
            FFFFFTTTTTTT, where True means the tokens needs to be matched,
            and the Falses will ALWAYS be at the PREFIX of the tensor.

        :param **kwargs: The additional arguments for the storage backend which
            will be passed into the gpu_connector.
            Should include KV cache specific information (e.g., paged KV buffer
            and the page tables).

        :raises: ValueError if the number of Falses in the mask is not a
            multiple of the chunk size.
        """

        if mask is not None:
            num_to_store_tokens = torch.sum(mask).item()
        elif tokens is not None:
            num_to_store_tokens = len(tokens)
        elif hashes is not None:
            num_to_store_tokens = sum(offsets)
            kwargs["slot_mapping"] = torch.tensor(
                kwargs["slot_mapping"], dtype=torch.long, device="cuda"
            )

        assert tokens is not None or hashes is not None, (
            "Either 'tokens' or 'hashes' must be provided."
        )

        monitor_req_id = self.stats_monitor.on_store_request(num_to_store_tokens)

        starts = []
        ends = []
        keys = []
        memory_objs = []

        offload_time = 0.0
        put_time = 0.0
        tot_kv_size = 0
        tot_token_num = 0
        t = time.perf_counter()

        for start, end, key in self.token_database.process_tokens(
            tokens, hashes, offsets, mask
        ):
            assert isinstance(key, CacheEngineKey)
            # Allocate the memory object
            num_tokens = end - start
            kv_shape = self.gpu_connector.get_shape(num_tokens)
            kv_dtype = self.metadata.kv_dtype

            # TODO (Jiayi): should be batched in the future
            memory_obj = self.storage_manager.allocate(kv_shape, kv_dtype)
            if memory_obj is None:
                logger.warning(
                    "Failed to allocate memory for the KV cache.\n"
                    "The KV cache will not be stored."
                )
                break

            starts.append(start)
            ends.append(end)
            keys.append(key)
            memory_objs.append(memory_obj)
            tot_kv_size += memory_obj.get_size()
            tot_token_num += num_tokens

        # memory_objs might be empty, directly return to avoid sending tokens
        if not memory_objs:
            return
        self.gpu_connector.batched_from_gpu(memory_objs, starts, ends, **kwargs)
        offload_time += time.perf_counter() - t

        t = time.perf_counter()

        transfer_spec = kwargs.get("transfer_spec", None)
        self.storage_manager.batched_put(keys, memory_objs, transfer_spec=transfer_spec)
        put_time += time.perf_counter() - t

        tot_time = offload_time + put_time

        if self.lookup_server is not None:
            self.lookup_server.batched_insert(keys)

        logger.info(
            "Stored %d out of total %d tokens. size: %.4f gb, cost %.4f ms, "
            "throughput: %.4f GB/s; offload_time: %.4f ms, put_time: %.4f ms",
            tot_token_num,
            num_to_store_tokens,
            tot_kv_size / 1024**3,
            tot_time * 1000,
            tot_kv_size / tot_time / 1024**3,
            offload_time * 1000,
            put_time * 1000,
        )

        self.stats_monitor.on_store_finished(monitor_req_id, tot_token_num)

    @_lmcache_nvtx_annotate
    @torch.inference_mode()
    def store_layer(
        self,
        tokens: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> Generator[None, None, None]:
        """
        Store the KV cache in a layerwise manner.

        :param torch.Tensor tokens: The tokens of the corresponding KV caches.

        :param Optional[torch.Tensor] mask: The mask for the tokens. Should
            have the same length as tokens. And the mask should ALWAYS be like
            FFFFFTTTTTTT, where True means the tokens needs to be matched.

        :param **kwargs: The additional arguments for the storage backend which
            will be passed into the gpu_connector.

        return: A generator that yields None. In the first iteration, the
            generator allocates the memory objects for all layers and moves
            the KV cache of the first layer from GPU to CPU. In the next
            iterations, it moves the KV cache of layer i from GPU to the memory
            objects (on CPU) and puts the memory objects of layer i-1 to the
            storage backends. In the last iteration, it puts the memory objects
            of the last layer to the storage backends.
        """

        if mask is not None:
            num_to_store_tokens = torch.sum(mask).item()
        else:
            num_to_store_tokens = len(tokens)
        monitor_req_id = self.stats_monitor.on_store_request(num_to_store_tokens)

        starts = []
        ends = []
        keys = []
        memory_objs = []
        tot_token_num = 0
        kv_dtype = self.metadata.kv_dtype
        for start, end, key in self.token_database.process_tokens(
            tokens=tokens, mask=mask
        ):
            assert isinstance(key, CacheEngineKey)

            keys_multi_layer = key.split_layers(self.num_layers)

            # Only check the first layer
            if self.storage_manager.contains(keys_multi_layer[0]):
                continue

            # Allocate the memory object
            num_tokens = end - start
            kv_shape_single_layer = self.gpu_connector.get_shape(num_tokens)

            memory_objs_multi_layer = self.storage_manager.batched_allocate(
                kv_shape_single_layer,
                kv_dtype,
                batch_size=self.num_layers,
                fmt=self.fmt,
            )

            if memory_objs_multi_layer is None:
                logger.warning(
                    "Failed to allocate memory for the KV cache.\n"
                    "The KV cache will not be stored."
                )
                break

            starts.append(start)
            ends.append(end)
            keys.append(keys_multi_layer)
            memory_objs.append(memory_objs_multi_layer)
            tot_token_num += num_tokens

            # Update lookup server
            if self.lookup_server is not None:
                self.lookup_server.batched_insert(keys_multi_layer)

        if keys:
            # Transpose the keys and memory objects into layer major format
            memory_objs = [list(row) for row in zip(*memory_objs, strict=False)]
            keys = [list(row) for row in zip(*keys, strict=False)]

            assert isinstance(
                self.gpu_connector,
                (VLLMPagedMemLayerwiseGPUConnector, VLLMBufferLayerwiseGPUConnector),
            )

            mem_obj_generator = self.gpu_connector.batched_from_gpu(
                memory_objs, starts, ends, **kwargs
            )

            next(mem_obj_generator)

            for layer_id in range(self.num_layers):
                yield
                next(mem_obj_generator)
                self.storage_manager.batched_put(keys[layer_id], memory_objs[layer_id])
        else:
            # If no cache are found, we still need to yield to avoid
            # `StopIteration`
            for layer_id in range(self.num_layers):
                yield

        self.stats_monitor.on_store_finished(monitor_req_id, tot_token_num)
        logger.debug(f"Stored {tot_token_num} out of total {len(tokens)} tokens")
        yield

    @_lmcache_nvtx_annotate
    @torch.inference_mode()
    def retrieve(
        self,
        tokens: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        """Retrieve the KV caches from the cache engine. And put the retrieved
        KV cache to the serving engine via the GPU connector.

        :param torch.Tensor tokens: The tokens of the corresponding KV caches.

        :param Optional[torch.Tensor] mask: The mask for the tokens. Should
            have the same length as tokens. And the mask should ALWAYS be like
            FFFFFTTTTTTT, where True means the tokens needs to be matched,
            and the Falses will ALWAYS be at the PREFIX of the tensor.

        :param **kwargs: The additional arguments for the storage backend which
            will be passed into the gpu_connector.
            Should include KV cache specific information (e.g., paged KV buffer
            and the page tables).

        :return: the boolean mask indicating which tokens are retrieved. The
            length of the mask should be the same as the tokens. On CPU.

        :raises: ValueError if the number of Falses in the mask is not a
            multiple of the chunk size.
        """
        if mask is not None:
            num_required_tokens = torch.sum(mask).item()
        else:
            num_required_tokens = len(tokens)
        monitor_req_id = self.stats_monitor.on_retrieve_request(num_required_tokens)

        ret_mask = torch.zeros_like(tokens, dtype=torch.bool, device="cpu")

        key_mapping: Dict[str, List[CacheEngineKey]] = {}
        start_mapping: Dict[str, List[int]] = {}
        end_mapping: Dict[str, List[int]] = {}

        reordered_keys = []
        reordered_memory_objs = []
        reordered_starts = []
        reordered_ends = []
        for start, end, key in self.token_database.process_tokens(
            tokens=tokens, mask=mask
        ):
            assert isinstance(key, CacheEngineKey)

            if key in self.lookup_cache:
                # TODO(Jiayi): we can reduce the number of `contains` calls
                # by checking the lookup cache first (should be updated in `lookup`)
                pass
            else:
                # NOTE: key should always be in the lookup cache once
                # we support it.
                location = self.storage_manager.contains(key)
                if location is None:
                    # TODO(Jiayi): Need to refactor P2P as a storage backend to
                    # clean up the following code.
                    if self.enable_p2p:
                        future_memory_obj = asyncio.run_coroutine_threadsafe(
                            self.distributed_server.issue_get(key),
                            self.distributed_loop,
                        )
                        memory_obj = future_memory_obj.result()
                        if memory_obj:
                            reordered_keys.append(key)
                            reordered_memory_objs.append(memory_obj)
                            reordered_starts.append(start)
                            reordered_ends.append(end)
                            ret_mask[start:end] = True
                        else:
                            # NOTE: break for P2P retrieve KV because of no required
                            # memory obj
                            break
                        continue
                    break

                # NOTE: Here we make the assumption that the underlying
                # storage backend support pin operation, and the memory
                # object is already pinned in the storage backend.
                ret_mask[start:end] = True

                if location not in key_mapping:
                    key_mapping[location] = [key]
                    start_mapping[location] = [start]
                    end_mapping[location] = [end]
                    continue

            assert location is not None

            key_mapping[location].append(key)
            start_mapping[location].append(start)
            end_mapping[location].append(end)

        # TODO(Jiayi): We can parallelize the retrieval from
        # different storage backends.
        for location, keys in key_mapping.items():
            memory_objs = self.storage_manager.batched_get(
                keys=keys,
                location=location,
            )
            reordered_memory_objs.extend(memory_objs)
            reordered_keys.extend(keys)
            reordered_starts.extend(start_mapping[location])
            reordered_ends.extend(end_mapping[location])

        # NOTE(Jiayi): memory_obj doesn't have to be a pinned
        # cpu tensor for the sake of performance.
        # For example, disk->gpu is faster than disk->cpu->gpu.
        # RDMA is another example.
        self.gpu_connector.batched_to_gpu(
            reordered_memory_objs, reordered_starts, reordered_ends, **kwargs
        )

        # TODO(Jiayi): Remove the following for loop with batched operations
        for key, memory_obj in zip(reordered_keys, reordered_memory_objs, strict=False):
            if self.remove_after_retrieve:
                self.storage_manager.remove(key)
            memory_obj.ref_count_down()

        retrieved_tokens = torch.sum(ret_mask)
        self.stats_monitor.on_retrieve_finished(monitor_req_id, retrieved_tokens)
        logger.info(
            f"Retrieved {retrieved_tokens} "
            f"out of {num_required_tokens} "
            f"out of total {len(tokens)} tokens"
        )
        return ret_mask

    @_lmcache_nvtx_annotate
    @torch.inference_mode()
    def retrieve_layer(
        self,
        tokens: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> Generator[Optional[torch.Tensor], None, None]:
        """
        Retrieve the KV cache in a layerwise manner.

        :param torch.Tensor tokens: The tokens of the corresponding KV caches.

        :param Optional[torch.Tensor] mask: The mask for the tokens. Should
            have the same length as tokens. And the mask should ALWAYS be like
            FFFFFTTTTTTT, where True means the tokens needs to be matched.

        :param **kwargs: The additional arguments for the storage backend which
            will be passed into the gpu_connector.

        return: A generator that yields Optional[torch.Tensor]. The tensor will
            be the boolean mask indicating which tokens are retrieved and will
            only be returned in the last iteration. In the first iteration,
            the generator retrieve the memory objects of the first layer from
            the storage backends. In the next iterations, it moves the KV cache
            of layer i from the memory objects (on CPU) to GPU and retrieves
            the memory objects of layer i+1 from the storage backends. In the
            last iteration, it moves the memory objects of the last layer to
            the GPU.
        """

        if mask is not None:
            num_required_tokens = torch.sum(mask).item()
        else:
            num_required_tokens = len(tokens)
        monitor_req_id = self.stats_monitor.on_retrieve_request(num_required_tokens)

        ret_mask = torch.zeros_like(tokens, dtype=torch.bool, device="cpu")

        starts = []
        ends = []
        keys = []
        for start, end, key in self.token_database.process_tokens(
            tokens=tokens, mask=mask
        ):
            assert isinstance(key, CacheEngineKey)

            keys_multi_layer = key.split_layers(self.num_layers)

            # NOTE: Only check the first layer
            if not self.storage_manager.contains(keys_multi_layer[0]):
                break

            starts.append(start)
            ends.append(end)
            keys.append(keys_multi_layer)

            ret_mask[start:end] = True

        if keys:
            # Transpose the keys into layer major format
            keys_layer_major = [list(row) for row in zip(*keys, strict=False)]

            get_generator = self.storage_manager.layerwise_batched_get(keys_layer_major)

            assert isinstance(
                self.gpu_connector,
                (
                    VLLMPagedMemLayerwiseGPUConnector,
                    VLLMBufferLayerwiseGPUConnector,
                ),
            )
            mem_obj_consumer = self.gpu_connector.batched_to_gpu(starts, ends, **kwargs)
            next(mem_obj_consumer)

            to_count_down = []
            for layer_id in range(self.num_layers):
                tasks = next(get_generator)

                assert None not in tasks

                yield None

                mem_objs_layer = [task.result() for task in tasks]
                mem_obj_consumer.send(mem_objs_layer)
                to_count_down.extend(mem_objs_layer)

            for mem_obj in to_count_down:
                mem_obj.ref_count_down()
        else:
            # If no cache are found, we still need to yield to avoid
            # `StopIteration`
            for layer_id in range(self.num_layers):
                yield None

        yield None

        # synchronize the last layer
        next(mem_obj_consumer)

        retrieved_tokens = torch.sum(ret_mask)
        self.stats_monitor.on_retrieve_finished(monitor_req_id, retrieved_tokens)
        logger.debug(
            f"Retrieved {retrieved_tokens} "
            f"out of {num_required_tokens} "
            f"out of total {len(tokens)} tokens"
        )

        yield ret_mask

    @_lmcache_nvtx_annotate
    def prefetch(
        self,
        tokens: Union[torch.Tensor, List[int]],
        mask: Optional[torch.Tensor] = None,
    ) -> None:
        """Launch the prefetching process in the storage manager to load the
        KV to the local CPU memory
        """
        for start, end, key in self.token_database.process_tokens(
            tokens=tokens, mask=mask
        ):
            assert isinstance(key, CacheEngineKey)
            self.storage_manager.prefetch(key)

    # TODO(Jiayi): Currently, search_range is only used for testing.
    @_lmcache_nvtx_annotate
    def lookup(
        self,
        tokens: Union[torch.Tensor, List[int]],
        search_range: Optional[List[str]] = None,
        request_id: Optional[str] = None,
        pin: bool = False,
    ) -> int:
        """
        Checks the existence of KV cache of the tokens from the cache engine.

        :param tokens: the input tokens, with shape [seq_len]

        :param Optional[List[str]] search_range: The range of storage backends
        to search in. Should be a subset of
        ["LocalCPUBackend", "LocalDiskBackend"] for now.
        If None, search in all backends.

        :param str request_id: The request ID to associate with the lookup

        :param bool pin: If True, pin the KV cache in the storage.

        :return: An int indicating how many prefix tokens are cached.
        """
        try:
            end = 0
            prev_end = 0

            if pin:
                assert request_id is not None, "request_id is required when pin is True"

            # secondary lookup on p2p (via lookup_server) if enabled
            search_p2p = self.enable_p2p and (
                search_range is None or "p2p" in search_range
            )

            for start, end, key in self.token_database.process_tokens(tokens=tokens):
                assert isinstance(key, CacheEngineKey)

                if self.use_layerwise:
                    # TODO(Jiayi): Optimize by checking only the existence of the key
                    # of one layer
                    key_all_layers = key.split_layers(self.num_layers)

                    found = False
                    for key_single_layer in key_all_layers:
                        if self.storage_manager.contains(
                            key_single_layer, search_range, pin
                        ):
                            found = True
                        if search_p2p:
                            assert self.lookup_server is not None
                            if self.lookup_server.lookup(key_single_layer):
                                found = True
                    if found:
                        if pin:
                            self.lookup_pins[request_id].extend(key_all_layers)
                        prev_end = end
                        continue
                    return prev_end
                else:
                    if self.storage_manager.contains(key, search_range, pin):
                        if pin:
                            self.lookup_pins[request_id].append(key)
                        prev_end = end
                        continue

                    if search_p2p:
                        assert self.lookup_server is not None
                        # TODO(Jiayi): We need to support pin for remote lookup
                        if self.lookup_server.lookup(key):
                            prev_end = end
                            continue
                    return prev_end

            # all tokens where found, return the maximal end
            return end
        finally:
            # vllm lookup sets pin to True
            if pin:
                self.storage_manager.touch_cache()

    @_lmcache_nvtx_annotate
    def move(
        self,
        tokens: Union[torch.Tensor, List[int]],
        old_position: str,
        new_position: tuple[str, str],
        event_id: str,
        do_copy: bool = True,
    ) -> int:
        """
        Perform cross-node move of the KV cache.
        """

        num_tokens = self.lookup(
            tokens,
            search_range=old_position,
            request_id=event_id,
            pin=True,
        )

        if not num_tokens:
            logger.debug("Move is not performed as there are no tokens to move.")
            return 0

        keys = self.lookup_pins[event_id]

        memory_objs = self.storage_manager.batched_get(
            keys=keys,
            location=old_position,
        )
        logger.debug(
            f"Trying to send {len(memory_objs)} memory objects to {new_position}"
        )

        future = asyncio.run_coroutine_threadsafe(
            self.distributed_server.batched_issue_put(
                keys, memory_objs, new_position[0], new_position[1]
            ),
            self.distributed_loop,
        )

        future.add_done_callback(lambda f: [m.unpin() for m in memory_objs])

        if not do_copy:
            remove_callback = lambda f: self.storage_manager.batched_remove(
                keys, locations=[old_position]
            )
            future.add_done_callback(remove_callback)

        future.result()

        logger.debug(f"Moving {num_tokens} token from {old_position} to {new_position}")
        return num_tokens

    # TODO(Jiayi): Need to handle the case where `tokens=None`.
    # In this case, we compress all tokens.
    # TODO(Jiayi): support other compression methods.
    # TODO(Jiayi): support decompression.
    # TODO(Jiayi): support loading with automatic decompression with
    # sth like `mem_obj.post_process()`
    @_lmcache_nvtx_annotate
    def compress(
        self,
        tokens: Union[torch.Tensor, List[int]],
        method: str,
        location: str,
        event_id: str,
    ) -> int:
        if method not in ["cachegen"]:
            logger.warning(f"Unsupported compression method: {method}.")
            return 0

        # First Party
        from lmcache.v1.storage_backend.naive_serde import CreateSerde

        serializer, _ = CreateSerde(method, self.metadata, self.config)

        num_tokens = self.lookup(
            tokens,
            search_range=[location],
            request_id=event_id,
            pin=True,
        )

        if not num_tokens:
            logger.debug("Move is not performed as there are no tokens to move.")
            return 0

        keys = self.lookup_pins[event_id]

        memory_objs = self.storage_manager.batched_get(
            keys=keys,
            location=location,
        )

        compressed_memory_objs = []
        for memory_obj in memory_objs:
            compressed_memory_obj = serializer.serialize(memory_obj)
            memory_obj.unpin()
            compressed_memory_objs.append(compressed_memory_obj)
        self.storage_manager.batched_put(
            keys=keys,
            memory_objs=compressed_memory_objs,
            location=location,
        )

        self.storage_manager.batched_remove(memory_objs, locations=[location])

        return num_tokens

    @_lmcache_nvtx_annotate
    def lookup_unpin(self, request_ids: list[str]) -> None:
        for request_id in request_ids:
            if request_id in self.lookup_pins:
                self.storage_manager.batched_unpin(self.lookup_pins[request_id])
                del self.lookup_pins[request_id]

    @_lmcache_nvtx_annotate
    def clear(
        self,
        tokens: Optional[Union[torch.Tensor, List[int]]] = None,
        locations: Optional[List[str]] = None,
    ) -> int:
        assert isinstance(self.storage_manager, StorageManager)
        # Clear all caches if tokens is None
        if tokens is None or len(tokens) == 0:
            num_cleared = self.storage_manager.clear(locations)
            return num_cleared

        num_removed = 0
        # Only remove the caches for the given tokens
        for start, end, key in self.token_database.process_tokens(tokens=tokens):
            assert isinstance(key, CacheEngineKey)
            removed = self.storage_manager.remove(key, locations)
            num_removed += removed
        return num_removed

    def close(self) -> None:
        """Close the cache engine and free all the resources"""

        if self.enable_p2p:
            self.distributed_server.close()

        if self.lmcache_worker is not None:
            self.lmcache_worker.close()

        self.storage_manager.close()

        self.memory_allocator.close()

        logger.info("LMCacheEngine closed.")


class LMCacheEngineBuilder:
    _instances: Dict[str, LMCacheEngine] = {}
    _cfgs: Dict[str, LMCacheEngineConfig] = {}
    _metadatas: Dict[str, LMCacheEngineMetadata] = {}
    _stat_loggers: Dict[str, LMCacheStatsLogger] = {}

    @staticmethod
    def _Create_memory_allocator(
        config: LMCacheEngineConfig,
        metadata: LMCacheEngineMetadata,
    ) -> MemoryAllocatorInterface:
        if config.enable_nixl:
            assert config.nixl_buffer_device is not None
            # TODO (Jiayi): make this less hacky
            if config.enable_xpyd:
                # First Party
                from lmcache.v1.storage_backend.connector.nixl_utils import (
                    get_correct_nixl_device,
                )

                corrected_device = get_correct_nixl_device(
                    config.nixl_buffer_device,
                    metadata.worker_id,
                )
                logger.info(f"Setting cuda device to {corrected_device} ")
                torch.cuda.set_device(corrected_device)
                buffer = torch.empty(
                    config.nixl_buffer_size,
                    dtype=torch.uint8,
                    device=corrected_device,
                )
                nixl_cpu_mem_allocator = NixlCPUMemoryAllocator()
                nixl_cpu_mem_allocator.init_nixl_memory_allocator(
                    buffer,
                    torch.Size(metadata.kv_shape),
                    metadata.kv_dtype,
                    MemoryFormat.KV_2LTD,  # TODO: remove this hardcode
                )
                if config.local_cpu:
                    max_local_cpu_size = config.max_local_cpu_size
                    nixl_cpu_mem_allocator.init_cpu_memory_allocator(
                        int(max_local_cpu_size * 1024**3)
                    )
                return nixl_cpu_mem_allocator
            return AdHocMemoryAllocator(config.nixl_buffer_device)

        if config.weka_path is not None or config.gds_path is not None:
            assert config.cufile_buffer_size is not None
            return CuFileMemoryAllocator(config.cufile_buffer_size * 1024**2)

        max_local_cpu_size = config.max_local_cpu_size
        return MixedMemoryAllocator(int(max_local_cpu_size * 1024**3))

    @staticmethod
    def _Create_token_database(
        config: LMCacheEngineConfig,
        metadata: LMCacheEngineMetadata,
    ) -> TokenDatabase:
        if config.enable_blending:
            return SegmentTokenDatabase(config, metadata)
        return ChunkedTokenDatabase(config, metadata)

    @classmethod
    def get_or_create(
        cls,
        instance_id: str,
        config: LMCacheEngineConfig,
        metadata: LMCacheEngineMetadata,
        gpu_connector: GPUConnectorInterface,
    ) -> LMCacheEngine:
        """
        Builds a new LMCacheEngine instance if it doesn't already exist for the
        given ID.

        raises: ValueError if the instance already exists with a different
            configuration.
        """
        logger.info(f"Creating LMCacheEngine instance {instance_id}")
        if instance_id not in cls._instances:
            memory_allocator = cls._Create_memory_allocator(config, metadata)
            token_database = cls._Create_token_database(config, metadata)
            stat_logger = LMCacheStatsLogger(metadata, log_interval=10)

            engine = LMCacheEngine(
                config,
                metadata,
                memory_allocator,
                token_database,
                gpu_connector,
            )

            cls._instances[instance_id] = engine
            cls._cfgs[instance_id] = config
            cls._metadatas[instance_id] = metadata
            cls._stat_loggers[instance_id] = stat_logger
            return engine
        else:
            if (
                cls._cfgs[instance_id] != config
                or cls._metadatas[instance_id] != metadata
            ):
                raise ValueError(
                    f"Instance {instance_id} already exists with a different "
                    f"configuration or metadata."
                )
            return cls._instances[instance_id]

    @classmethod
    def get(cls, instance_id: str) -> Optional[LMCacheEngine]:
        """Returns the LMCacheEngine instance associated with the instance ID,
        or None if not found."""
        return cls._instances.get(instance_id)

    @classmethod
    def destroy(cls, instance_id: str) -> None:
        """Close and delete the LMCacheEngine instance by the instance ID"""
        # TODO: unit test for this
        if instance_id in cls._instances:
            stat_logger = cls._stat_loggers[instance_id]
            stat_logger.shutdown()
            engine = cls._instances[instance_id]
            engine.close()
            cls._instances.pop(instance_id, None)
            cls._cfgs.pop(instance_id, None)
            cls._metadatas.pop(instance_id, None)
            cls._stat_loggers.pop(instance_id, None)
            LMCStatsMonitor.DestroyInstance()
