# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/9 22:36
class FactoryRegistry:
    _factories = {}

    @classmethod
    def register_factory(cls, name, factory_callable):
        """ 注册工厂，可以是一个类或可调用对象 """
        if name not in cls._factories:
            cls._factories[name] = factory_callable

    @classmethod
    def get_factory(cls, name):
        return cls._factories.get(name, None)