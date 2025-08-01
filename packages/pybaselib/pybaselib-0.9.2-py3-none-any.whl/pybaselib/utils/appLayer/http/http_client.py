# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/24 15:55
import requests


class HttpClient:
    def __init__(self, base_url, headers=None):
        """
        初始化 HTTP 客户端
        :param base_url: 基础 URL
        :param headers: 默认请求头
        """
        self.base_url = base_url
        self.headers = headers or {"Content-Type": "application/json"}

    def get(self, endpoint, params=None, headers=None):
        """
        发送 GET 请求
        :param endpoint: API 接口路径
        :param params: 查询参数
        :param headers: 请求头
        :return: 响应对象
        """
        url = self._build_url(endpoint)
        response = requests.get(url, params=params, headers=self._merge_headers(headers))
        return self._handle_response(response)

    def post(self, endpoint, data=None, json=None, headers=None):
        """
        发送 POST 请求
        :param endpoint: API 接口路径
        :param data: 表单数据
        :param json: JSON 数据
        :param headers: 请求头
        :return: 响应对象
        """
        url = self._build_url(endpoint)
        response = requests.post(url, data=data, json=json, headers=self._merge_headers(headers))
        return self._handle_response(response)

    def put(self, endpoint, data=None, json=None, headers=None):
        """
        发送 PUT 请求
        :param endpoint: API 接口路径
        :param data: 表单数据
        :param json: JSON 数据
        :param headers: 请求头
        :return: 响应对象
        """
        url = self._build_url(endpoint)
        response = requests.put(url, data=data, json=json, headers=self._merge_headers(headers))
        return self._handle_response(response)

    def delete(self, endpoint, headers=None):
        """
        发送 DELETE 请求
        :param endpoint: API 接口路径
        :param headers: 请求头
        :return: 响应对象
        """
        url = self._build_url(endpoint)
        response = requests.delete(url, headers=self._merge_headers(headers))
        return self._handle_response(response)

    def _build_url(self, endpoint):
        """
        构建完整的 URL
        :param endpoint: API 接口路径
        :return: 完整 URL
        """
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _merge_headers(self, headers):
        """
        合并默认请求头和自定义请求头
        :param headers: 自定义请求头
        :return: 合并后的请求头
        """
        if headers:
            merged_headers = self.headers.copy()
            merged_headers.update(headers)
            return merged_headers
        print(f"self.headers: {self.headers}")
        return self.headers

    @staticmethod
    def _handle_response(response):
        """
        处理 HTTP 响应
        :param response: 响应对象
        :return: 响应内容或错误信息
        """
        if response.status_code // 100 == 2:  # 成功的响应
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            response.raise_for_status()
