# 存储注解方法的集合
from threading import Lock

# 使用方式必须是 static_global.static_dir_lock


#   类属性 vs 实例属性
# 类属性：定义在类中但不在任何方法内的变量，属于类本身，所有实例共享同一个值。
# running_values.server_host =>http://10.114.101.124:8000

# 实例属性：定义在 __init__ 方法或其他实例方法内的变量，每个实例都有自己独立的副本
# from running_values import server_host
# server_host  => 0.0.0.0


static_anno_func = list()

static_map = {}
static_list = []

static_dir_lock = Lock()

static_root_dir = None
