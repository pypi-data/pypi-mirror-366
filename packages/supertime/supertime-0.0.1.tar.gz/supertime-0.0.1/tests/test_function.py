from time import time
from asyncio import run

from supertime import supersleep


global_sleep_time = 0.001

before = time()
supersleep(global_sleep_time)
real_global_sync_sleep_time = time() - before

before = time()
run(supersleep(global_sleep_time))
real_global_async_sleep_time = time() - before


def test_simple_sync_sleep():
    sleep_time = 0.001

    before = time()
    supersleep(sleep_time)
    after = time()

    assert after - before >= sleep_time


def test_simple_async_sleep():
    sleep_time = 0.001

    before = time()
    run(supersleep(sleep_time))
    after = time()

    assert after - before >= sleep_time


def test_global_sync_sleep():
    assert real_global_sync_sleep_time >= global_sleep_time


def test_global_async_sleep():
    assert real_global_async_sleep_time >= global_sleep_time
