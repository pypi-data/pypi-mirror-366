# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/21 23:18
from django.db import models


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    status = models.CharField(max_length=20, default="active", verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        verbose_name = "基础模型"
        verbose_name_plural = "基础模型"

    def soft_delete(self):
        """逻辑删除"""
        self.is_deleted = True
        self.save()

    def restore(self):
        """恢复逻辑删除的记录"""
        self.is_deleted = False
        self.save()


class UserProfile(BaseModel):
    username = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.username

    class Meta:
        abstract = True


class BugRecord(BaseModel):
    """
            bug状态有:
                state:
                    opened 打开,
                    closed 关闭
                labels:
                    Fixed
                    stage::验证  ['foundByAutoTest', 'priority::2', 'severity::2', 'stage::验证', 'type::bug']
                    closed::done
                    Rejected
                    Reopen

    """
    testcase = models.CharField(max_length=100, verbose_name="testcase")
    bug_id = models.BigIntegerField(verbose_name="iid")
    project_id = models.BigIntegerField(verbose_name="project_id")
    bug_title = models.CharField(max_length=100, verbose_name="bug_title")
    reopen_num = models.BigIntegerField(default=0, verbose_name="reopen_num")

    class Meta:
        abstract = True

