import abc

import paramiko

from package.utils.log import logger


class TaskType(object):
    GENERATOR = 'GENERATOR'
    JUMPSERVER = 'JUMPSERVER'
    MYSQL = 'MYSQL'
    REDIS = 'REDIS'
    OTHER = 'OTHER'


class BaseTask(object, metaclass=abc.ABCMeta):
    NAME = None
    TYPE = None
    PRIORITY = 0  # 数值越大，优先级越高，任务越早执行

    class Meta:
        abstract = True

    def __init__(self):
        self._ssh_client = None
        self.abnormal_number = 0
        self.task_result = []  # [(result, is_alert)]

    def __str__(self):
        return self.NAME

    def register(self, ssh_client):
        self._ssh_client = ssh_client

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

    @abc.abstractmethod
    def do(self):
        """
        重写此方法
        执行完任务之后，要把任务结果返回
        :return: task_result
        """
        pass


class TaskExecutor(object):
    def __init__(self, ssh_ip, ssh_port, ssh_username, ssh_password, **kwargs):
        self._task_list = []
        self._ssh_client = None
        self._ssh_ip = ssh_ip
        self._ssh_port = ssh_port
        self._ssh_username = ssh_username
        self._ssh_password = ssh_password
        self._abnormal_task = {}
        self.kwargs = kwargs

    def __str__(self):
        return '机器 [%s] 任务执行器' % self._ssh_ip

    @property
    def ssh_client(self):
        if self._ssh_client is None:
            self.get_ssh_client()
        return self._ssh_client

    def add_tasks(self, tasks):
        for task in tasks:
            if not isinstance(task, BaseTask):
                raise Exception('任务实例不匹配，请检查代码')
            self._task_list.append(task)

    def get_ssh_client(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            self._ssh_ip, self._ssh_port, self._ssh_username, self._ssh_password
        )
        self._ssh_client = ssh_client

    def get_abnormal_task(self):
        return self._abnormal_task

    def set_abnormal_task(self, task, number):
        task_number = self._abnormal_task.get(task, 0)
        self._abnormal_task[task] = task_number + number

    def execute(self):
        """
        任务执行入口函数
        :return:
        """
        task_result = {}
        self._task_list.sort(key=lambda x: getattr(x, 'PRIORITY', 0), reverse=True)
        for task in self._task_list:
            task.register(self.ssh_client)
            try:
                line = '+' * 66
                logger.empty(line, br=False)
                logger.info('开始执行 -> %s' % str(task))
                resp = task.do()

                self.set_abnormal_task(task, task.abnormal_number)

                logger.info('执行结束 -> %s' % str(task))
                logger.empty(line, br=False)
            except Exception as err:
                err_msg = '%s 执行任务 %s 出错, 错误: %s' % (self, task, err)
                logger.error(err_msg)
                resp = [err_msg]
            task_result[task.NAME] = resp
        self.ssh_client.close()
        return task_result
