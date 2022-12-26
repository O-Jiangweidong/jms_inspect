from .base import BaseTask, TaskType


__all__ = ['JmsMySQLTask']


class JmsMySQLTask(BaseTask):
    NAME = '堡垒机后端 MySQL 信息'
    TYPE = TaskType.MYSQL

    def __init__(self):
        super().__init__()
        self.mysql_client = None
        self.jms_config = None
        self.script_config = None

    @staticmethod
    def get_do_params():
        return ['jms_config', 'script_config', 'mysql_client']

    @staticmethod
    def get_tables_order_by_rows(sql_result):
        table = [('表名', '表记录数', '表大小(M)')]
        for table_name, table_record, table_size in sql_result[:10]:
            table.append((table_name, table_record, table_size))
        return table

    def filter_big_tables(self, sql_result):
        table_size_threshold = int(self.script_config.get(
            'MYSQL_TABLE_SIZE', 100
        ))
        table_record_threshold = int(self.script_config.get(
            'MYSQL_TABLE_RECORD', 1000
        )) * 10000

        resp = []
        for table_name, table_record, table_size in sql_result:
            if table_size > table_size_threshold or table_record > table_record_threshold:
                self.abnormal_number += 1
                warning = True
            else:
                continue
            info = '表名: %s; 表记录数: %s 个; 表大小: %s M;' % (table_name, table_record, table_size)
            resp.append((info, warning))
            resp.append(('', False))
        return resp

    def get_tables_info(self):
        sql = "select table_name, table_rows, " \
              "round(data_length/1024/1024, 2)" \
              "from information_schema.tables where table_schema=%s " \
              "order by table_rows desc;"
        self.mysql_client.execute(sql, (self.jms_config.get('DB_NAME'),))
        sql_result = self.mysql_client.fetchall()
        table = self.get_tables_order_by_rows(sql_result)
        resp = self.filter_big_tables(sql_result)
        self.task_result.extend(resp)
        self.task_result.append((table, False))

    def do(self, **kwargs):
        self.get_tables_info()
        return self.task_result
