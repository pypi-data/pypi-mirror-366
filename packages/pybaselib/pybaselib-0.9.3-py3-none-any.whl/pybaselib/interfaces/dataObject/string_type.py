# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/4/21 10:10
from typing import Protocol, Self, final

class StringType(Protocol):
    def strip(self):
        """
        去除字符串两端的空白字符
        :return:
        """
        pass

    def strip(self, content):
        """
        去除两边指定内容
        text.strip(' ') 去掉两边的空格（不包括换行，制表符）
        :param content:
        :return:
        """
        pass

    def lsstrip(self):
        """
        去除字符串左侧的空白字符
        :return:
        """
        pass

    def rstrip(self):
        """
        去除字符串右侧的空白字符
        :return:
        """
        pass

