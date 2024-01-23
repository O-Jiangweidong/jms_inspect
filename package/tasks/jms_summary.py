from .base import BaseTask, TaskType


__all__ = ['JmsSummaryTask']


class JmsSummaryTask(BaseTask):
    NAME = '堡垒机信息汇总'
    TYPE = TaskType.VIRTUAL
    PRIORITY = 9998

    def __init__(self):
        super().__init__()
        self.mysql_client = None

    @staticmethod
    def get_do_params():
        return ['mysql_client']

    def get_num_of_asset_by_platform(self):
        sql = "SELECT p.name, COUNT(*) AS asset_count FROM assets_platform p " \
              "JOIN assets_asset a ON p.id = a.platform_id " \
              "GROUP BY p.name ORDER BY asset_count desc LIMIT 3;"
        self.mysql_client.execute(sql)
        result = self.mysql_client.fetchall()
        result_display = '，'.join(map(lambda x: '%s类型: %s个' % (x[0], x[1]), result))
        return result, result_display

    def _task_get_jms_summary(self):
        # 获取用户总数
        sql = "SELECT COUNT(*) FROM users_user WHERE is_service_account=0"
        self.mysql_client.execute(sql)
        user_count = self.mysql_client.fetchone()[0]
        # 获取资产总数
        sql = "SELECT COUNT(*) FROM assets_asset"
        self.mysql_client.execute(sql)
        asset_count = self.mysql_client.fetchone()[0]
        # 获取在线会话总数
        sql = "SELECT COUNT(*) FROM terminal_session WHERE is_finished=0"
        self.mysql_client.execute(sql)
        online_session = self.mysql_client.fetchone()[0]
        # 获取各平台资产数量
        __, asset_count_display = self.get_num_of_asset_by_platform()
        # 获取组织数量
        sql = "SELECT COUNT(*) FROM orgs_organization"
        self.mysql_client.execute(sql)
        organization_count = self.mysql_client.fetchone()[0]
        # 获取最大单日登录次数
        sql = "SELECT DATE(datetime) AS d, COUNT(*) AS num FROM audits_userloginlog " \
              "WHERE status=1 GROUP BY d ORDER BY num DESC LIMIT 1"
        self.mysql_client.execute(sql)
        res = self.mysql_client.fetchone()
        max_login_count = '%s(%s)' % (res[1], res[0])
        # 最大单日访问资产数
        # TODO 没数据记得处理下
        sql = "SELECT DATE(date_start) AS d, COUNT(*) AS num FROM terminal_session " \
              "GROUP BY d ORDER BY num DESC LIMIT 1"
        self.mysql_client.execute(sql)
        res = self.mysql_client.fetchone()
        max_connect_asset_count = '%s(%s)' % (res[1], res[0])
        # 近三月最大单日用户登录数
        sql = "SELECT DATE(datetime) AS d, COUNT(*) AS num FROM audits_userloginlog " \
              "WHERE status=1 AND datetime > DATE_SUB(CURDATE(), INTERVAL 3 MONTH) " \
              "GROUP BY d ORDER BY num DESC LIMIT 1"
        self.mysql_client.execute(sql)
        self.mysql_client.fetchone()
        last_3_month_max_login_count = '%s(%s)' % (res[1], res[0])
        # 近三月最大单日资产登录数
        sql = "SELECT DATE(date_start) AS d, COUNT(*) AS num FROM  terminal_session " \
              "WHERE date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH) " \
              "GROUP BY d ORDER BY num DESC LIMIT 1"
        self.mysql_client.execute(sql)
        self.mysql_client.fetchone()
        last_3_month_max_connect_asset_count = '%s(%s)' % (res[1], res[0])
        # 近一月登录用户数
        sql = "SELECT COUNT(DISTINCT username) FROM audits_userloginlog " \
              "WHERE status=1 AND datetime > DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
        self.mysql_client.execute(sql)
        last_1_month_login_count = self.mysql_client.fetchone()[0]
        # 近一月登录资产数
        sql = "SELECT COUNT(*) FROM terminal_session " \
              "WHERE date_start > DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
        self.mysql_client.execute(sql)
        last_1_month_connect_asset_count = self.mysql_client.fetchone()[0]
        # 近一月文件上传数
        sql = "SELECT COUNT(*) FROM audits_ftplog WHERE operate='Upload' " \
              "AND date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_1_month_upload_count = self.mysql_client.fetchone()[0]
        # 近三月登录用户数
        sql = "SELECT COUNT(DISTINCT username) FROM audits_userloginlog " \
              "WHERE status=1 AND datetime > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_login_count = self.mysql_client.fetchone()[0]
        # 近三月登录资产数
        sql = "SELECT COUNT(*) FROM terminal_session " \
              "WHERE date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_connect_asset_count = self.mysql_client.fetchone()[0]
        # 近三月文件上传数
        sql = "SELECT COUNT(*) FROM audits_ftplog WHERE operate='Upload' " \
              "AND date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_upload_count = self.mysql_client.fetchone()[0]
        # 近三月命令记录数
        sql = "SELECT COUNT(*) FROM terminal_command WHERE " \
              "FROM_UNIXTIME(timestamp) > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_command_count = self.mysql_client.fetchone()[0]
        # 近三月高危命令记录数
        sql = "SELECT count(*) FROM terminal_command WHERE risk_level=5 and " \
              "FROM_UNIXTIME(timestamp) > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_danger_command_count = self.mysql_client.fetchone()[0]
        # TODO 没数据记得处理
        # 近三月最大会话时长
        sql = "SELECT timediff(date_end, date_start) AS duration from terminal_session " \
              "WHERE date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH) " \
              "ORDER BY duration DESC LIMIT 1"
        self.mysql_client.execute(sql)
        last_3_month_max_session_duration = self.mysql_client.fetchone()[0]
        # 近三月平均会话时长
        sql = "SELECT ROUND(AVG(TIME_TO_SEC(TIMEDIFF(date_end, date_start))), 0) AS duration " \
              "FROM terminal_session WHERE date_start > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_avg_session_duration = self.mysql_client.fetchone()[0]
        # 近三月工单申请数
        sql = "SELECT COUNT(*) FROM tickets_ticket WHERE date_created > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        self.mysql_client.execute(sql)
        last_3_month_ticket_count = self.mysql_client.fetchone()[0]

        info_dict = {
            'user_count': user_count,
            'online_session': online_session, 'organization_count': organization_count,
            'max_login_count': max_login_count, 'asset_count_display': asset_count_display,
            'asset_count': asset_count, 'max_connect_asset_count': max_connect_asset_count,
            'last_3_month_connect_asset_count': last_3_month_connect_asset_count,
            'last_3_month_max_login_count': last_3_month_max_login_count,
            'last_3_month_max_connect_asset_count': last_3_month_max_connect_asset_count,
            'last_1_month_login_count': last_1_month_login_count,
            'last_1_month_connect_asset_count': last_1_month_connect_asset_count,
            'last_1_month_upload_count': last_1_month_upload_count,
            'last_3_month_login_count': last_3_month_login_count,
            'last_3_month_upload_count': last_3_month_upload_count,
            'last_3_month_command_count': last_3_month_command_count,
            'last_3_month_danger_command_count': last_3_month_danger_command_count,
            'last_3_month_max_session_duration': str(last_3_month_max_session_duration),
            'last_3_month_avg_session_duration': last_3_month_avg_session_duration,
            'last_3_month_ticket_count': last_3_month_ticket_count
        }
        self.task_result.update(info_dict)

    def _task_get_chart_data(self):
        # 按周用户登录折线图
        sql = "SELECT DATE(datetime) AS d, COUNT(*) AS num FROM audits_userloginlog " \
              "WHERE status=1 and DATE_SUB(CURDATE(), INTERVAL 6 DAY) <= datetime GROUP BY d"
        self.mysql_client.execute(sql)
        resp = self.mysql_client.fetchall()
        x = [str(i[0]) for i in resp]
        y = [i[1] for i in resp]
        self.task_result['user_login_chart'] = {'x': x, 'y': y}

        # 按周资产登录折线图
        sql = "SELECT DATE(date_start) AS d, COUNT(*) AS num FROM terminal_session " \
              "WHERE DATE_SUB(CURDATE(), INTERVAL 6 DAY) <= date_start GROUP BY d"
        self.mysql_client.execute(sql)
        resp = self.mysql_client.fetchall()
        x = [str(i[0]) for i in resp]
        y = [i[1] for i in resp]
        self.task_result['asset_connect_chart'] = {'x': x, 'y': y}

        # 月活跃用户柱状图
        sql = "SELECT username, count(*) AS num FROM audits_userloginlog " \
              "WHERE status=1 and DATE_SUB(CURDATE(), INTERVAL 1 MONTH) <= datetime " \
              "GROUP BY username ORDER BY num DESC LIMIT 5;"
        self.mysql_client.execute(sql)
        resp = self.mysql_client.fetchall()
        x = [str(i[0]) for i in resp]
        y = [i[1] for i in resp]
        self.task_result['active_user_chart'] = {'x': x, 'y': y}

        # 近3个月活跃资产柱状图
        sql = "SELECT asset, count(*) AS num FROM terminal_session " \
              "WHERE DATE_SUB(CURDATE(), INTERVAL 3 MONTH) <= date_start " \
              "GROUP BY asset ORDER BY num DESC LIMIT 5;"
        self.mysql_client.execute(sql)
        resp = self.mysql_client.fetchall()
        x = [str(i[0]) for i in resp]
        y = [i[1] for i in resp]
        self.task_result['active_asset_chart'] = {'x': x, 'y': y}

        # 近3个月各种协议访问饼状图
        sql = "SELECT protocol, count(*) AS num FROM terminal_session " \
              "WHERE DATE_SUB(CURDATE(), INTERVAL 3 MONTH) <= date_start " \
              "GROUP BY protocol ORDER BY num DESC"
        self.mysql_client.execute(sql)
        self.task_result['protocol_chart'] = [
            {'name': i[0], 'value': i[1]} for i in self.mysql_client.fetchall()
        ]
