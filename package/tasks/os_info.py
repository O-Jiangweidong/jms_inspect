import re

from .base import BaseTask, TaskType, TError
from ..utils.tools import boolean
from .. import const


__all__ = ['OSInfoTask']


os_pattern = r'.*up (\d*).+?(\d+:\d+|\d+).+?(\d+).+?(\d+.\d*).+?(\d+.\d*).+?(\d+.\d*)'
os_pattern_obj = re.compile(os_pattern)


class OSInfoTask(BaseTask):
    NAME = '机器当前系统信息'
    TYPE = TaskType.GENERATOR

    def __init__(self):
        super().__init__()

    def _task_get_hostname(self):
        command = "hostname"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['machine_hostname'] = TError
        else:
            self.task_result['machine_hostname'] = resp

    def _task_get_language(self):
        command = "echo $LANG"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['machine_language'] = TError
        else:
            self.task_result['machine_language'] = resp

    def _task_get_all_ip(self):
        command = "hostname -I"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['machine_ip'] = TError
        else:
            self.task_result['machine_ip'] = resp

    def _task_get_os_version(self):
        command = "uname -o"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['os_version'] = TError
        else:
            self.task_result['os_version'] = resp

    def _task_get_kernel_version(self):
        command = "uname -r"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['kernel_version'] = TError
        else:
            self.task_result['kernel_version'] = resp

    def _task_get_cpu_arch(self):
        command = "uname -m"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['cpu_arch'] = TError
        else:
            self.task_result['cpu_arch'] = resp

    def _task_get_current_datetime(self):
        command = "date +'%F %T'"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['current_time'] = TError
        else:
            self.task_result['current_time'] = resp

    def _task_get_last_up_time(self):
        # command = "last reboot"
        command = "who -b | awk '{print $2,$3,$4}'"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['last_up_time'] = TError
        else:
            self.task_result['last_up_time'] = resp

    def _task_get_operating_time(self):
        command = "uptime"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['operating_time'] = TError
        else:
            find = os_pattern_obj.match(resp)
            if find:
                up_day, up_time, user, avg_1, avg_5, avg_15 = find.groups()
                if up_day:
                    up = '%s 天' % (up_day,)
                else:
                    up = '%s' % up_time
                self.task_result['operating_time'] = up

    def _task_get_cpu_info(self):
        # CPU数
        core_num_command = 'cat /proc/cpuinfo | grep "physical id" | sort | uniq | wc -l'
        resp, ok = self.do_command(core_num_command)
        if not ok:
            self.task_result['cpu_num'] = TError
        else:
            self.task_result['cpu_num'] = resp

        # 每物理核心数
        physical_command = 'cat /proc/cpuinfo | grep "cpu cores" | uniq'
        resp, ok = self.do_command(physical_command)
        if not ok:
            self.task_result['cpu_physical_cores'] = TError
        else:
            self.task_result['cpu_physical_cores'] = resp.rsplit()[-1]

        # 逻辑核数
        logical_command = 'cat /proc/cpuinfo | grep "processor" | wc -l'
        resp, ok = self.do_command(logical_command)
        if not ok:
            self.task_result['cpu_logical_cores'] = TError
        else:
            self.task_result['cpu_logical_cores'] = resp

        # CPU 型号
        cpu_model_command = 'cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq'
        resp, ok = self.do_command(cpu_model_command)
        if not ok:
            self.task_result['cpu_model'] = TError
        else:
            self.task_result['cpu_model'] = resp

    def _task_get_mem_info(self):
        # 物理内存信息
        free_command = 'free -h|grep -i mem'
        resp, ok = self.do_command(free_command)
        if not ok:
            self.task_result['memory_total'] = TError
            self.task_result['memory_used'] = TError
            self.task_result['memory_available'] = TError
        else:
            total, used, free, *arg, available = resp.split()[1:]
            self.task_result['memory_total'] = total
            self.task_result['memory_used'] = used
            self.task_result['memory_available'] = available

        # 虚拟内存信息
        free_command = 'free -h|grep -i swap'
        resp, ok = self.do_command(free_command)
        if not ok:
            self.task_result['swap_total'] = TError
            self.task_result['swap_used'] = TError
            self.task_result['swap_free'] = TError
        else:
            total, used, free, *arg = resp.split()[1:]
            self.task_result['swap_total'] = total
            self.task_result['swap_used'] = used
            self.task_result['swap_free'] = free

    def _task_get_disk_info(self):
        command = "df -hT -x tmpfs -x overlay -x devtmpfs|" \
                  "awk '{if (NR > 1 && $1!=tmpfs) {print $1,$2,$3,$4,$5,$6,$7}}'"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['disk_info_list'] = []
        else:
            disk_info_list = []
            for disk in resp.split('\n'):
                if not disk:
                    continue
                disk_info = [d.strip() for d in disk.split()]
                disk_info_list.append({
                    'file_system': disk_info[0], 'file_type': disk_info[1],
                    'file_size': disk_info[2], 'file_used': disk_info[3],
                    'file_available': disk_info[4], 'file_usage_rate': disk_info[5],
                    'file_mount': disk_info[6]
                })
            self.task_result['disk_info_list'] = disk_info_list

    def _task_get_system_params(self):
        # SELinux是否开启
        selinux_command = 'getenforce'
        resp, ok = self.do_command(selinux_command)
        if not ok:
            self.task_result['selinux_enable'] = TError
        else:
            self.task_result['selinux_enable'] = resp

        # 防火墙是否开启
        firewalld_command = 'systemctl status firewalld | ' \
                            'grep active > /dev/null 2>&1;if [[ $? -eq 0 ]];' \
                            'then echo 1;else echo 0;fi'
        resp, ok = self.do_command(firewalld_command)
        if not ok:
            self.task_result['firewall_enable'] = TError
        else:
            boolean_display = boolean(resp)
            self.task_result['firewall_enable'] = boolean_display
            if boolean_display != const.YES:
                self.set_abnormal_event(const.FIREWALLD_NOT_ENABLED_WARNING, const.CRITICAL)

        # 是否开启RSyslog
        firewalld_command = 'systemctl status rsyslog | ' \
                            'grep active > /dev/null 2>&1;if [[ $? -eq 0 ]];' \
                            'then echo 1;else echo 0;fi'
        resp, ok = self.do_command(firewalld_command)
        if not ok:
            self.task_result['rsyslog_enable'] = TError
        else:
            self.task_result['rsyslog_enable'] = boolean(resp)

        # 是否存在定时任务
        crontab_command = 'ls /var/spool/cron/ |wc -l'
        resp, ok = self.do_command(crontab_command)
        if not ok:
            self.task_result['exist_crontab'] = TError
        else:
            self.task_result['exist_crontab'] = boolean(resp)

    @staticmethod
    def __get_port_tidy_display(port_str):
        # 首先分割字符串，并清除掉多余的字符
        ports = map(lambda x: x.strip(), port_str.split(','))
        # 过滤掉非数字类型元素
        ports = filter(lambda x: x.isdigit(), ports)
        # 转换数据类型并排序
        ports = sorted(map(int, ports)) + [99999]
        finally_port = []
        start, end = '', ''
        for i in range(0, len(ports) - 1):
            if ports[i] + 1 == ports[i + 1]:
                if not start:
                    start = ports[i]
            elif start:
                end = ports[i]
                finally_port.append('%s-%s' % (start, end))
                start, end = '', ''
            else:
                finally_port.append(str(ports[i]))
        return ', '.join(finally_port)

    def _task_get_expose_port(self):
        # 系统监听的端口
        ss_command = "ss -tuln | grep LISTEN | awk '{print $5}' |" \
                     " awk -F: '{print $2$4}' | sort |uniq -d |" \
                     " tr '\n' ',' | sed 's/,$//'"
        resp, ok = self.do_command(ss_command)
        if not ok:
            self.task_result['expose_port'] = TError
        else:
            ports = self.__get_port_tidy_display(resp)
            self.task_result['expose_port'] = ports

    def _task_get_zombie_process(self):
        command = "ps -e -o ppid,stat | grep Z| wc -l"
        resp, ok = self.do_command(command)
        if not ok:
            self.task_result['exist_zombie'] = TError
        else:
            boolean_display = boolean(resp)
            self.task_result['exist_zombie'] = boolean_display
            if boolean_display == const.YES:
                self.set_abnormal_event(const.ZOMBIE_EXIST_ERROR, const.NORMAL)
