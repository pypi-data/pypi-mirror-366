# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/3/10 09:04
import importlib
import os
import sys
import pkgutil
from pathlib import Path


def dynamic_import(module_name, package="utils.modules"):
    """
    动态导入指定模块
    :param module_name: 要导入的模块名称（不带 .py）
    :param package: 模块所在的包路径，默认为 'utils.modules'
    :return: 导入的模块对象
    """
    try:
        full_module_name = f"{package}.{module_name}"
        return importlib.import_module(full_module_name)
    except ModuleNotFoundError as e:
        print(f"Error: {e}")
        return None


def import_all_modules_from_directory(directory="utils/modules"):
    """
    动态导入目录下的所有 Python 模块
    :param directory: 目标目录（默认是 utils/modules）
    :return: 已导入的模块字典
    """
    imported_modules = {}
    sys.path.insert(0, os.path.abspath(directory))  # 确保路径可访问

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # 去掉 .py
            module = dynamic_import(module_name)
            if module:
                imported_modules[module_name] = module

    sys.path.pop(0)  # 清理路径
    return imported_modules


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


# def singleton(cls, value):
#     instances = {}
#
#     if cls not in instances:
#         instances[cls] = cls(value)
#
#     return instances[cls]


def load_custom_classes(base_path=Path(__file__).parent.resolve()):
    """
    如果不同模块如果类同名,这部分没处理
    :param value:
    :param base_path:
    :return:
    """
    sys.path.insert(0, str(base_path))  # 添加到sys.path，确保可以导入 将 base_path 插入到 sys.path 的第一个位置（索引 0）。
    classes = {}

    for subpackage in base_path.iterdir():
        if subpackage.is_dir() and (subpackage / "__init__.py").exists():
            for finder, name, ispkg in pkgutil.walk_packages([str(subpackage)], prefix=f"{subpackage.name}."):
                try:
                    module = importlib.import_module(name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr.__module__.startswith(subpackage.name):  # 只导入类
                            classes[attr_name] = singleton(attr)
                except Exception as e:
                    print(f"Error importing {name}: {e}")

    return classes


def set_class_attributes(class_factory, cls_attr, class_name):
    """
    通过反射,给对象赋值
    :param cls_attr:
    :param class_factory:
    :param class_name:
    :return:
    """
    for cls_name, cls_obj in class_factory.items():
        if hasattr(cls_obj, cls_attr):
            if getattr(cls_obj, cls_attr) is None:
                setattr(cls_obj, cls_attr, class_factory[class_name])
                class_factory[cls_name] = cls_obj
