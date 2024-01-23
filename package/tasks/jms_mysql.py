import datetime

from .base import BaseTask, TaskType, TError


__all__ = ['JmsMySQLTask']


class JmsMySQLTask(BaseTask):
    NAME = '堡垒机后端 MySQL 信息'
    TYPE = TaskType.MYSQL

    def __init__(self):
        super().__init__()
        self.mysql_client = None

    @staticmethod
    def get_do_params():
        return ['jms_config', 'script_config', 'mysql_client']

    @staticmethod
    def get_tables_order_by_rows(sql_result, limit=10):
        table = []
        for table_name, table_record, table_size in sql_result[:limit]:
            table.append({
                'table_name': table_name, 'table_record': table_record,
                'table_size': table_size
            })
        return table

    def _task_get_tables_info(self):
        sql = "SELECT table_name, table_rows, " \
              "ROUND(data_length/1024/1024, 2)" \
              "FROM information_schema.tables WHERE table_schema=%s " \
              "ORDER BY table_rows DESC;"
        self.mysql_client.execute(sql, (self.jms_config.get('DB_NAME'),))
        sql_result = self.mysql_client.fetchall()
        table = self.get_tables_order_by_rows(sql_result)
        self.task_result['top_10_table'] = table

    def _task_get_db_info(self):
        sql = "SHOW GLOBAL VARIABLES"
        self.mysql_client.execute(sql)
        variables = self.mysql_client.fetchall()
        sql = "SHOW GLOBAL STATUS"
        self.mysql_client.execute(sql)
        status = self.mysql_client.fetchall()
        db_info = {k: v for k, v in variables + status}

        # QPS 计算
        questions = db_info.get('Questions', '0')
        uptime = db_info.get('Uptime', '1')
        qps = int(questions) / int(uptime)
        # TPS 计算
        commit = db_info.get('Com_commit', '0')
        rollback = db_info.get('Com_rollback', '0')
        tps = (int(commit) + int(rollback)) / int(uptime)
        # 获取slave信息
        db_slave_sql_running = TError
        db_slave_io_running = TError
        sql = "SHOW SLAVE STATUS"
        self.mysql_client.execute(sql)
        rest = self.mysql_client.fetchone() or []
        desc = self.mysql_client.description
        for i, v in enumerate(rest):
            if desc[i][0] == 'Slave_SQL_Running':
                db_slave_sql_running = rest[i]
            elif desc[i][0] == 'Slave_IO_Running':
                db_slave_io_running = rest[i]
        # 获取表数量
        sql = "SELECT COUNT(*) FROM information_schema.tables WHERE table_type='BASE TABLE'"
        self.mysql_client.execute(sql)
        table_count = self.mysql_client.fetchone()[0]

        # 获取当前事务数量
        sql = "SELECT count(*) FROM information_schema.innodb_trx"
        self.mysql_client.execute(sql)
        transaction_count = self.mysql_client.fetchone()[0]

        info_dict = {
            'db_operating_time': str(datetime.timedelta(seconds=int(uptime))),
            'db_sql_mode': db_info.get('sql_mode'),
            'db_max_connect': db_info.get('max_connections'),
            'db_current_connect': db_info.get('Threads_connected'),
            'db_qps': qps, 'db_tps': tps,
            'db_slow_query': db_info.get('slow_query_log'),
            'db_current_transaction': transaction_count,
            'db_charset': db_info.get('character_set_database'),
            'db_sort_rule': db_info.get('collation_database'),
            'db_slave_io_running': db_slave_io_running,
            'db_slave_sql_running': db_slave_sql_running,
            'db_table_count': table_count,
        }
        self.task_result.update(info_dict)
