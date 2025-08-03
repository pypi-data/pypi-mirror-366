import time
from . import pysick_core

def time_in(ms, func):
    pysick_core.ingine._root.after(ms, func)

def tick(ms):
    time.sleep(ms/1000)