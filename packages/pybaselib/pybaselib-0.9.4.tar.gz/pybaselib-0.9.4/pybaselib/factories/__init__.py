# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/9 22:35
from .factory_registry import FactoryRegistry
from .factories.snmp_factory import SNMPFactory

FactoryRegistry.register_factory("snmp", SNMPFactory)
