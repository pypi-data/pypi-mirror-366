import bisect
import os
import re
import sys
import time
from functools import wraps

import helpers.exception_helper
from helpers import static_global
from helpers.color_helper import str_cyan, str_magenta
from helpers.file_helper import file_parent_directory, file_sub_directory, file_load_py_from_directory
from helpers.re_helper import str_to_pattern
from helpers.thread_helper import submit, t_log

log_time = False


def action_dispatch(key, arg):
    for re_fun in static_global.static_anno_func:
        # if re_fun.pattern.match(key):
        if re_fun.pattern.search(key):
            submit(re_fun.fun, arg)
            return re_fun
    t_log(str_cyan(f"--- action_dispatch -> nothing match => key:{key} = arg:{arg}"))
    return None


def action_dispatch_result(key, arg):
    for re_fun in static_global.static_anno_func:
        # if re_fun.pattern.match(key):
        if re_fun.pattern.search(key):
            return re_fun.fun(arg)
    t_log(str_cyan(f"--- action_dispatch_result -> nothing match => key:{key} = arg:{arg}"))
    return None


class ReFun:
    def __init__(self, key, pattern, desc, priority, fun):
        self.key = key
        self.fun = fun
        self.desc = desc
        self.pattern = pattern
        self.priority = priority

    def __lt__(self, other):
        if not isinstance(other, ReFun):
            return NotImplemented
        return self.priority < other.priority

    def __str__(self):
        return f"ReFun.class【{self.key}】=> {self.desc}"


# 自定义注解
def action(pattern, desc, priority=1):
    """
    当和多个修饰符一起使用的时候必须放在最上面，否则action上面的修饰符会失效
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            fun_info = f"{func.__name__}{args} =>【{pattern}】> {desc}"
            t_log(str_cyan(f"{'👇' * 6} {fun_info} {'👇' * 16}"))
            start_time = time.time()  # 记录开始时间
            result = None
            try:
                result = func(*args, **kwargs)  # 执行被装饰的函数
            except Exception as e:
                helpers.exception_helper.exception_log()
            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time  # 计算耗时
            t_log(str_cyan(f"{'👆' * 6} {fun_info} {kwargs} cost:{elapsed_time:.2f}s {'👆' * 16}"))
            return result

        re_fun = ReFun(pattern, str_to_pattern(pattern, re.IGNORECASE), desc, priority, wrapper)
        # annotated_functions.append(re_fun)
        # 使用 bisect.insort 插入元素,添加的时候就排序
        bisect.insort(static_global.static_anno_func, re_fun)
        t_log(str_magenta(
            f"register action -> {re_fun} =>{len(static_global.static_anno_func)}->{id(static_global.static_anno_func)}"))
        return wrapper

    return decorator


def scan_and_import(directory):
    """扫描目录并导入所有Python文件"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        directory = os.path.join(sys._MEIPASS, directory)
        print(f"Scanning exe directory: {directory}")
        file_load_py_from_directory(directory)
    else:
        print(f"Scanning src directory: {directory}")
        # 如果是源代码
        file_load_py_from_directory(directory)


if __name__ == "__main__":
    # 扫描当前目录下的所有Python文件
    scan_and_import(file_sub_directory(file_parent_directory("."), "test"))
    print(id(static_global.static_anno_func))
    for func in static_global.static_anno_func:
        print(f"Found annotated function: {func}")

    # for i in range(10):
    #     print(action_dispatch("3", i))
    print(action_dispatch("""
    3
    """, 33))
    # print(action_dispatch_result("test", "nihao"))
