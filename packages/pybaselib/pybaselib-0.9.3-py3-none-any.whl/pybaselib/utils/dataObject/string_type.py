# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/19 19:33
import json

def string_to_bytes_length(string: str) -> int:
    """
    字符串对应字节长度
    :param string:
    :return:
    """
    # byte = len(str(string.encode('utf-8').hex()))/2
    # print(byte)
    return len(string.encode('utf-8'))

def json_to_bytes_to_hex(data: dict) -> str:
    """
    json字符串转为字节再转为16进制
    :param string:
    :return:
    """
    json_str = json.dumps(data)
    byte_data = json_str.encode('utf-8')
    hex_str = byte_data.hex()
    return hex_str

def has_non_ascii(s: str) -> bool:
    return any(ord(c) > 127 for c in s)

def process_string_if_non_ascii(s: str) -> str:
    """
    如果字符串包含 ASCII > 127 的字符，则返回该字符串的十六进制表示；
    否则返回原字符串。
    """
    if any(ord(c) > 127 for c in s):
        hex_str = ''.join(f"{ord(c):02X}" for c in s)
        return hex_str
    return s

class StringType:
    has_non_ascii = staticmethod(has_non_ascii)
    process_string_if_non_ascii = staticmethod(process_string_if_non_ascii)


if __name__ == "__main__":
    # print(string_to_bytes_length("FFFFFF0700010000C0A8017A"))
    print(has_non_ascii("éöçABCD"))
    print(has_non_ascii("abcdefghijklmnopqrst!,@#$%^&*()-=+{}[]"))
    print(process_string_if_non_ascii("éöçABCD"))