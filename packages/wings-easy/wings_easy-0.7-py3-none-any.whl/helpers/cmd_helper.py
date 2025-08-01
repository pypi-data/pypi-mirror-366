import msvcrt
import os
import platform
import subprocess
import sys
import time

from helpers import static_global
from helpers.exception_helper import exception_log


# args: 要执行的命令和参数，可以是一个字符串（如果 shell=True）或一个列表。
# stdin: 用于提供子进程标准输入的文件对象、PIPE 或 None（默认为 None）。
# input: 传递给子进程 stdin 的数据，是字节序列。如果使用 input，则 stdin 必须是 PIPE。
# stdout: 子进程标准输出可以连接到的文件对象、PIPE 或 None（默认为 None）。
# stderr: 子进程标准错误输出可以连接到的文件对象、PIPE 或 None（默认为 None）。
# capture_output: 是否捕获标准输出和标准错误。如果为 True 等同于 stdout=PIPE 和 stderr=PIPE。
# shell: 如果为 True，将通过 shell 执行命令。
# cwd: 子进程的工作目录。
# timeout: 如果指定，子进程运行时间超过 timeout 秒将引发 TimeoutExpired 异常。
# check: 如果为 True，则命令返回码非零时将引发 CalledProcessError 异常。
# encoding: 如果指定，将以给定编码处理输入和输出。
# errors: 指定编码和解码错误的处理方式。
# text 或 universal_newlines: 如果为 True，输入和输出以字符串形式处理，而不是字节。
# env: 用于指定子进程的环境变量。默认为当前进程的环境变量。
# startupinfo: （仅适用于 Windows）用于传递给子进程的 STARTUPINFO。
# creationflags: （仅适用于 Windows）用于传递给子进程的 creationflags。
#
# subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, capture_output=False,
#                shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None,
#                text=None, env=None, universal_newlines=None, startupinfo=None, creationflags=0)


def directory_cmd(directory, callback, *args):
    """
    进入directory后执行cmd命令，执行完回到原始目录
    :param directory:
    :param callback: (directory, *args): 参数为 1，原始目录(进入directory之前的目录) 2 args为directory外部传递的参数
    :param args: 传递给callback的原始参数，可能在进入目录之后，callback执行的时候要使用的参数
    :return:
    """
    with static_global.static_dir_lock:
        cwd = os.getcwd()
        print(f"getcwd -> {cwd}")
        try:
            print(f"chdir -> {directory}")
            os.chdir(directory)
            callback(cwd, *args)
        finally:
            os.chdir(cwd)

#   **kwargs 和 *args 的区别及使用场景
# *args: 用于接收任意数量的位置参数，参数被收集到一个元组中。
# **kwargs: 用于接收任意数量的关键字参数，参数被收集到一个字典中。
# 使用场景:
# 当你需要接收不确定数量的位置参数时，使用 *args。
# 当你需要接收不确定数量的关键字参数时，使用 **kwargs。
# 当你需要同时接收位置参数和关键字参数时，可以同时使用 *args 和 **kwargs。
# ====================================================
#      def my_function(*args):
#          for arg in args:
#              print(arg)
#      my_function(1, 2, 3, 'a', 'b')
# =====================================================
#      def my_function(**kwargs):
#          for key, value in kwargs.items():
#              print(f"{key}: {value}")
#      my_function(name="Alice", age=30, city="New York")
# ========================================================


def adb_logcat(key):
    system = platform.system()
    if system == "Windows":
        command = f"adb logcat | findstr {key}"
    else:
        command = f"adb logcat | grep {key}"
    yield from shell_observer(command)


def shell_observer(command):
    # 使用 shell=True 来执行带有管道的命令
    # 当 shell=True 时，subprocess.Popen 会通过系统的 shell 来执行命令。
    # 在 Windows 上，默认的 shell 是 cmd.exe，而在 Unix 系统上，默认的 shell 是 /bin/sh。
    # cmd.exe 支持 findstr，但不支持 grep，因为 grep 不是 Windows 的内置命令。
    # /bin/sh 支持 grep，但不支持 findstr，因为 findstr 是 Windows 特有的命令。
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True, encoding='utf-8')
    try:
        # 逐行读取输出
        while True:
            try:
                line = process.stdout.readline()
                if line:
                    yield line.strip()
            except:
                exception_log()
    except KeyboardInterrupt:
        # 捕获 Ctrl+C 中断，终止进程
        print("Process interrupted")
    finally:
        process.terminate()


def cmd_result(command: str) -> str:
    run_result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if run_result.returncode != 0:
        raise RuntimeError(f"【{command}】failed：{run_result.returncode}")
    stdout = run_result.stdout
    print(f"【{command}】executed ok\nstdout:【{stdout}】")
    return stdout
    # return subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
    # return subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True, encoding='utf-8').stdout


def shell_result(command: str) -> str:
    run_result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True, encoding='utf-8')
    if run_result.returncode != 0:
        raise RuntimeError(f"【{command}】failed：{run_result.returncode}")
    stdout = run_result.stdout
    print(f"【{command}】executed ok\nstdout:【{stdout}】")
    return stdout
    # return subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
    # return subprocess.run(command, capture_output=True, text=True, encoding='utf-8')


def cmd_result_to_file(command: str, file: str):
    # 执行命令并捕获输出
    try:
        run_result = cmd_result(command)
        # 将输出保存到文件中
        with open(file, 'w', encoding='utf-8') as log_file:
            log_file.write(run_result)
        print(f"result saved to -> {file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e.stderr}")


def shell_result_file(command, file):
    # 执行命令并捕获输出
    try:
        run_result = shell_result(command)
        # 将输出保存到文件中
        with open(file, 'w', encoding='utf-8') as log_file:
            log_file.write(run_result)
        print(f"result saved to -> {file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e.stderr}")


def cmd(command):
    run_result = subprocess.run(command, capture_output=False)
    # 检查 commit 命令是否成功执行
    if run_result.returncode != 0:
        print(f"【{command}】failed:", run_result.stderr)
        return False
    else:
        print(f"【{command}】executed ok")
        return True


def cmd_window_pause():
    print("请按 Enter 键继续...")
    msvcrt.getch()  # 等待用户按下任意键
    print("程序结束")


def cmd_print_one_line(msg):
    sys.stdout.write(f"\r{msg}")  # 使用 \r 回到行首，覆盖之前的数字
    sys.stdout.flush()


def cmd_window_pause_countdown(seconds=5):
    print(f"Waiting for {seconds} seconds")
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{i}")  # 使用 \r 回到行首，覆盖之前的数字
        sys.stdout.flush()
        time.sleep(1)
    print("\rGo!...")  # 最后输出 "Go!"
    time.sleep(3)


if __name__ == '__main__':
    # 捕获标准输出
    result = subprocess.run("adb devices", capture_output=True, text=True)
    print(f"stdout: {result.stdout}")
    print(cmd_result("java --version"))
    print(cmd_result("adb devices"))
    print(cmd("adb devices"))
    # cmd_window_pause_countdown()
    # for log in shell_observer("adb logcat"):
    for log in adb_logcat("Health_"):
        # for log in cmd_observer("adb logcat | findStr Health_"):
        print(log)
