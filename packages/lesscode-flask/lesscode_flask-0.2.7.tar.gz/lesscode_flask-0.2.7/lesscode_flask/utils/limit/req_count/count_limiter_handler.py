import logging

from lesscode_flask.model.response_result import ResponseResult

logger = logging.getLogger(__name__)


class CountLimitHandler:
    """
    限流后的处理函数实现
    """

    def __init__(self, req, remaining):
        self.req = req
        self.remaining = remaining


    def response_handler(self):
        message = "请求过于频繁，请稍后再试！"
        return ResponseResult.fail(status_code="403", http_code="403", message=message)