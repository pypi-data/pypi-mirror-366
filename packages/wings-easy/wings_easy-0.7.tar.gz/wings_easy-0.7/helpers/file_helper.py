import csv
import importlib.util
import json
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Union, List, Optional


def file_write(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding=encoding) as log_file:
        log_file.write(content)
    print(f"write_file->【{content}】")


def file_to_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> dict:
    """
    读取JSON文件内容

    Args:
        file_path: JSON文件路径
        encoding: 文件编码，默认utf-8

    Returns:
        解析后的JSON对象

    Raises:
        FileNotFoundError: 文件不存在时抛出
        json.JSONDecodeError: JSON解析失败时抛出
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"读取JSON文件失败: {file_path}, 错误: {str(e)}")
        raise


def file_to_cvs(file_path: Union[str, Path], encoding: str = 'utf-8') -> List[dict]:
    """
    读取CSV文件内容

    Args:
        file_path: CSV文件路径
        encoding: 文件编码，默认utf-8

    Returns:
        CSV数据列表，每行数据转换为字典

    Raises:
        FileNotFoundError: 文件不存在时抛出
        csv.Error: CSV解析失败时抛出
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logging.error(f"读取CSV文件失败: {file_path}, 错误: {str(e)}")
        raise


def file_from_cvs(file_path: Union[str, Path], data: List[dict], encoding: str = 'utf-8') -> None:
    """
    将数据写入CSV文件

    Args:
        file_path: CSV文件路径
        data: 要写入的数据列表，每个元素为一个字典
        encoding: 文件编码，默认utf-8

    Raises:
        IOError: 写入文件失败时抛出
    """
    if not data:
        return

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        logging.error(f"写入CSV文件失败: {file_path}, 错误: {str(e)}")
        raise


def create_directory(directory_path: Union[str, Path]) -> None:
    """
    创建目录，如果目录已存在则忽略

    Args:
        directory_path: 目录路径

    Raises:
        OSError: 创建目录失败时抛出
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        logging.error(f"创建目录失败: {directory_path}, 错误: {str(e)}")
        raise


def remove_directory(directory_path: Union[str, Path]) -> None:
    """
    删除目录及其内容

    Args:
        directory_path: 目录路径

    Raises:
        OSError: 删除目录失败时抛出
    """
    try:
        shutil.rmtree(directory_path)
    except Exception as e:
        logging.error(f"删除目录失败: {directory_path}, 错误: {str(e)}")
        raise


def zip_directory(directory_path: Union[str, Path],
                  output_path: Union[str, Path],
                  base_dir: Optional[str] = None) -> None:
    """
    压缩目录为ZIP文件

    Args:
        directory_path: 要压缩的目录路径
        output_path: 输出的ZIP文件路径
        base_dir: ZIP文件中的基础目录名，默认为None

    Raises:
        OSError: 压缩失败时抛出
    """
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory_path)
                    if base_dir:
                        arcname = os.path.join(base_dir, arcname)
                    zipf.write(file_path, arcname)
    except Exception as e:
        logging.error(f"压缩目录失败: {directory_path}, 错误: {str(e)}")
        raise


def unzip_file(zip_path: Union[str, Path],
               extract_path: Union[str, Path],
               password: Optional[bytes] = None) -> None:
    """
    解压ZIP文件到指定目录

    Args:
        zip_path: ZIP文件路径
        extract_path: 解压目标目录
        password: ZIP文件密码，如果有的话

    Raises:
        zipfile.BadZipFile: ZIP文件损坏时抛出
        RuntimeError: 解压加密文件但未提供密码时抛出
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_path, pwd=password)
    except Exception as e:
        logging.error(f"解压文件失败: {zip_path}, 错误: {str(e)}")
        raise


def file_read(file: Union[str, Path], encoding: str = 'utf-8'):
    print(f"file_read->【file】")
    # 上下文管理器: with 语句使用了上下文管理器（Context Manager）机制。当进入 with 语句块时，会调用文件对象的 __enter__ 方法；当退出 with 语句块时，会调用文件对象的 __exit__ 方法。__exit__ 方法会负责关闭文件。
    # 资源管理: 使用 with 语句可以确保资源（如文件）在使用完毕后被正确释放，避免了资源泄漏的问题。
    with open(file, "r", encoding=encoding) as f:
        for line in f:
            yield line.strip()


