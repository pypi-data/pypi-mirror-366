import logging
from lesscode_flask.utils.redis.redis_helper import RedisHelper

logger = logging.getLogger(__name__)

class RedisCountLimiter:
    """Redis限流计数器实现"""
    
    def __init__(self, redis_key):
        self.redis_key = redis_key

    def is_allowed(self, key, count, time_window, cost=1):
        """
        检查是否允许请求
        :param key: 限流键
        :param count: 时间窗口内的请求数量限制
        :param time_window: 时间窗口（秒）
        :param cost: 本次请求消耗的令牌数
        :return: (allowed, remaining)
        """
        if not key: # 没有key表示不验证
            return True, 0
        key = f"limit_count:{key}"

        try:
            remaining = RedisHelper(self.redis_key).sync_get(key)
            if remaining is None:
                remaining = count-cost
                RedisHelper(self.redis_key).sync_set(key,remaining,time_window)
            else:
                # 键存在，减少令牌数
                remaining = RedisHelper(self.redis_key).sync_incrby(name=key,amount=0- cost)
            if remaining < 0:
                return False, remaining
            else:
                return True, remaining
        except Exception as e:
            # Redis出错时的降级处理
            logger.error(f"Redis count limiter error: {e}")
            return True, remaining
