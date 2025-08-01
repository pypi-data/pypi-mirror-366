from eventcounter import EventCounter
from random import randint

counter: EventCounter = EventCounter("Numbers")

for _ in range(100):
    if randint(1, 10) % 2 == 0:
        counter.log("even number")
    else:
        counter.log("odd number")

counter.print()
