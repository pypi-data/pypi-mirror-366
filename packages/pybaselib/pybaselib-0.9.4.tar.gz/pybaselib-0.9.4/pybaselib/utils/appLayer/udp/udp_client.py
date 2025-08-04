# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/6 19:04
import socket
import time
from pybaselib.utils import UDPNonResponse


class UDPClient:
    def __init__(self, server_ip="127.0.0.1", server_port=10012, buffer_size=1024, timeout=3, max_retries=3):
        """
        初始化 UDP 客户端
        :param server_ip: 服务器 IP 地址
        :param server_port: 服务器端口
        :param buffer_size: 接收缓冲区大小
        :param timeout: 服务器响应超时时间（秒）
        :param max_retries: 最大超时重试次数
        """
        self.server_address = (server_ip, server_port)
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.max_retries = max_retries
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建 UDP 套接字
        self.sock.settimeout(self.timeout)  # 设置超时时间

    def send_message(self, message):
        """
        发送消息到服务器并等待响应
        :param message: 发送的字符串消息
        :return: 服务器的回复或 None（如果超时）
        """
        retries = 0
        while retries < self.max_retries:
            try:
                if isinstance(message, bytes):
                    self.sock.sendto(message, self.server_address)  # 发送数据
                else:
                    self.sock.sendto(message.encode(), self.server_address)  # 发送数据
                data, _ = self.sock.recvfrom(self.buffer_size)  # 接收服务器回复
                if isinstance(message, bytes):
                    return data
                else:
                    return data.decode()
            except socket.timeout:
                retries += 1
                print(f"警告: 服务器无响应，重试 {retries}/{self.max_retries} ...")

        print("错误: 服务器无响应，客户端即将退出。")
        raise UDPNonResponse("UDP服务器无响应")  # 服务器无响应

    def close(self):
        """ 关闭 UDP 套接字 """
        self.sock.close()


if __name__ == "__main__":
    client = UDPClient(server_ip="192.168.1.120")
    print(client.send_message(b'\x02420001\x03'))
