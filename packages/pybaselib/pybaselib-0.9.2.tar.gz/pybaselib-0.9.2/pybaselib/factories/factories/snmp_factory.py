# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/9 22:36
from pybaselib.utils.appLayer.snmp import SNMPManager


class SNMPFactory:
    """ SNMP 连接工厂，缓存已创建的实例 """
    _instances = {}

    @staticmethod
    def get_snmp_connection(name="default",  host="192.168.1.1",
                            central_port=161, local_port=161,
                            community="public", mib_name="NTCIP1203v03f-MIB"):
        if name not in SNMPFactory._instances:
            SNMPFactory._instances[name] = SNMPManager(host, central_port=central_port,
                                                       local_port=local_port, community=community,
                                                       mib_name=mib_name)
        return SNMPFactory._instances[name]

    @staticmethod
    def switch_to_local(local_port=None):
        for name, snmp_obj in SNMPFactory._instances.items():
            snmp_obj.switch_to_local(local_port=local_port)

    @staticmethod
    def switch_to_central():
        for name, snmp_obj in SNMPFactory._instances.items():
            snmp_obj.switch_to_central()
