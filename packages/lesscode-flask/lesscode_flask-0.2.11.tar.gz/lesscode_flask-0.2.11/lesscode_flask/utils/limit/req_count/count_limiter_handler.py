import logging

from flask import current_app, request

from lesscode_flask.model.response_result import ResponseResult
from lesscode_flask.model.user import flask_login
from lesscode_flask.utils.fs_util import fs_webhook

logger = logging.getLogger(__name__)


class CountLimitHandler:
    """
    限流后的处理函数实现
    """

    def __init__(self, req, remaining):
        self.req = req
        self.remaining = remaining


    def response_handler(self):
        """
        处理请求频率超限的响应

        该函数用于当用户请求过于频繁触发限流时，返回相应的错误响应。
        同时会发送告警信息到飞书 webhook，记录相关用户和请求信息。

        Returns:
            ResponseResult: 包含403状态码和错误信息的响应结果
        """
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
            fs_webhook(limit_fs_webhook_url, "触发总量限流告警", content)
        return ResponseResult.fail(status_code="403", http_code="403", message="请求过于频繁，请稍后再试！")
