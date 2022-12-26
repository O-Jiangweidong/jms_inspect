import re

from .base import BaseTask, TaskType


__all__ = ['OSInfoTask']


os_pattern = r'.*up (\d*).+?(\d+:\d+|\d+).+?(\d+).+?(\d+.\d*).+?(\d+.\d*).+?(\d+.\d*)'
os_pattern_obj = re.compile(os_pattern)


class OSInfoTask(BaseTask):
    NAME = '机器当前系统信息'
    TYPE = TaskType.GENERATOR

    def __init__(self):
        super().__init__()

    def _get_cpu_num(self):
        command = "grep -c 'processor' /proc/cpuinfo"
        resp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            cpu_num = resp
            self.task_result.append(('CPU 个数为: %s' % cpu_num, False))

    def _get_up_time_info(self):
        up_time_command = 'uptime'
        resp, ok = self.do_command(up_time_command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            find = os_pattern_obj.match(resp)
            if find:
                warning = False
                up_day, up_time, user, avg_1, avg_5, avg_15 = find.groups()
                if up_day:
                    up = '%s 天' % (up_day,)
                else:
                    up = '%s' % up_time
                resp_list = [
                    ('CPU在1分钟、5分钟、15分钟的平均占比分别为 %s%%、%s%%、%s%%'
                     % (avg_1, avg_5, avg_15), warning),
                    ('当前系统已经运行了 %s' % up, warning),
                    ('当前有 %s 个连接用户' % user, warning),
                ]
            else:
                item = 'uptime命令解析数据发生错误'
                self.abnormal_number += 1
                warning = True
                resp_list = [(item, warning)]
            self.task_result.extend(resp_list)

    def _get_mem_info(self):
        free_command = 'free -h|grep -i mem'
        resp, ok = self.do_command(free_command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            total, used, free, *arg, available = resp.split()[1:]
            item = '内存总大小: %s, 已经使用: %s, 物理未使用: %s, 应用程序可使用: %s'\
                   % (total, used, free, available)
            self.task_result.append((item, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        # command = 'top -b -i -n 1'
        self._get_cpu_num()
        self._get_up_time_info()
        self._get_mem_info()
        return self.task_result
