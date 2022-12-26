from .base import BaseTask, TaskType


__all__ = ['JmsServiceTask']


class JmsServiceTask(BaseTask):
    NAME = '堡垒机服务检查'
    TYPE = TaskType.JUMPSERVER
    PRIORITY = 9000

    def __init__(self):
        super().__init__()

    def _get_jms_service_status(self):
        sep = '***'
        command = 'docker ps --format "table {{.Names}}%s{{.Status}}%s{{.Ports}}"' % (sep, sep)
        resp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            table = []
            resp_list = [i.strip() for i in resp.split('\n') if i]
            header = ['名称', '状态', '监听端口']
            body = resp_list[2:]

            table.append(header)
            for obj in body:
                obj_list = obj.split(sep)
                port_temp = obj_list[2].replace(' ', '').split(',')
                port_temp.sort()
                obj_list[2] = '\n'.join(port_temp)
                table.append(obj_list)
            self.task_result.append((table, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_jms_service_status()
        return self.task_result
