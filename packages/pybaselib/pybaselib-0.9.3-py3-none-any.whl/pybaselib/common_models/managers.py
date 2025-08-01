# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/21 23:30

from django.db import models

class SoftDeleteManager(models.Manager):
    """自定义Manager，过滤掉已删除的数据"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
