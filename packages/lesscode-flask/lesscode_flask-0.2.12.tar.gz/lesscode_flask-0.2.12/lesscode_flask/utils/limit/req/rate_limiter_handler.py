import time
import logging

from flask import current_app, request

from lesscode_flask.model.response_result import ResponseResult
from lesscode_flask.model.user import flask_login
from lesscode_flask.utils.fs_util import fs_webhook
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
        # 如果配置了飞书 webhook URL，则发送告警通知
        limit_fs_webhook_url = current_app.config.get("LIMIT_FS_WEBHOOK_URL")
        # 如果配置了飞书 webhook URL，则发送告警通知
        if limit_fs_webhook_url:
            content = []
            current_user = flask_login.current_user
            # 收集用户相关信息
            content.append(f"用户名称：{current_user.display_name}")
            phone_no = current_user.phone_no if current_user.phone_no is not None else "-"
            content.append(f"手机号：{phone_no}")
            content.append(f"用户IP：{request.remote_addr}")
            content.append(f"资源地址：{request.url_rule.rule}")

            # 发送飞书 webhook 告警
            fs_webhook(limit_fs_webhook_url, "触发频率限流告警", content)
        return ResponseResult.fail(status_code="403", http_code="403", message="请求过于频繁，请稍后再试！")