# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/27 09:27
import socket
import netifaces
import ipaddress


def get_ip_and_subnet():
    ip_info = {}
    # 获取所有网络接口
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        # 获取每个网络接口的 IP 地址和子网掩码
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ip_list = []
            for addr_info in addrs[netifaces.AF_INET]:
                ip_list.append({
                    "ip": addr_info.get('addr'),
                    "netmask": addr_info.get('netmask')
                })
            ip_info[interface] = ip_list
    return ip_info


def is_same_network(ip1, ip2, netmask):
    network1 = ipaddress.IPv4Network(f"{ip1}/{netmask}", strict=False)
    network2 = ipaddress.IPv4Network(f"{ip2}/{netmask}", strict=False)
    return network1.overlaps(network2)


def get_local_ip_in_same_network(target_ip):
    ip_info = get_ip_and_subnet()
    print(ip_info)
    for interface, ip_list in ip_info.items():
        for info in ip_list:
            local_ip = info["ip"]
            netmask = info["netmask"]
            if is_same_network(local_ip, target_ip, netmask):
                print(f"Target IP {target_ip} is in the same network as {local_ip} on interface {interface}.")
                return local_ip
            else:
                print(f"Target IP {target_ip} is NOT in the same network as {local_ip} on interface {interface}.")
    return None


def is_valid_ip(ip_str):
    try:
        # 尝试解析 IPv4 或 IPv6 地址
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        # 如果抛出 ValueError 异常，说明不是有效的 IP 地址
        return False
# Example: Check if target IP is in the same network
# target_ip = "192.168.1.120"
# check_ip_in_same_network(target_ip)

# if __name__ == "__main__":
#     get_local_ip_in_same_network("192.168.1.177")
