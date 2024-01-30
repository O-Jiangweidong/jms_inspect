import abc
import time

import paramiko

from package.utils.log import logger
from package.utils.tools import get_ssh_client
from .. import const


class TaskType(object):
    GENERATOR = 'GENERATOR'
    JUMPSERVER = 'JUMPSERVER'
    VIRTUAL = 'VIRTUAL'
    MYSQL = 'MYSQL'
    REDIS = 'REDIS'
    OTHER = 'OTHER'


class TaskResponse(object):
    pass


class TaskResponseEmpty(TaskResponse):
    def __str__(self):
        return '空'


class BaseTask(object, metaclass=abc.ABCMeta):
    NAME = None
    TYPE = None
    PRIORITY = 0  # 数值越大，优先级越高，任务越早执行

    class Meta:
        abstract = True

    def __init__(self):
        self._ssh_client = None
        self.jms_config = None
        self.script_config = None
        self.task_result = {}
        self.abnormal_result = []

    def __str__(self):
        return self.NAME

    def register(self, task_executor):
        self._ssh_client = task_executor.get_ssh_client()

    def do_command(self, command):
        ok = True
        _, stdout, stderr = self._ssh_client.exec_command(command)
        resp = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error:
            ok = False
            resp = '获取命令[%s]，获取数据失败' % command
        return resp, ok

    @staticmethod
    def get_do_params():
        return []

    def set_do_params(self, param_name, param_value):
        setattr(self, param_name, param_value)

    def set_abnormal_event(self, e_desc, e_level):
        level_mapping = {
            const.CRITICAL: '严重', const.NORMAL: '一般', const.SLIGHT: '轻微'
        }
        level_display = level_mapping.get(e_level, '未知')
        self.abnormal_result.append({
            'level': e_level, 'desc': e_desc, 'level_display': level_display
        })

    def do(self):
        """
        任务钩子函数，会获取指定前缀的任务自动执行
        :return: task_result
        """
        for f in dir(self):
            f_func = getattr(self, f)
            if f.startswith('_task') and callable(f_func):
                try:
                    f_func()
                except Exception as e:
                    logger.warning(e)
                    raise e
        return self.task_result, self.abnormal_result


class TaskExecutor(object):
    def __init__(
            self, ssh_ip=None, ssh_port=None, ssh_username=None, ssh_password=None, **kwargs
    ):
        self._task_list = []
        self._ssh_ip = ssh_ip
        self._ssh_port = ssh_port
        self._ssh_username = ssh_username
        self._ssh_password = ssh_password
        self._ssh_client = None
        self._abnormal_task = {}
        self.kwargs = kwargs

        self.get_ssh_client()

    def __str__(self):
        return '机器 [%s] 任务执行器' % self._ssh_ip

    def add_tasks(self, tasks):
        for task in tasks:
            if not isinstance(task, BaseTask):
                raise ValueError('任务实例不匹配，请检查代码')
            self._task_list.append(task)

    def get_ssh_client(self):
        if self._ssh_client is None and \
                all((self._ssh_ip, self._ssh_port, self._ssh_username, self._ssh_password)):
            self._ssh_client = get_ssh_client(self._ssh_ip, self._ssh_port, self._ssh_username, self._ssh_password, 10)
        return self._ssh_client

    def task_end(self):
        try:
            if self._ssh_client:
                self._ssh_password.close()
        except: # noqa
            pass

    def execute(self):
        """
        任务执行入口函数
        :return:
        """
        task_result = {}
        task_abnormal_result = []
        self._task_list.sort(key=lambda x: getattr(x, 'PRIORITY', 0), reverse=True)
        machine_name = self.kwargs.get('name', '未知')
        logger.info('> 开始执行机器名为[%s]的任务, 共%s个' % (machine_name, len(self._task_list)))
        for task in self._task_list:
            start = time.time()
            logger.info('> 开始执行任务: %s' % str(task))
            if task.TYPE != TaskType.VIRTUAL:
                task.register(self)
            try:
                result, abnormal_result = task.do()
            except Exception as err:
                err_msg = '%s 执行任务 %s 出错, 错误: %s' % (self, task, err)
                logger.error(err_msg)
                raise err
            logger.info('> 执行结束(耗时: %.2f秒)' % (time.time() - start))
            task_result.update(result)
            task_abnormal_result.extend(abnormal_result)
        self.task_end()
        return task_result, task_abnormal_result


TError = TaskResponseEmpty()
