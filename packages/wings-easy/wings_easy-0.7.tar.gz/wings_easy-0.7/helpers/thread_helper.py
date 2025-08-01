import concurrent.futures
import threading

from helpers.color_helper import str_magenta
from helpers.time_helper import show_time

executor = concurrent.futures.ThreadPoolExecutor(max_workers=15)


def submit(fun, arg):
    # fun(arg)
    # executor.submit(run, fun, arg)
    executor.submit(fun, arg)


def run(fun, arg):
    fun(arg)


def t_log(msg):
    thread = threading.current_thread()
    thread_info = f"{thread.name}[{thread.ident}]"
    print(f"{show_time()} {str_magenta(thread_info)} {msg}")
