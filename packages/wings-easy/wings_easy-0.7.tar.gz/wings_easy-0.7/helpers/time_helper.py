import threading
from datetime import datetime


def show_time():
    return datetime.now().strftime("%m-%d %H:%M:%S")


import time
from functools import wraps


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算耗时
        print(
            f"{show_time()} {threading.current_thread().ident} 函数 {func.__name__} {args} {kwargs} 执行耗时: {elapsed_time:.2f} 秒")
        return result

    return wrapper


@measure_time
def my_function():
    # 模拟一个耗时的操作
    time.sleep(2)  # 假设这个操作耗时2秒
    print("my_function 执行完毕")


# main.py
if __name__ == "__main__":
    my_function()
