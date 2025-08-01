# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/6 17:32
import logging


class GenErr(Exception):
    def __init__(self, message):
        self.message = message
        logging.error(self.message)
        super().__init__(self.message)


class BadValue(Exception):
    def __init__(self, message):
        self.message = message
        logging.error(self.message)
        super().__init__(self.message)


class ParameterError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnimplementedFunctionality(Exception):
    """
        此异常需要提交issue future
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DeviceError(Exception):
    """
        此异常需要告警
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BugException(Exception):
    """
        此异常需要告警
    """

    def __init__(self, message):
        self.message = message
        logging.error(self.message)
        super().__init__(self.message)


class UDPNonResponse(Exception):
    """
        UDP Server 无响应
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def assert_with_log(condition, message):
    if not condition:
        logging.error(f"断言失败: {message}")
        raise AssertionError(message)
