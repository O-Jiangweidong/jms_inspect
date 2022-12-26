import os

from .base import BaseTask, TaskType


__all__ = ['JmsLogFileTask']


class JmsLogFileTask(BaseTask):
    NAME = '堡垒机日志文件大小'
    TYPE = TaskType.JUMPSERVER

    def __init__(self):
        super().__init__()
        self.jms_config = None

    @staticmethod
    def get_do_params():
        return ['jms_config']

    def _get_log_file_size(self):
        volume_dir = self.jms_config.get('VOLUME_DIR')
        log_path = os.path.join(volume_dir, 'core', 'logs')
        command = 'cd %s;du -h --max-depth=1 *' % log_path
        resp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            resp_list = resp.strip().split('\n')
            table_header = ['文件名称', '文件大小', '文件名称', '文件大小']
            table = [table_header, ]
            for idx in range(0, len(resp_list), 2):
                o1, *o2 = resp_list[idx: idx + 2]
                if not o1:
                    continue
                o1_size, o1_name = o1.split()
                if not o2:
                    body = [o1_name, o1_size]
                else:
                    o2_size, o2_name = o2[0].split()
                    body = [o1_name, o1_size, o2_name, o2_size]
                table.append(body)
            self.task_result.append((table, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_log_file_size()
        return self.task_result
