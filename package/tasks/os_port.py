from .base import BaseTask, TaskType


__all__ = ['OSPortTask']


class OSPortTask(BaseTask):
    NAME = '机器当前监听端口情况'
    TYPE = TaskType.GENERATOR

    def __init__(self):
        super().__init__()

    def _get_listen_port(self):
        netstat_command = "netstat -alnput|awk '{print $4, $6, $7}'"
        ss_command = "ss -alnptu| awk '{print $5, $2, $7}'"
        resp, ok = self.do_command(netstat_command)
        if not ok:
            resp, ok = self.do_command(ss_command)

        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            table = [('进程名称', '监听信息')]
            for r in resp.split('\n')[2:]:
                resp_line = r.split()
                if len(resp_line) != 3:
                    continue
                local_address, state, program_name = resp_line
                if state.upper() not in ['LISTEN']:
                    continue
                table.append((program_name.strip(), local_address.strip()))
            self.task_result.append((table, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_listen_port()
        return self.task_result
