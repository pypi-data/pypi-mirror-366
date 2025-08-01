# TreeTimer

A hierarchical performance timer for measuring nested execution scopes in Python.  
Supports context-based timing, named sub-scopes, repeated series tracking, and structured reporting.

![PyPI](https://img.shields.io/pypi/v/tree-timer)
![Python](https://img.shields.io/badge/python-3.11+-blue)

---

## Features

- ⏱ Simple `with`-based timing API
- 🌲 Tree-style nested timing scopes
- 🔁 Support for repeated timing series (e.g. epochs, batches)
- 📦 `to_dict()` output for visualization or structured logging

---

## Installation

```bash
pip install tree-timer
```

---

## Usage

### 1. Simple use

```python
from tree_timer import TreeTimer
import time

with TreeTimer() as timer:
    time.sleep(0.1)

print(timer)
```

```
root: 0.100123s
```

---

### 2. Nested scopes with `add_scope()`

```python
with TreeTimer() as timer:
    with timer.add_scope("load_data"):
        time.sleep(0.05)
    with timer.add_scope("process_data"):
        time.sleep(0.08)

print(timer)
```

```
root: 0.130456s
  load_data: 0.050123s
  process_data: 0.080333s
```

---

### 3. Loop timing with `add_series()`

```python
with TreeTimer() as timer:
    steps = timer.add_series("steps", 3)
    for step in steps:
        with step:
            time.sleep(0.03)

print(timer)
```

```
root: 0.090876s
  steps: 0.090876s
    [0]: 0.030141s
    [1]: 0.030251s
    [2]: 0.030484s
```

---

### 4. Combined use with parallel execution

```python
from tree_timer import TreeTimer
from concurrent.futures import ThreadPoolExecutor
import time

def run_task(timer):
    with timer:
        time.sleep(0.03)

with TreeTimer() as timer:
    with timer.add_scope("pipeline") as pipeline:
        with pipeline.add_scope("load"):
            time.sleep(0.02)

        steps = pipeline.add_series("parallel_steps", 4)
        with ThreadPoolExecutor() as executor:
            executor.map(run_task, steps)

        with pipeline.add_scope("finalize"):
            time.sleep(0.01)

print(timer)
```

```
root: 0.063421s
  pipeline: 0.063421s
    load: 0.020114s
    parallel_steps: 0.120548s
      [0]: 0.030102s
      [1]: 0.030184s
      [2]: 0.030120s
      [3]: 0.030142s
    finalize: 0.010216s
```

> 💡 Tasks in `parallel_steps` run concurrently using ThreadPoolExecutor, while the surrounding `load` and `finalize` scopes are timed sequentially.

---

## License

[MIT](LICENSE)
