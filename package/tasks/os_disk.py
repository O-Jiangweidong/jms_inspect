from .base import BaseTask, TaskType


__all__ = ['OSDiskTask']


class OSDiskTask(BaseTask):
    NAME = '机器当前磁盘信息'
    TYPE = TaskType.GENERATOR

    def __init__(self):
        super().__init__()

    def _get_free_disk(self):
        command = 'df -h'
        resp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            resp_list = resp.split('\n')
            # 处理表头 mounted on 切割问题
            table_header = [i.strip() for i in resp_list[0].split()]
            last_ = table_header.pop()
            need_merge = '%s %s' % (table_header.pop(), last_)
            table_header.append(need_merge)
            table = [table_header]
            for r in resp_list[1:]:
                if not r:
                    continue
                r_list = [i.strip() for i in r.split(None, len(table_header)-1)]
                file_system = r_list[0]
                if file_system in ['overlay', 'tmpfs', 'devtmpfs']:
                    continue
                table.append(r_list)
            self.task_result.append((table, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_free_disk()
        return self.task_result
