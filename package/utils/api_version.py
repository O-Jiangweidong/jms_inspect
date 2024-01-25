import functools
import os
import traceback


VERSION_FUNC_MAPPING = {}


def _get_function_name(func):
    filename, _lineno, _name, line = traceback.extract_stack()[-4]
    module, _file_extension = os.path.splitext(filename)
    module = module.replace("/", ".")
    if module.endswith(func.__module__):
        return "%s.[%s].%s" % (func.__module__, line, func.__name__)
    else:
        return "%s.%s" % (func.__module__, func.__name__)


def _get_func_by_name(name, api_version):
    return VERSION_FUNC_MAPPING['%s_%s' % (name, api_version)]


def wraps(version):
    def decor(func):
        name = _get_function_name(func)
        VERSION_FUNC_MAPPING['%s_%s' % (name, version)] = func

        @functools.wraps(func)
        def substitution(obj, *args, **kwargs):
            method = _get_func_by_name(name, obj.api_version)
            return method(obj, *args, **kwargs)

        return substitution
    return decor
