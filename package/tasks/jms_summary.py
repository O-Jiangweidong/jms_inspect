import os

from .base import BaseTask, TaskType


__all__ = ['JmsSummaryTask']


class JmsSummaryTask(BaseTask):
    NAME = '堡垒机信息汇总'
    TYPE = TaskType.JUMPSERVER
    PRIORITY = 9998

    def __init__(self):
        super().__init__()
        self.mysql_client = None

    @staticmethod
    def get_do_params():
        return ['mysql_client']

    def _get_jms_summary(self):
        # 获取用户总数
        sql1 = "select count(*) from users_user where is_service_account=0"
        self.mysql_client.execute(sql1)
        result1 = self.mysql_client.fetchone()[0]
        # 获取资产总数
        sql2 = "select count(*) from assets_asset"
        self.mysql_client.execute(sql2)
        result2 = self.mysql_client.fetchone()[0]
        # 获取在线会话总数
        sql3 = "select count(*) from terminal_session where is_finished=0"
        self.mysql_client.execute(sql3)
        result3 = self.mysql_client.fetchone()[0]
        # 获取30天内活跃用户数
        sql4 = "select count(distinct username) from audits_userloginlog " \
               "where TO_DAYS( now( ) ) - TO_DAYS( datetime ) <= 30;"
        self.mysql_client.execute(sql4)
        result4 = self.mysql_client.fetchone()[0]
        # 获取30天内会话总数
        sql5 = "select COUNT(*) '会话管理数量' from terminal_session where" \
               " datediff( NOW(), date_start ) <= 30"
        self.mysql_client.execute(sql5)
        result5 = self.mysql_client.fetchone()[0]
        # 获取基础平台为 Windows 及 Linux 的平台 ID
        sql6_1 = "select base, id from assets_platform where base=%s or base=%s"
        # 获取基于某个平台的资产总数
        sql6_2 = "select count(*) from assets_asset where platform_id in %s"
        self.mysql_client.execute(sql6_1, ('Windows', 'Linux'))
        result6_1 = self.mysql_client.fetchall()
        linux_id_list = []
        windows_id_list = []
        for base, p_id in result6_1:
            if base == 'Windows':
                windows_id_list.append(p_id)
            else:
                linux_id_list.append(p_id)
        self.mysql_client.execute(sql6_2, (linux_id_list,))
        result6_2 = self.mysql_client.fetchone()[0]
        self.mysql_client.execute(sql6_2, (windows_id_list,))
        result6_3 = self.mysql_client.fetchone()[0]

        header = ('++', '-', '++', '-', '++', '-', '++', '-', '++', '-')
        row1 = (
            '用户总数', str(result1), '资产总数', str(result2),
            'Windows 资产数', str(result6_3), 'Linux 资产数', str(result6_2),
            '在线会话数', str(result3)
        )
        row2 = (
            '30天活跃用户人数', str(result4), '30天会话总数', str(result5)
        )
        table = (header, row1, row2)
        self.task_result.append((table, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_jms_summary()
        return self.task_result