# os.listdir:
# 只能列出指定目录下的所有文件和子目录名称。
# 返回一个列表，包含该目录下的所有文件和子目录的名称。
# 不会递归遍历子目录。

# os.walk:
# 递归地遍历指定目录及其所有子目录。
# 返回一个生成器，每次迭代返回一个三元组 (root, dirs, files)，其中 root 是当前遍历的目录路径，dirs 是该目录下的子目录列表，files 是该目录下的文件列表。
# 适用于需要递归遍历整个目录树的场景。

def file_deep_walk(directory, filter):
    """
    深度遍历dir_path目录下的所有文件，子目录也遍历
    :param dir_path:
    :param filter:
    :return:
    """
    abs_path = os.path.abspath(directory)
    print(f"walk_files: {abs_path}")
    for root, dirs, files in os.walk(abs_path):
        print(f"当前目录: {root}")
        print(f"子目录: {dirs}")
        print(f"文件: {files}")
        for file_name in files:
            if filter(file_name):
                yield os.path.join(root, file_name), file_name


def file_in_directory(directory, filter):
    """
    - 列出指定目录下的所有文件和子目录名称。
    - 不会递归遍历子目录。
    """
    abs_path = os.path.abspath(directory)
    print(f"file_in_directory->listdir: {abs_path}")
    for file_dir_name in os.listdir(abs_path):
        # file_dir_name 可能是文件可能是文件夹
        if filter(file_dir_name):
            yield os.path.join(abs_path, file_dir_name), file_dir_name


def file_parent_directory(directory):
    return os.path.dirname(os.path.abspath(directory))


def file_sub_directory(parent, sub):
    return os.path.join(parent, sub)


def current_py_directory():
    """
    获取脚本文件所在的目录路径，这个路径是静态的，与脚本文件位置相关。
    """
    # os.getcwd() 获取当前工作的目录路径，可以在程序运行时动态改变
    # os.getcwd() 用于获取当前工作的目录路径（current working directory，CWD）。当前工作目录是指当前程序运行时所在的目录路径。
    # os.path.dirname(os.path.abspath(__file__)) 获取脚本文件所在的目录路径，这个路径是静态的，与脚本文件位置相关。
    return os.path.dirname(os.path.abspath(__file__))


def current_working_directory():
    """
    获取当前工作的目录路径，可以在程序运行时动态改变
    """
    # os.getcwd() 获取当前工作的目录路径，可以在程序运行时动态改变
    # os.getcwd() 用于获取当前工作的目录路径（current working directory，CWD）。当前工作目录是指当前程序运行时所在的目录路径。
    # os.path.dirname(os.path.abspath(__file__)) 获取脚本文件所在的目录路径，这个路径是静态的，与脚本文件位置相关。
    return os.getcwd()


