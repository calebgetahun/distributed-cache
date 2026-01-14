import time
from ..factory import CacheFactory
from ..eviction import EvictionPolicy

def benchmark_lru(
    capacity=100,
    n_ops=10_000_000,
    read_ratio=0.1,  #HIGH write ratio 
):
    print(f"--- LRU Microbenchmark ---")
    print(f"Capacity: {capacity}")
    print(f"Operations: {n_ops:,}")
    print(f"Read ratio: {read_ratio * 100:.0f}%\n")

    cache = CacheFactory.create_local_cache(capacity, EvictionPolicy.LRU)

    # Warm-up phase: fill cache to capacity
    print("Warming up cache...")
    for i in range(capacity):
        cache.put(f"key{i}", i)

    print("Starting benchmark...\n")
    start = time.perf_counter()

    for i in range(n_ops):
        key = f"key{i % capacity}"

        if (i % 100) < (read_ratio * 100):
            # GET operation
            cache.get(key)
            pass
        else:
            # SET operation
            cache.put(key, i)
            pass

    end = time.perf_counter()

    duration = end - start
    ops_per_sec = n_ops / duration

    print(f"Duration: {duration:.3f}s")
    print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
    print("\nBenchmark complete.")


if __name__ == "__main__":
    benchmark_lru()
