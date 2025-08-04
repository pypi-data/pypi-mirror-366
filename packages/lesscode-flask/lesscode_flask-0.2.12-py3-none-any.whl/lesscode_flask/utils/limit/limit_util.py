import hashlib

from flask import request, current_app

from lesscode_flask.model.user import flask_login
from lesscode_flask.utils.helpers import app_config
def limit_key_encode() -> str:
    limit_key = None
    # 白名单
    limit_white_list = app_config.get("LIMIT_WHITE_LIST", [])
    request_url = request.url_rule.rule
    if request_url in limit_white_list:
        # 白名单访问 直接返回None
        return None
    # 1、获取当前用户
    current_user = flask_login.current_user
    if current_user and not current_user.is_anonymous_user:
        user_id = current_user.id
        # 拼接 key 用户id+url
        limit_key = f"{user_id}:{request_url}"
    # 如果键为空，使用客户端IP
    if not limit_key:
        limit_key = f"{request.remote_addr}{request_url}"
    # 对键进行哈希处理，避免键过长
    limit_key = hashlib.md5(limit_key.encode('utf-8')).hexdigest()
    return hashlib.md5(limit_key.encode('utf-8')).hexdigest()


def get_rate_limit_info() -> str:
    """
    获取限流信息，包含限流key 频率 rate , 突发数量 burst:
    :return: 实际使用的限流键
    """
    rate = app_config.get("RATE_LIMIT_RATE", 1)  # 限流频率 单位是每秒
    burst = app_config.get("RATE_LIMIT_BURST", 0)  # 限流频率允许的突发值 请求速率超过（rate + brust）的请求会被直接拒绝。
    time_window = app_config.get("RATE_LIMIT_TIME_WINDOW", 1)  # 限流频率允许的突发值 请求速率超过（rate + brust）的请求会被直接拒绝。
    limit_key = limit_key_encode()
    return limit_key, rate, burst,time_window

def get_count_limit_info() -> str:
    """
    获取限流信息，包含限流key 总量 rate , 窗口期 burst:
    :return: 实际使用的限流键
    """
    # 窗口期内最大访问量
    count = app_config.get("COUNT_LIMIT_COUNT",500)
    # 窗口期时长 单位秒
    time_window = app_config.get("COUNT_LIMIT_TIME_WINDOW",3600)
    limit_key = limit_key_encode()
    return limit_key, count, time_window

