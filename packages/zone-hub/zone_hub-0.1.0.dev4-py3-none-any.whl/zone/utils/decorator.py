import os
import sys
import time
from pathlib import Path
from functools import wraps


"""
这个模块定义一些修饰器
"""


def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):  # 改名为wrapper更明确，修正kwargs拼写
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]  # 简化了条件判断

    return wrapper


def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    """
    失败重试装饰器工厂

    参数:
        max_attempts: 最大尝试次数
        delay: 重试间隔(秒)
        exceptions: 触发重试的异常类型
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == max_attempts:
                        print(f"操作失败，已达最大重试次数 {max_attempts}")
                        raise  # 重新抛出最后捕获的异常
                    print(f"重试 {attempts}/{max_attempts}，遇到错误: {str(e)}")
                    time.sleep(delay)

        return wrapper

    return decorator
