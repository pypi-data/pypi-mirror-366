import time
from functools import wraps

from helpers.color_helper import bg_blue
from helpers.thread_helper import t_log


def log_time(func):
    """
    此修饰符必须在其他修饰符的下面，应该放最底下
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        fun_info = f"{func.__name__} {args} {kwargs}"
        t_log(bg_blue(f"{'👇' * 6} {fun_info} {'👇' * 8}"))
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算耗时
        t_log(bg_blue(f"{'👆' * 6} {fun_info} cost:{elapsed_time:.2f}s {'👆' * 8}"))
        return result

    return wrapper
