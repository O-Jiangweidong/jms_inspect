import os


SCRIPT_DOCUMENT = """
jms_inspect_cli v0.2

使用方式: jms-inspect_cli [命令] [参数]]
  -h                         输出帮助信息 (同--help)
  --help                     输出帮助信息 (同-h)
  --report-type <type>       最终报告类型 (类型有 html(默认)、excel(暂未支持)、all)
  --inspect-config <file>    巡检脚本配置文件路径 (默认位置: %s)
  --machine-template <file>  待巡检机器模板文件路径 (默认位置: %s)
"""


STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


ZOMBIE_EXIST_ERROR = '节点下存在僵尸进程'
FIREWALLD_NOT_ENABLED_WARNING = '节点下防火墙未开启'

CRITICAL = 'critical'
NORMAL = 'normal'
SLIGHT = 'slight'

YES = '是'
NO = '否'
