import socket

from datetime import datetime
from importlib import import_module


def import_string(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class' %
            (module_path, class_name)) from err


def is_machine_connect(ip, port, timeout=1):
    status = True
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(timeout)
    try:
        sk.connect((ip, port))
    except Exception: # noqa
        status = False
    return status


def get_current_timestamp():
    return datetime.now().timestamp()


def get_current_datetime_display(format_file=True):
    if format_file:
        format_string = '%Y-%m-%d-%H-%M-%S'
    else:
        format_string = '%Y-%m-%d %H:%M:%S'
    return datetime.now().strftime(format_string)


def get_current_date_display():
    return datetime.now().strftime('%Y-%m-%d')


def boolean(e):
    if isinstance(e, str):
        try:
            e = float(e)
        except ValueError:
            pass
    return '是' if bool(e) else '否'
