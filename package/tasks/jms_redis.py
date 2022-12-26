import redis

from package.utils.log import logger
from .base import BaseTask, TaskType


__all__ = ['JmsRedisTask']


class JmsRedisTask(BaseTask):
    NAME = '堡垒机后端 Redis 信息'
    TYPE = TaskType.REDIS

    def __init__(self):
        super().__init__()
        self.jms_config = None
        self.script_config = None
        self._redis_client = None

    @staticmethod
    def get_do_params():
        return ['jms_config', 'script_config']

    def get_redis_client(self):
        host = self.jms_config.get('REDIS_HOST', '127.0.0.1')
        port = self.jms_config.get('REDIS_PORT', 6379)
        password = self.jms_config.get('REDIS_PASSWORD')
        connect = redis.Redis(
            host=host, port=int(port), password=password
        )
        return connect

    @property
    def redis_client(self):
        if self._redis_client is None:
            self._redis_client = self.get_redis_client()
        return self._redis_client

    @staticmethod
    def filter_useful_info(redis_info):
        used_memory = redis_info.get('used_memory', 0)
        used_memory_human = redis_info.get('used_memory_human', 0)
        used_memory_rss_human = redis_info.get('used_memory_rss_human', 0)
        total_system_memory = redis_info.get('total_system_memory', 1)
        used_percent = int(used_memory) / int(total_system_memory) * 100
        used_percent_pretty = '{:.3f}%'.format(used_percent)
        redis_version = redis_info.get('redis_version', '未知')
        used_memory_peak = redis_info.get('used_memory_peak_human', '未知')
        connected = redis_info.get('connected_clients', 0)
        table = [
            ('Redis 版本', '使用内存', '系统分配内存', '内存占用率', '连接数', '内存消耗峰值'),
            (redis_version, used_memory_human, used_memory_rss_human,
             used_percent_pretty, connected, used_memory_peak),
        ]

        return table

    def get_redis_info(self):
        try:
            redis_info = self.redis_client.info()
        except Exception as error:
            logger.warning('%s:%s' % (self.NAME, error))
            redis_info = {}
        resp = self.filter_useful_info(redis_info)
        self.task_result.append((resp, False))

    def do(self, **kwargs):
        try:
            self.get_redis_info()
        except Exception as error:
            self.task_result.append((error, True))
        return self.task_result
