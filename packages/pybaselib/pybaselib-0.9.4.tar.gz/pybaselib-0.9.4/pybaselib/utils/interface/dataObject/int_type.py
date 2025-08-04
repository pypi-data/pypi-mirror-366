# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/7 14:24
from typing import Protocol


class IntType(Protocol):
    @staticmethod
    def int_to_hex_string(intValue: int, length=2) -> str:
        """
        将整数转换为指定长度的十六进制字符串
        不足位补0, 实际整数转十六进制超过了位数,返回超过位数16进制
        如：
            f"{0x02:02X}" ==> '02'
            f"{2:02X}" ==> '02'
        :param intValue: 
        :param length: 
        :return: 
        """
        pass

    @staticmethod
    def int_to_binary_string(int_value: int, length: int, reversal=True) -> str:
        """
        将十进制转为指定位数的2进制,支持反转结果
        示例: 30 转为15位二进制
        '000000000011110'
        反转结果位
        '011110000000000'
        :param int_value:
        :param length:
        :param reversal:
        :return:
        """
        pass

    @staticmethod
    def ip_to_hex_string(ip_value) -> str:
        """
        把IP地址转为4字节十六进制
        如:
            "192.168.1.122" ==> 'C0A8017A'
        :param ip_value:
        :return:
        """
        pass

