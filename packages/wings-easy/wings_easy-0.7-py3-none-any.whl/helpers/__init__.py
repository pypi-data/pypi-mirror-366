import os

from helpers import static_global

if static_global.static_root_dir is None:
    static_global.static_root_dir = os.getcwd()
    print(f"------ static_global.global_root_dir = {static_global.static_root_dir}")
