# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/9 08:38
# setup.py
from setuptools import setup, find_packages

setup(
    name="pybaselib",  # 包的名称
    version="0.9.2",  # 包的版本
    author="maoyongfan",  # 作者
    author_email="maoyongfan@163.com",  # 作者邮件
    description="base lib",  # 包的简短描述
    long_description=open('README.md').read(),  # 读取 README 文件中的详细描述
    long_description_content_type="text/markdown",  # README 文件格式
    url="",  # 项目的 GitHub 或主页 URL
    packages=find_packages(),  # 自动查找包
    classifiers=[  # 包的分类信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 支持的 Python 版本
)
