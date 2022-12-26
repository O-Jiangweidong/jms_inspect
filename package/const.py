SCRIPT_DOCUMENT = """
jms_inspect_cli 0.1

使用方式: jms-inspect_cli [命令] [参数]]
  -h                         输出帮助信息 (同--help)
  --help                     输出帮助信息 (同-h)
  --report-type <type>       最终报告类型 (类型有 pdf(默认)、excel(暂未支持)、all)
  --inspect-config <file>    巡检脚本配置文件路径 (默认位置: %s)
  --machine-template <file>  待巡检机器模板文件路径 (默认位置: %s)
"""
