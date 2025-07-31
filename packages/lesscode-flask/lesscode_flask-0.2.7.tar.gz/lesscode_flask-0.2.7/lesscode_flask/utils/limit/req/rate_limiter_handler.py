import time
import logging

from lesscode_flask.model.response_result import ResponseResult
from lesscode_flask.utils.redis.redis_helper import RedisHelper

logger = logging.getLogger(__name__)


class RateLimitHandler:
    """
    限流后的处理函数实现
    """
    def __init__(self, req, delay: float, excess: float):
        """
         初始化
        :param req:
        :param delay: 延迟时间
        :param excess: 超出数量
        """
        self.req = req
        self.delay = delay
        self.excess = excess


    def response_handler(self):
        message = "请求过于频繁，请稍后再试"
        return ResponseResult.fail(status_code="403", http_code="403", message=message)