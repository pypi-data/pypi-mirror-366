# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/9 13:07

import os
import platform

def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    res = os.system(f"ping {param} 2 {ip}")
    return res == 0

if __name__ == '__main__':
    # print(ping_ip('192.168.1.105'))
	print(ping_ip(1))