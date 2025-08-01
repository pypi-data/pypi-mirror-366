# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/26 21:19
import math
from pybaselib.utils.net import is_valid_ip
from pybaselib.utils import ParameterError
from pybaselib.utils.interface import IntType as intType
from functools import reduce


def int_to_hex_string(int_value, length=2):
    """
    16进制数也会转为十六进制string 没有0x
    当content 长度length时，只取length长度
    :param int_value:
    :param length:
    :return:
    """
    content =  f"{int_value:0{length}X}"
    # print(content, type(content), len(content), length)
    if len(content) > length:
        content = content[:length]
        # print(content)
        return content
    else:
        return content


def ip_to_hex_string(ip_value):
    hex_string = ""
    if is_valid_ip(ip_value):
        for item in ip_value.split("."):
            hex_string += f"{int(item):02X}"
        return hex_string
    else:
        raise ParameterError("无效的IP地址")


def int_to_binary_string(int_value, length, reversal=True):
    binary_string = format(int_value, f'0{length}b')
    if reversal:
        return reduce(lambda x, y: y + x, binary_string)
    else:
        return binary_string


def num_to_hex_ascii_hex(int_value) -> str:
    """
    把数字转为16进制字符串去除0x
    遍历这个16进制字符串,将单子字符转换为ASCII码表示(整数)
    将上述整数转为16进制字符串去除0x
    合并这些16进制字符串为一个字符串
    int -> hex_string -> ascii -> hex_string -> full_string
    :param int_value:
    :return:
    """
    return "".join(
        [int_to_hex_string(ord(char)) for char in hex(int_value).removeprefix("0x")])


def hex_to_ascii_num(hex_string):
    """
    应用于模拟FBI控制盒
    第一步将16进制字符串转为ASCII码字符表示
    第二步ASCII码字符当作16进制字符串转为整形
    整形即实际对应的结果
    :param hex_string:
    :return:
    """
    return hex_to_int(bytes.fromhex(hex_string).decode("utf-8"))


def hex_to_int(hex_string):
    return int(hex_string, 16)


def custom_round_division(a, b):
    """
    向上取整，有小数就进一位
    :param a:
    :param b:
    :return:
    """
    result = a / b
    return math.ceil(result)


def bits_to_hex(bit_string):
    """
        将比特流转换为十六进制字符串
        示例:
        Bit Data: 1000010010010010011000110000100011000010010010001010000101110000
        Length: 64 bits (8 bytes)
        Hex Data: 84926308C248A170
    """
    hex_string = hex(int(bit_string, 2))[2:].upper()  # 转换为整数 -> 十六进制 -> 去掉 '0x'

    # 补齐偶数长度
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string

    return hex_string


def hex_to_bits(hex_data):
    """
        将十六进制字符串转换为比特流
        Hex data: 84926308C248A170
        Bit Data: 1000010010010010011000110000100011000010010010001010000101110000
    """
    bin_data = bin(int(hex_data, 16))[2:]  # 转换为二进制字符串并去掉前缀 '0b'
    padding_length = 8 - (len(bin_data) % 8) if len(bin_data) % 8 != 0 else 0
    return '0' * padding_length + bin_data  # 确保比特数是8的倍数


class IntType:
    int_to_hex_string = staticmethod(int_to_hex_string)
    int_to_binary_string = staticmethod(int_to_binary_string)
    ip_to_hex_string = staticmethod(ip_to_hex_string)
    num_to_hex_ascii_hex = staticmethod(num_to_hex_ascii_hex)
    custom_round_division = staticmethod(custom_round_division)
    bits_to_hex = staticmethod(bits_to_hex)
    hex_to_bits = staticmethod(hex_to_bits)


if __name__ == '__main__':
    print(int_to_hex_string(62820, 4))
    print(num_to_hex_ascii_hex(32))
    # print(num_to_hex_ascii_hex(31))
    #
    # print(num_to_hex_ascii_hex(29))
    # print(num_to_hex_ascii_hex(25))
    # print(hex(32))
    # print(hex_to_int("30"))
    # print(int_to_hex_string(0x02))
    # print(ip_to_hex_string("192.168.1.122"))
    # print(int_to_binary_string(30, 15))
    # print(hex_to_ascii_num("3034"))
    # print(custom_round_division(30, 8))
