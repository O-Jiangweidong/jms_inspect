import os

from .base import BaseTask, TaskType, TError


__all__ = ['JmsServiceTask']


class JmsServiceTask(BaseTask):
    NAME = '堡垒机服务检查'
    TYPE = TaskType.JUMPSERVER
    PRIORITY = 9000

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_do_params():
        return ['jms_config']

    def _task_get_replay_path_info(self):
        volume_dir = self.jms_config.get('VOLUME_DIR', '/')
        replay_path = os.path.join(volume_dir, 'core', 'data', 'media', 'replay')
        # 总大小
        command = "df -h . --output=size| awk '{if (NR > 1) {print $1}}'"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['replay_total'] = TError
        else:
            self.task_result['replay_total'] = resp
        # 已经使用
        command = 'cd %s;du -sh' % replay_path
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['replay_used'] = TError
        else:
            self.task_result['replay_used'] = resp
        # 未使用
        command = "df -h . --output=avail| awk '{if (NR > 1) {print $1}}'"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['replay_unused'] = TError
        else:
            self.task_result['replay_unused'] = resp
        # 录像路径
        self.task_result['replay_path'] = replay_path

    def _task_get_component_log_size(self):
        volume_dir = self.jms_config.get('VOLUME_DIR', '/')
        # 获取Web日志大小
        web_log = os.path.join(volume_dir, 'nginx', 'data', 'logs')
        command = 'cd %s;du -sh' % web_log
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['web_log_size'] = TError
        else:
            self.task_result['web_log_size'] = resp
        # 获取Core日志大小
        core_log = os.path.join(volume_dir, 'core', 'logs')
        command = 'cd %s;du -sh' % core_log
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['core_log_size'] = TError
        else:
            self.task_result['core_log_size'] = resp
        # 获取Koko日志大小
        koko_path = os.path.join(volume_dir, 'koko', 'data', 'logs')
        command = 'cd %s;du -sh' % koko_path
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['koko_log_size'] = TError
        else:
            self.task_result['koko_log_size'] = resp
        # 获取Lion日志大小
        lion_path = os.path.join(volume_dir, 'lion', 'data', 'logs')
        command = 'cd %s;du -sh' % lion_path
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['lion_log_size'] = TError
        else:
            self.task_result['lion_log_size'] = resp

    def _task_get_jms_service_status(self):
        sep = '***'
        command = 'docker ps --format "table {{.Names}}%s{{.Status}}%s{{.Ports}}"' % (sep, sep)
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['component_info'] = [{
                'service_name': TError, 'service_status': TError,
                'service_port': TError
            }]
        else:
            component_info = []
            resp_list = [i.strip() for i in resp.split('\n') if i]
            body = resp_list[2:]
            for obj in body:
                obj_list = obj.split(sep)
                sorted_port = sorted(obj_list[2].replace(' ', '').split(','))
                obj_list[2] = '\n'.join(sorted_port)

                obj_item = {
                    'service_name': obj_list[0], 'service_status': obj_list[1],
                    'service_port': obj_list[2]
                }
                component_info.append(obj_item)
            self.task_result['component_info'] = component_info
