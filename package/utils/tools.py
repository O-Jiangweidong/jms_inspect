import socket
import subprocess

import paramiko

from datetime import datetime
from importlib import import_module
from paramiko.ssh_exception import SSHException

from package import const


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


def get_ssh_client(ip, port, username, password, timeout=1):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(
            ip, port, username, password, timeout=timeout
        )
    except SSHException:
        ssh_client = None
    return ssh_client


def is_machine_connect(ip, port, username, password, timeout=1):
    ssh_client = get_ssh_client(ip, port, username, password, timeout)
    return False if ssh_client is None else True


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
    return const.YES if bool(e) else const.NO


def local_shell(commands):
    result = None
    process = subprocess.Popen(
        commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    if not error:
        try:
            result = output.decode('utf-8').strip()
        except UnicodeDecodeError:
            pass
    return result
