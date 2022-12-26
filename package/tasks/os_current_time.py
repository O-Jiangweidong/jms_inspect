from datetime import datetime

from .base import BaseTask, TaskType


__all__ = ['OSCurrentTimeTask']


class OSCurrentTimeTask(BaseTask):
    NAME = '机器当前时间信息'
    TYPE = TaskType.GENERATOR
    PRIORITY = 9999

    def __init__(self):
        super().__init__()
        self.script_config = None
        self.current_timestamp = 0

    @staticmethod
    def get_do_params():
        return ['current_timestamp', 'script_config']

    @staticmethod
    def _timestamp_to_datetime_display(timestamp):
        timestamp = int(timestamp)
        datetime_obj = datetime.fromtimestamp(timestamp)
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    def _get_current_timestamp(self):
        warning = False
        command = 'date +%s'
        timestamp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((timestamp, True))
        else:
            time_log = int(self.script_config.get('TIME_LAG', 60))
            diff = int(timestamp) - self.current_timestamp
            if abs(diff) > time_log:
                self.abnormal_number += 1
                warning = True
            if diff > 0:
                msg_tip = '比脚本时间快了 %s 秒' % int(diff)
            else:
                msg_tip = '比脚本时间慢了 %s 秒' % abs(int(diff))
            resp = self._timestamp_to_datetime_display(timestamp)
            script_time = self._timestamp_to_datetime_display(self.current_timestamp)
            self.task_result.append(('%s (脚本机器时间: %s)' % (resp, script_time), warning))
            self.task_result.append((msg_tip, warning))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_current_timestamp()
        return self.task_result
