from background_task import background

from time import time

t = time()


@background
def mytask():
    global t
    print('background task', time() - t)
    t = time()