# 在文件 a.py 中定义了一个列表 annotated_functions，然后通过 spec.loader.exec_module 加载另一个 Python 文件 b.py，但在 b.py 中访问的 annotated_functions 列表与 a.py 中的不是同一个对象。这通常是由于命名空间隔离导致的。
# 全局变量作用域：全局变量定义在单独的py中，然后使用的地方显示导入，不同py都导入这个全局py中的全局变量
def file_load_py(file_path):
    """
    加载py文件
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"file_load_py->【{module_name}】【{file_path}】")
    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def file_load_py_from_directory(directory):
    print(f"load_py_from_directory->【{directory}】")
    """
    加载directory目录内的所有py脚本
    """
    for file, name, in file_in_directory(directory, lambda file_name: file_name.endswith(".py")):
        file_load_py(file)


def file_all_in_directory(directory: str, recursive: bool = False, include_dirs: bool = False, filter=None):
    """
    遍历目录下的所有文件

    demo:
        # 遍历文件包括子目录下的文件
        for file_path in all_files_in_dir("./test_dir", recursive=True, include_dirs=False):
            print(f"File: {file_path}")
        # 遍历文件和目录
        for path in all_files_in_dir("./test_dir", recursive=True, include_dirs=True):
            print(f"Path: {path}")

    Args:
        directory (str): 要遍历的目录路径
        recursive (bool): 是否递归遍历子目录，默认为True
        include_dirs (bool): 是否包含目录路径在返回结果中，默认为False

    Yields:
        str: 文件或目录的完整路径
    """
    try:
        print(f"listdir -> 【{directory}】")
        # 遍历目录中的所有项目
        for item in os.listdir(directory):
            # 构建完整路径
            full_path = os.path.join(directory, item)

            # 如果是目录
            if os.path.isdir(full_path):
                # 如果包含目录，就yield目录路径
                if include_dirs:
                    if filter is None:
                        yield full_path
                    elif filter(full_path):
                        yield full_path
                # 如果需要递归遍历
                if recursive:
                    # 递归遍历子目录
                    yield from file_all_in_directory(full_path, recursive, include_dirs)
            # 如果是文件，直接yield
            else:
                if filter is None:
                    yield full_path
                elif filter(full_path):
                    yield full_path
    except Exception as e:
        print(f"Error accessing {directory}: {e}")


# 可执行文件的完整路径，双击exe可执行文件可获得exe可执行文件的具体路径
def exe_path():
    """
    可执行文件的完整路径，双击exe可执行文件可获得exe可执行文件的具体路径
    """
    return sys.argv[0]


def exe_name():
    return os.path.basename(exe_path())


def file_get_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension


def get_extension(file_name):
    if "." not in file_name:
        return ""
    # str.rfind获取字符最后的位置
    return file_name[file_name.rfind(".") + 1:]


def remove_extension(file_name):
    if "." not in file_name:
        return ""
    return file_name[0:file_name.index("."):]


def file_copy(src_path: Union[str, Path],
              dst_path: Union[str, Path],
              overwrite: bool = True) -> None:
    """
    复制文件

    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
        overwrite: 是否覆盖已存在的文件

    Raises:
        FileNotFoundError: 源文件不存在时抛出
        IOError: 复制失败时抛出
    """
    try:
        if not overwrite and os.path.exists(dst_path):
            raise FileExistsError(f"目标文件已存在: {dst_path}")
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
    except Exception as e:
        logging.error(f"复制文件失败: {src_path} -> {dst_path}, 错误: {str(e)}")
        raise


def file_move(src_path: Union[str, Path],
              dst_path: Union[str, Path],
              overwrite: bool = True) -> None:
    """
    移动文件

    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
        overwrite: 是否覆盖已存在的文件

    Raises:
        FileNotFoundError: 源文件不存在时抛出
        IOError: 移动失败时抛出
    """
    try:
        if not overwrite and os.path.exists(dst_path):
            raise FileExistsError(f"目标文件已存在: {dst_path}")
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
    except Exception as e:
        logging.error(f"移动文件失败: {src_path} -> {dst_path}, 错误: {str(e)}")
        raise


if __name__ == '__main__':
    # 捕获标准输出
    print(current_py_directory())
    print(current_working_directory())
    # for file in all_files_in_dir(current_working_directory(), recursive=False):
    for file in file_all_in_directory(file_parent_directory(current_working_directory())):
        print(file)

    print("---------------------------")
    for f, n in file_deep_walk("../", lambda name: get_extension(name) == "py"):
        print(f)
        print(n)

#  打包命令
# pyinstaller --name=log_translator --onefile --windowed ui_pyqt6.py
# -F, --onefile   产生单个的可执行文件
# -n NAME, --name NAME   指定项目（产生的 spec）名字。如果省略该选项，那么第一个脚本的主文件名将作为 spec 的名字
# -w, --windowed, --noconsole   指定程序运行时不显示命令行窗口（仅对 Windows 有效）
# -i <FILE.ico>, --icon <FILE.ico>  指定icon

#  打包执行以下命令
# pyinstaller -n log_translator --hidden-import config -F -w -i tools.ico ui_pyqt6.py
# --hidden-import 设置导入要动态加载的类 因为没被引用 所以不会导入需要手动设置

# pip install PyInstaller
# pyinstaller --name=<your_exe_name> --onefile --windowed --add-data "<your_data_folder>;<your_data_folder>" <your_script_name>.py

# 上述命令中的选项说明：
# --name: 可执行文件名称。
# --onefile: 将整个项目打包为一个单独的可执行文件。
# --windowed: 隐藏控制台窗口，将打包的应用程序显示为GUI应用程序。
# --add-data: 添加项目资源，支持文件夹和文件，前面是资源路径，后面是输出路径，用分号进行分割。
# 执行上述命令后，会在项目目录下生成一个.spec文件，这个文件会告诉PyInstaller如何将项目打包成exe文件。
