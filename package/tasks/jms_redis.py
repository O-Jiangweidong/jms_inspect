from package.utils.log import logger
from .base import BaseTask, TaskType, TError


__all__ = ['JmsRedisTask']


class JmsRedisTask(BaseTask):
    NAME = '堡垒机后端 Redis 信息'
    TYPE = TaskType.REDIS

    def __init__(self):
        super().__init__()
        self.redis_client = None

    @staticmethod
    def get_do_params():
        return ['jms_config', 'script_config', 'redis_client']

    def set_service_info(self, info):
        self.task_result['redis_version'] = info.get('redis_version', TError)
        self.task_result['redis_mode'] = info.get('redis_mode', TError)
        self.task_result['redis_port'] = info.get('tcp_port', TError)
        self.task_result['redis_uptime'] = info.get('uptime_in_days', TError)

    def set_client_info(self, info):
        self.task_result['redis_connect'] = info.get('connected_clients', TError)
        self.task_result['redis_cluster_connect'] = info.get('cluster_connections', TError)
        self.task_result['redis_max_connect'] = info.get('maxclients', TError)
        self.task_result['redis_blocked_connect'] = info.get('blocked_clients', TError)

    def set_mem_info(self, info):
        self.task_result['used_memory_human'] = info.get('used_memory_human', TError)
        self.task_result['used_memory_rss_human'] = info.get('used_memory_rss_human', TError)
        self.task_result['used_memory_peak_human'] = info.get('used_memory_peak_human', TError)
        self.task_result['used_memory_lua_human'] = info.get('used_memory_lua_human', TError)
        self.task_result['maxmemory_human'] = info.get('maxmemory_human', TError)
        self.task_result['maxmemory_policy'] = info.get('maxmemory_policy', TError)

    def set_statistics_info(self, info):
        self.task_result['total_connections_received'] = info.get('total_connections_received', TError)
        self.task_result['total_commands_processed'] = info.get('total_commands_processed', TError)
        self.task_result['instantaneous_ops_per_sec'] = info.get('instantaneous_ops_per_sec', TError)
        self.task_result['total_net_input_bytes'] = info.get('total_net_input_bytes', TError)
        self.task_result['total_net_output_bytes'] = info.get('total_net_output_bytes', TError)
        self.task_result['rejected_connections'] = info.get('rejected_connections', TError)
        self.task_result['expired_keys'] = info.get('expired_keys', TError)
        self.task_result['evicted_keys'] = info.get('evicted_keys', TError)
        self.task_result['keyspace_hits'] = info.get('keyspace_hits', TError)
        self.task_result['keyspace_misses'] = info.get('keyspace_misses', TError)
        self.task_result['pubsub_channels'] = info.get('pubsub_channels', TError)
        self.task_result['pubsub_patterns'] = info.get('pubsub_patterns', TError)

    def _task_get_redis_info(self):
        try:
            redis_info = self.redis_client.info()
        except Exception as error:
            logger.warning('%s:%s' % (self.NAME, error))
            redis_info = {}

        self.set_service_info(redis_info)
        self.set_client_info(redis_info)
        self.set_mem_info(redis_info)
        self.set_statistics_info(redis_info)
