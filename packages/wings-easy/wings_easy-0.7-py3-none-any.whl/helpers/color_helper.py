# 定义颜色和样式的 ANSI 转义码
RESET = "\033[0m"  # 重置所有样式
BOLD = "\033[1m"  # 粗体/高亮
UNDERLINE = "\033[4m"  # 下划线
REVERSE = "\033[7m"  # 反显

# 前景色
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

# 背景色
BG_COLORS = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}


def str_colorful(text, color=None, bg_color=None, bold=False, underline=False, reverse=False):
    """
      打印带有指定颜色和样式的文本

      :param text: 要打印的文本
      :param color: 前景色（文本颜色），可选
      :param bg_color: 背景色，可选
      :param bold: 是否加粗，默认False
      :param underline: 是否添加下划线，默认False
      :param reverse: 是否反显，默认False
      """
    style = ""
    if bold:
        style += BOLD
    if underline:
        style += UNDERLINE
    if reverse:
        style += REVERSE
    if color and color in COLORS:
        style += COLORS[color]
    if bg_color and bg_color in BG_COLORS:
        style += BG_COLORS[bg_color]
    return f"{style}{text}{RESET}"


def str_magenta(str):
    return str_colorful(str, "magenta")


def bg_magenta(str):
    return str_colorful(str, bg_color="magenta")


def str_red(str):
    return str_colorful(str, "red")


def str_green(str):
    return str_colorful(str, "green")


def str_cyan(str):
    return str_colorful(str, "cyan")


def bg_cyan(str):
    return str_colorful(str, bg_color="cyan")


def str_blue(str):
    return str_colorful(str, "blue")


def bg_blue(str):
    return str_colorful(str, bg_color="blue")


def bg_white(str):
    return str_colorful(str, bg_color="white")


def str_yellow(str):
    return str_colorful(str, "yellow")


if __name__ == '__main__':
    # 示例：打印所有前景色
    for color in COLORS:
        print(str_colorful(f"This is {color}", color=color))

    # 示例：打印所有背景色
    for bg_color in BG_COLORS:
        print(str_colorful(f"This is with {bg_color} background", bg_color=bg_color))

    # 示例：打印带有不同样式的文本
    print(str_colorful("This is bold and underlined", color="yellow", bold=True, underline=True))
    print(str_colorful("This is reverse color text", color="cyan", reverse=True))
