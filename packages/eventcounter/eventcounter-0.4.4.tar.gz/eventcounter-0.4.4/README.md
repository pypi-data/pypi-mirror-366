# EventCounter

`EventCounter` is a Python module to count events and print event statistics. 

## Install

```sh
pip install eventcounter
```

## Usage

Count events with `log()` and `print()` counted events.

```python
from eventcounter import EventCounter
from random import randint

counter: EventCounter = EventCounter("Numbers")

for _ in range(100):
    if randint(1, 10) % 2 == 0:
        counter.log("even number")
    else:
        counter.log("odd number")

counter.print()
```
#### Output

```bash
even number   : 53
odd number    : 47
```

# Example

Full runnable example below. It can be found in [demos/](demos/) folder. 

```python

```
