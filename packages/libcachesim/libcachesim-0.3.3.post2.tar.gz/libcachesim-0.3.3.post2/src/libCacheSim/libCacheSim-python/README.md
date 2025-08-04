# libCacheSim Python Binding

[![Python Release](https://github.com/1a1a11a/libCacheSim/actions/workflows/pypi-release.yml/badge.svg)](https://github.com/1a1a11a/libCacheSim/actions/workflows/pypi-release.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/libcachesim.svg?logo=python&logoColor=white)](https://pypi.org/project/libcachesim)
[![PyPI Version](https://img.shields.io/pypi/v/libcachesim.svg?)](https://pypi.org/project/libcachesim)
[![PyPI - Downloads](https://img.shields.io/pypi/dd/libcachesim)](https://pypistats.org/packages/libcachesim)

Python bindings for libCacheSim, a high-performance cache simulator and analysis library.

## Installation

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/libcachesim).

```bash
pip install libcachesim
```

### Installation from sources

If there are no wheels suitable for your environment, consider building from source.

```bash
git clone https://github.com/1a1a11a/libCacheSim.git
cd libCacheSim

# Build the main libCacheSim library first
cmake -G Ninja -B build
ninja -C build

# Install Python binding
cd libCacheSim-python
pip install -e .
```

### Testing
```bash
# Run all tests
python -m pytest .

# Test import
python -c "import libcachesim; print('Success!')"
```

## Quick Start

### Basic Usage

```python
import libcachesim as lcs

# Create a cache
cache = lcs.LRU(cache_size=1024*1024)  # 1MB cache

# Process requests
req = lcs.Request()
req.obj_id = 1
req.obj_size = 100

print(cache.get(req))  # False (first access)
print(cache.get(req))  # True (second access)
```

### Trace Processing

To simulate with traces, we need to read the request of traces correctly. `open_trace` is an unified interface for trace reading, which accepet three parameters:

- `trace_path`: trace path, can be relative or absolutive path.
- `type` (optional): if not given, we will automatically infer the type of trace according to the suffix of the trace file.
- `params` (optional): if not given, default params are applied.

```python
import libcachesim as lcs

# Open trace and process efficiently
reader = lcs.open_trace(
    trace_path = "./data/cloudPhysicsIO.oracleGeneral.bin",
    type = lcs.TraceType.ORACLE_GENERAL_TRACE,
    params = lcs.ReaderInitParam(ignore_obj_size=True)
)
cache = lcs.S3FIFO(cache_size=1024*1024)

# Process entire trace efficiently (C++ backend)
obj_miss_ratio, byte_miss_ratio = cache.process_trace(reader)
print(f"Object miss ratio: {obj_miss_ratio:.4f}, Byte miss ratio: {byte_miss_ratio:.4f}")

cache = lcs.S3FIFO(cache_size=1024*1024)
# Process with limits and time ranges
obj_miss_ratio, byte_miss_ratio = cache.process_trace(
    reader,
    start_req=0,
    max_req=1000
)
print(f"Object miss ratio: {obj_miss_ratio:.4f}, Byte miss ratio: {byte_miss_ratio:.4f}")
```

## Custom Cache Policies

Implement custom cache replacement algorithms using pure Python functions - **no C/C++ compilation required**.

### Python Hook Cache Overview

The `PythonHookCachePolicy` allows you to define custom caching behavior through Python callback functions. This is perfect for:
- Prototyping new cache algorithms
- Educational purposes and learning
- Research and experimentation
- Custom business logic implementation

### Hook Functions

You need to implement these callback functions:

- **`init_hook(cache_size: int) -> Any`**: Initialize your data structure
- **`hit_hook(data: Any, obj_id: int, obj_size: int) -> None`**: Handle cache hits
- **`miss_hook(data: Any, obj_id: int, obj_size: int) -> None`**: Handle cache misses
- **`eviction_hook(data: Any, obj_id: int, obj_size: int) -> int`**: Return object ID to evict
- **`remove_hook(data: Any, obj_id: int) -> None`**: Clean up when object removed
- **`free_hook(data: Any) -> None`**: [Optional] Final cleanup

### Example: Custom LRU Implementation

```python
import libcachesim as lcs
from collections import OrderedDict

# Create a Python hook-based cache
cache = lcs.PythonHookCachePolicy(cache_size=1024*1024, cache_name="MyLRU")

# Define LRU policy hooks
def init_hook(cache_size):
    return OrderedDict()  # Track access order

def hit_hook(lru_dict, obj_id, obj_size):
    lru_dict.move_to_end(obj_id)  # Move to most recent

def miss_hook(lru_dict, obj_id, obj_size):
    lru_dict[obj_id] = True  # Add to end

def eviction_hook(lru_dict, obj_id, obj_size):
    return next(iter(lru_dict))  # Return least recent

def remove_hook(lru_dict, obj_id):
    lru_dict.pop(obj_id, None)

# Set the hooks
cache.set_hooks(init_hook, hit_hook, miss_hook, eviction_hook, remove_hook)

# Use it like any other cache
req = lcs.Request()
req.obj_id = 1
req.obj_size = 100
hit = cache.get(req)
print(f"Cache hit: {hit}")  # Should be False (miss)
```

### Example: Custom FIFO Implementation

```python
import libcachesim as lcs
from collections import deque
from contextlib import suppress

cache = lcs.PythonHookCachePolicy(cache_size=1024, cache_name="CustomFIFO")

def init_hook(cache_size):
    return deque()  # Use deque for FIFO order

def hit_hook(fifo_queue, obj_id, obj_size):
    pass  # FIFO doesn't reorder on hit

def miss_hook(fifo_queue, obj_id, obj_size):
    fifo_queue.append(obj_id)  # Add to end of queue

def eviction_hook(fifo_queue, obj_id, obj_size):
    return fifo_queue[0]  # Return first item (oldest)

def remove_hook(fifo_queue, obj_id):
    with suppress(ValueError):
        fifo_queue.remove(obj_id)

# Set the hooks and test
cache.set_hooks(init_hook, hit_hook, miss_hook, eviction_hook, remove_hook)

req = lcs.Request(obj_id=1, obj_size=100)
hit = cache.get(req)
print(f"Cache hit: {hit}")  # Should be False (miss)
```

## Available Algorithms

### Built-in Cache Algorithms

#### Basic Algorithms
- **FIFO**: First-In-First-Out
- **LRU**: Least Recently Used
- **LFU**: Least Frequently Used
- **LFUDA**: LFU with Dynamic Aging
- **Clock**: Clock/Second-chance algorithm

#### Advanced Algorithms
- **QDLP**: Queue Demotion with Lazy Promotion
- **S3FIFO**: Simple, Fast, Fair FIFO (recommended for most workloads)
- **Sieve**: High-performance eviction algorithm
- **ARC**: Adaptive Replacement Cache
- **TwoQ**: Two-Queue algorithm
- **SLRU**: Segmented LRU
- **TinyLFU**: TinyLFU with window
- **WTinyLFU**: Windowed TinyLFU

#### Research/ML Algorithms
- **LeCaR**: Learning Cache Replacement (adaptive)
- **Cacheus**: Cache replacement policy
- **LRB**: Learning-based cache (if enabled)
- **GLCache**: Machine learning-based cache
- **ThreeLCache**: Three-level cache hierarchy (if enabled)

#### Optimal Algorithms (for analysis)
- **Belady**: Optimal offline algorithm
- **BeladySize**: Size-aware optimal algorithm

```python
import libcachesim as lcs

# All algorithms use the same unified interface
cache_size = 1024 * 1024  # 1MB

lru_cache = lcs.LRU(cache_size)
s3fifo_cache = lcs.S3FIFO(cache_size)
sieve_cache = lcs.Sieve(cache_size)
arc_cache = lcs.ARC(cache_size)

# All caches work identically
req = lcs.Request()
req.obj_id = 1
req.obj_size = 100
hit = lru_cache.get(req)
print(hit)
```

## Examples and Testing

### Algorithm Comparison
```python
import libcachesim as lcs

def compare_algorithms(trace_path):
    reader = lcs.open_trace(trace_path, lcs.TraceType.VSCSI_TRACE)
    algorithms = ['LRU', 'S3FIFO', 'Sieve', 'ARC']
    for algo_name in algorithms:
        cache = getattr(lcs, algo_name)(cache_size=1024*1024)
        obj_miss_ratio, byte_miss_ratio = cache.process_trace(reader)
        print(f"{algo_name}\t\tObj: {obj_miss_ratio:.4f}, Byte: {byte_miss_ratio:.4f}")

compare_algorithms("./data/cloudPhysicsIO.vscsi")
```

### Performance Benchmarking
```python
import time

def benchmark_cache(cache, num_requests=100000):
    """Benchmark cache performance"""
    start_time = time.time()
    for i in range(num_requests):
        req = lcs.Request()
        req.obj_id = i % 1000  # Working set of 1000 objects
        req.obj_size = 100
        cache.get(req)
    end_time = time.time()
    throughput = num_requests / (end_time - start_time)
    print(f"Processed {num_requests} requests in {end_time - start_time:.2f}s")
    print(f"Throughput: {throughput:.0f} requests/sec")

# Compare performance
lru_cache = lcs.LRU(cache_size=1024*1024)
s3fifo_cache = lcs.S3FIFO(cache_size=1024*1024)

print("LRU Performance:")
benchmark_cache(lru_cache)

print("\nS3FIFO Performance:")
benchmark_cache(s3fifo_cache)
```

## Advanced Usage

### Multi-Format Trace Processing

```python
import libcachesim as lcs

# Supported trace types
trace_types = {
    "oracle": lcs.TraceType.ORACLE_GENERAL_TRACE,
    "csv": lcs.TraceType.CSV_TRACE,
    "vscsi": lcs.TraceType.VSCSI_TRACE,
    "txt": lcs.TraceType.PLAIN_TXT_TRACE
}

# Open different trace formats
oracle_reader = lcs.open_trace("./data/cloudPhysicsIO.oracleGeneral.bin", trace_types["oracle"])
csv_reader = lcs.open_trace("./data/cloudPhysicsIO.txt", trace_types["txt"])

# Process traces with different caches
caches = [
    lcs.LRU(cache_size=1024*1024),
    lcs.S3FIFO(cache_size=1024*1024),
    lcs.Sieve(cache_size=1024*1024)
]

for i, cache in enumerate(caches):
    miss_ratio_oracle = cache.process_trace(oracle_reader)[0]
    miss_ratio_csv = cache.process_trace(csv_reader)[0]
    print(f"Cache {i} miss ratio: {miss_ratio_oracle:.4f}, {miss_ratio_csv:.4f}")
```

## Troubleshooting

### Common Issues

**Import Error**: Make sure libCacheSim C++ library is built first:
```bash
cmake -G Ninja -B build && ninja -C build
```

**Performance Issues**: Use `process_trace()` for large workloads instead of individual `get()` calls for better performance.

**Memory Usage**: Monitor cache statistics (`cache.occupied_byte`) and ensure proper cache size limits for your system.

**Custom Cache Issues**: Validate your custom implementation against built-in algorithms using the test functions above.

**Install with uv**: Since automatically building with `uv` will fail due to incomplete source code, please force install the binary file via `uv pip install libcachesim --only-binary=:all:`.

### Getting Help

- Check the [main documentation](../doc/) for detailed guides
- Open issues on [GitHub](https://github.com/1a1a11a/libCacheSim/issues)
- Review [examples](/example) in the main repository
