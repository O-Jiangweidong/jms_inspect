import csv
import getopt
import os
import re
import sys

import pymysql

from importlib import import_module
from datetime import datetime

from package.tasks.base import TaskExecutor, TaskType
from package.utils.log import logger
from package.utils.tableprint import TablePrint
from package.utils.tools import (
    is_machine_connect, get_current_datetime_display, get_current_timestamp
)
from package.utils.config import Config
from package.utils.html import HtmlPrinter


BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class JumpServerInspector(object):
    def __init__(self):
        self._table_print = TablePrint()
        self._machine_info_list = []
        self._mysql_client = None
        self._report_type = 'html'
        self._machine_config_path = os.path.join(BASE_PATH, 'package', 'static', 'extends', 'demo.csv')
        self._script_config = os.path.join(BASE_PATH, 'package', 'static', 'config', 'config.txt')
        self.jms_config = None
        self.script_config = None

    def get_mysql_client(self):
        host = self.jms_config.get('DB_HOST')
        port = self.jms_config.get('DB_PORT')
        user = self.jms_config.get('DB_USER')
        password = self.jms_config.get('DB_PASSWORD')
        database = self.jms_config.get('DB_NAME')
        connect = pymysql.connect(
            host=host, port=int(port), user=user, password=password,
            database=database
        )
        cur = connect.cursor()
        return cur

    @property
    def mysql_client(self):
        if self._mysql_client is None:
            self._mysql_client = self.get_mysql_client()
        return self._mysql_client

    @property
    def current_timestamp(self):
        return get_current_timestamp()

    def _view_script_document(self):
        from package.const import SCRIPT_DOCUMENT
        script_document = SCRIPT_DOCUMENT % (self._script_config, self._machine_config_path)
        logger.empty(script_document, br=False)

    def _set_report_type(self, report_type):
        support_report_type = ('html', 'excel', 'all')
        if report_type in support_report_type:
            self._report_type = report_type
        else:
            return '报告类型%s有误，只能为 [%s]' % (report_type, '、'.join(support_report_type))

    def _check_config(self):
        """
        检查堡垒机的配置文件路径
        检查脚本配置文件
        :return:
        """

        if not os.path.exists(self._script_config):
            err_msg = '请检查文件路径: [%s]，文件不存在。' % self._script_config
            return False, err_msg

        try:
            self.jms_config = Config(self._script_config, config_prefix='JMS_')
            self.script_config = Config(self._script_config)
        except ValueError as err:
            return False, str(err)

        return True, None

    def _get_machine_config_path(self):
        """
        获取待检查机器模板路径
        :return:
        """
        if not os.path.exists(self._machine_config_path):
            err_msg = '请检查文件路径: [%s]，文件不存在。' % self._machine_config_path
            return False, err_msg
        return True, None

    def table_pretty_output(self):
        headers = self._machine_info_list[0].keys()
        self._table_print.add_headers(headers)
        for machine in self._machine_info_list:
            self._table_print.add_row(machine.values())

        self._table_print.show()

    def _check_machine_config_is_valid(self):
        """
        检查用户输入的机器模板是否符合要求
        :return:
        """
        logger.debug('正在检查模板文件中机器是否合法...')
        ip_re = re.compile(r'((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))')
        unique_set, multiple_name = set(), None
        try:
            with open(self._machine_config_path, encoding='gbk')as f:
                reader = csv.reader(f)
                # 忽略首行(表头)
                _ = next(reader)
                for row in reader:
                    ip, port = row[2], row[3]
                    machine_info = {
                        'name': row[0], 'type': row[1].upper(),
                        'ssh_ip': ip, 'ssh_port': port,
                        'ssh_username': row[4], 'ssh_password': row[5]
                    }

                    if port.isdigit():
                        port = int(port)
                    if ip_re.match(ip) and is_machine_connect(ip, port):
                        machine_info['valid'] = True
                    else:
                        machine_info['valid'] = False
                    self._machine_info_list.append(machine_info)
                    if row[0] in unique_set:
                        multiple_name = row[0]
                    unique_set.add(row[0])
        except Exception as err:
            err_msg = '机器配置填写有误: %s' % err
            return False, err_msg

        if not self._machine_info_list:
            err_msg = '没有获取到机器信息，请检查此文件内容: %s' % self._machine_config_path
            return False, err_msg

        if multiple_name:
            err_msg = '待巡检机器名称重复，名称为: %s' % multiple_name
            return False, err_msg
        return True, None

    @staticmethod
    def _get_tasks_class():
        task_modules = []
        task_module_path = os.path.join(BASE_PATH, 'package', 'tasks')
        for module in os.listdir(task_module_path):
            module_string = 'package.tasks.' + module.rsplit('.')[0]
            task_module = import_module(module_string)
            expose_task_class = getattr(task_module, '__all__', None)
            if expose_task_class is not None:
                for class_name in expose_task_class:
                    task_modules.append(getattr(task_module, class_name))
        return task_modules

    def get_all_task(self, need_task_type):
        tasks_class = self._get_tasks_class()
        return_value = []
        for task_class in tasks_class:
            task_type = getattr(task_class, 'TYPE')
            if task_type != TaskType.GENERATOR \
                    and task_type != need_task_type:
                continue
            if task_type == TaskType.VIRTUAL \
                    and task_type != need_task_type:
                continue
            task = task_class()
            do_params = task.get_do_params()
            for param in do_params:
                task.set_do_params(param, getattr(self, param))
            return_value.append(task)
        return return_value

    def pre_check(self):
        """
        程序预检通道
        :return:
        """
        logger.debug('开始检查配置等相关信息...')
        ok, err = self._check_config()
        if not ok:
            logger.error(err)
            return False

        ok, err = self._get_machine_config_path()
        if not ok:
            logger.error(err)
            return False

        ok, err = self._check_machine_config_is_valid()
        if not ok:
            logger.error(err)
            return False

        self.table_pretty_output()
        answer = input('是否继续执行，本地任务只会执行有效资产(默认为 yes): ')
        if answer.lower() not in ['y', 'yes', '']:
            return False
        return True

    def _get_do_machines(self):
        do_machines = self._machine_info_list
        for m in self._machine_info_list:
            if m['type'] == 'MYSQL':
                do_machines.append({
                    'name': '虚拟任务', 'type': 'VIRTUAL', 'valid': True,
                    'ssh_ip': m['ssh_ip'], 'ssh_port': m['ssh_port'],
                    'ssh_username': m['ssh_username'],
                    'ssh_password': m['ssh_password']
                })
                break
        return do_machines

    def do(self):
        result_summary, v_info, machines = {}, {}, []
        for machine in self._get_do_machines():
            if machine.get('valid'):
                tasks = self.get_all_task(machine['type'])
                task_executor = TaskExecutor(**machine)
                task_executor.add_tasks(tasks)
                result_dict = task_executor.execute()

                if machine['type'] == TaskType.VIRTUAL:
                    result_summary['v'] = result_dict
                else:
                    result_dict['machine_type'] = machine['type']
                    result_dict['machine_name'] = machine['name']
                    machines.append(result_dict)
            result_summary['machines'] = machines
        return result_summary

    @staticmethod
    def _to_html(filename: str, content: dict, **kwargs):
        filename += '.html'
        html_printer = HtmlPrinter('jumpserver_report.html')
        html_printer.save(filename, content)
        logger.info('文件生成成功，文件路径: %s' % filename)

    @staticmethod
    def _to_pdf(filename: str, content: dict, **kwargs):
        filename += '.pdf'
        logger.warning('此格式报告还未支持')
        # logger.info('文件生成成功，文件路径: %s' % filename)

    @staticmethod
    def _to_excel(filename: str, content: dict, **kwargs):
        filename += '.xlsx'
        logger.warning('此格式报告还未支持')
        # logger.info('文件生成成功，文件路径: %s' % filename)

    def _to_all_type(self, filename: str, content: dict, **kwargs):
        self._to_pdf(filename, content, **kwargs)
        self._to_html(filename, content, **kwargs)
        self._to_excel(filename, content, **kwargs)

    def store_file(self, result_summary, file_type):
        file_type_handler = {
            'pdf': self._to_pdf,
            'html': self._to_html,
            'excel': self._to_excel,
            'all': self._to_all_type,
        }

        func = file_type_handler.get(file_type, self._to_html)

        output_path = os.path.join(BASE_PATH, 'output')
        filename = get_current_datetime_display()
        result_file_name = os.path.join(output_path, filename)
        os.makedirs(output_path, exist_ok=True)

        func(filename=result_file_name, content=result_summary)

    def __get_machine_info(self):
        machine_info, jms_count, mysql_count, redis_count, other_count = [], 0, 0, 0, 0
        for m in self._machine_info_list:
            if m['type'] == TaskType.VIRTUAL:
                continue
            if m['type'] == TaskType.JUMPSERVER:
                jms_count += 1
            elif m['type'] == TaskType.MYSQL:
                mysql_count += 1
            elif m['type'] == TaskType.REDIS:
                redis_count += 1
            else:
                other_count += 1

            machine = {
                'machine_name': m['name'], 'machine_type': m['type'],
                'machine_ip': m['ssh_ip'], 'machine_port': m['ssh_port'],
                'machine_username': m['ssh_username'],
                'machine_valid': m['valid']
            }
            machine_info.append(machine)
        total_count = sum([jms_count, mysql_count, redis_count, other_count])
        return machine_info, jms_count, mysql_count, redis_count, other_count, total_count

    def _set_task_global_info(self, result_summary: dict):
        # 设置报告时间
        current_date = datetime.now().date()
        result_summary['inspect_datetime'] = current_date
        # 设置巡检机器信息
        machines, *count_info = self.__get_machine_info()
        global_info = {
            'machines': machines, 'jms_count': count_info[0],
            'mysql_count': count_info[1], 'redis_count': count_info[2],
            'other_count': count_info[3], 'total_count': count_info[4]
        }
        result_summary['gb_info'] = global_info

    def filter_options(self, options):
        """
        :param options: 命令行接收用户输入的参数
        :return: 参数
        """
        opts = []
        short_options = 'h'
        long_options = [
            'help', 'report-type=',
            'inspect-config=', 'machine-template='
        ]
        try:
            # 短参数后加`:` 表示该参数后需要加参数
            opts, _ = getopt.getopt(
                options, short_options, long_options
            )
        except getopt.GetoptError:
            self._view_script_document()
            self.exit_program()
        if not opts:
            self._view_script_document()
            self.exit_program()

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self._view_script_document()
                self.exit_program()
            elif opt in ('--report-type',):
                err = self._set_report_type(arg)
                if err is not None:
                    logger.error(err)
                    self.exit_program()
            elif opt in ('--inspect-config',):
                self._script_config = arg
            elif opt in ('--machine-template',):
                self._machine_config_path = arg
            else:
                self._view_script_document()
                self.exit_program()

    @staticmethod
    def exit_program(show=False):
        """
        退出程序，并打印注释
        :return: None
        """
        if show:
            logger.info('退出成功')
        sys.exit()

    def run(self):
        """
        程序运行入口
        :return:
        """
        try:
            self.filter_options(sys.argv[1:])
            ok = self.pre_check()
            if ok:
                result_summary = self.do()
                self._set_task_global_info(result_summary)
                self.store_file(result_summary, self._report_type)
            else:
                self.exit_program(show=True)

        except Exception as err:
            logger.error('执行任务出错，错误: %s' % err)
            raise err
        except KeyboardInterrupt:
            logger.info('用户主动取消任务')


jms_inspector = JumpServerInspector()
jms_inspector.run()
