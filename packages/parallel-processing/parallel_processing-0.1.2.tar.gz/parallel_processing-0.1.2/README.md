# Parallel Processing

[![PyPI version](https://badge.fury.io/py/parallel-processing.svg)](https://pypi.org/project/parallel-processing/)

A minimal, easy-to-use Python utility to parallelize function execution using threads or processes.  
This library helps you speed up processing over iterable items by distributing work across multiple workers.

---

## Features

- Lightweight and dependency-free  
- Simple interface for threading and multiprocessing  
- Easily process a list of items with any custom function  
- Ideal for I/O-bound or CPU-bound tasks

---

## Installation

```bash
pip install parallel-processing
```

---

## Usage

You can use either **threading** or **multiprocessing** to parallelize your task over a list of items.

### Example: Using Threads

```python
from parallel_processing import ParallelProcessing

def fetch(x):
    print(f"Processing item: {x}")

workers = 10
its = 100

ParallelProcessing.thread(
    workers=workers,
    processor=fetch,
    items=range(its)
)
```

---

### Example: Using Processes

```python
from parallel_processing import ParallelProcessing

def compute(x):
    return x * x

results = ParallelProcessing.process(
    workers=4,
    processor=compute,
    items=range(10)
)

print(list(results))
```

---

## API

### `ParallelProcessing.thread(workers, processor, items)`

Runs `processor(item)` for each item in `items` using `workers` threads.

- `workers` (int): Number of threads to use  
- `processor` (callable): Function to apply to each item  
- `items` (iterable): The list or iterable of items to process

---

### `ParallelProcessing.process(workers, processor, items)`

Runs `processor(item)` for each item in `items` using `workers` processes and returns results.

- `workers` (int): Number of processes to use  
- `processor` (callable): Function to apply to each item  
- `items` (iterable): The list or iterable of items to process

---

## License

MIT License

---

## Author

**Louis Nguyen**  
[louis.nguyen@qode.world](mailto:louis.nguyen@qode.world)
