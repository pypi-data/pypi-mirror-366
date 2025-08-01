# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/21 23:26

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    """自定义分页器"""
    page_size = 10  # 默认每页大小
    page_size_query_param = 'size'  # URL 中动态设置每页大小参数
    max_page_size = 100  # 最大分页大小
    page_query_param = 'page'  # URL 中的页码参数名

