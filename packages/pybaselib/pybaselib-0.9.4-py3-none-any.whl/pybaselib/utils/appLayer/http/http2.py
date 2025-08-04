# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/24 17:36
import httpx


class Http2Client:
    def __init__(self, base_url: str, timeout: int = 10, headers=None):
        """
        初始化 HttpClient 类。

        :param base_url: API 的基础 URL
        :param timeout: 请求超时时间，单位为秒
        """
        self.base_url = base_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.client = httpx.Client(base_url=base_url, timeout=timeout, verify=False)

    def remove_header(self, key: str):
        self.headers.pop(key, None)

    def get(self, endpoint: str, params: dict = None, headers: dict = None) -> dict:
        """
        发送 GET 请求。

        :param endpoint: API 端点
        :param params: 查询参数
        :param headers: 请求头
        :return: JSON 响应
        """
        response = self.client.get(endpoint, params=params, headers=self._merge_headers(headers))
        response.raise_for_status()  # 检查请求是否成功
        try:
            return response.json()
        except ValueError:
            return response.text

    def post(self, endpoint: str, data: dict = None, json: dict = None, files=None, headers: dict = None) -> dict:
        """
        发送 POST 请求。

        :param files: 以二进制形式读取，用于传输文件内容
        :param endpoint: API 端点
        :param data: 表单数据
        :param json: JSON 数据
        :param headers: 请求头
        :return: JSON 响应
        """
        response = self.client.post(endpoint, data=data, json=json, files=files, headers=self._merge_headers(headers))
        response.raise_for_status()
        return self._handle_response(response)

    def put(self, endpoint: str, data: dict = None, json: dict = None,headers: dict = None) -> dict:
        """
        发送 PUT 请求。

        :param endpoint: API 端点
        :param data: 表单数据
        :param headers: 请求头
        :return: JSON 响应
        """
        response = self.client.put(endpoint, data=data, json=json, headers=self._merge_headers(headers))
        response.raise_for_status()
        return self._handle_response(response)

    def delete(self, endpoint: str, headers: dict = None) -> dict:
        """
        发送 DELETE 请求。

        :param endpoint: API 端点
        :param headers: 请求头
        :return: JSON 响应
        """
        response = self.client.delete(endpoint, headers=self._merge_headers(headers))
        response.raise_for_status()
        return response.json()

    def close(self):
        """
        关闭 HTTP 客户端。
        """
        self.client.close()

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
        # print(f"self.headers: {self.headers}")
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
