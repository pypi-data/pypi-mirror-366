import traceback


def exception_log():
    traceback.print_exc()


def exception_stack_trace_msg():
    traceback.format_exc()
