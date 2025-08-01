# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/9 08:52

import paramiko


class SSHClient():
	def __init__(self, machine_ip, username="sansi", password="Sansi@1280"):
		self.client = paramiko.SSHClient()
		# self.client.load_system_host_keys()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加公钥
		self.client.connect(machine_ip, username=username, password=password, banner_timeout=2, auth_timeout=2,timeout=3)

	def execute_cmd(self, command_list):
		result_list = []
		for command in command_list:
			stdin, stdout, stderr = self.client.exec_command(command)

			stdout._set_mode('rb')

			temp = stdout.read()

			result_list.append(temp.decode("utf-8","ignore"))

		return result_list

	def close(self):
		if self.client:
			self.client.close()


if __name__ == '__main__':
	ssh_client = SSHClient("192.168.1.200")
	result = ssh_client.execute_cmd(["cd /home/sansi/xstudiopro&&cat xStudioPro.info"])
	print(len(result))
	# import re
	# versionObj = re.compile(r"\[version\]\s(.*)\s\s")
	# # print(result[0])
	# version = re.findall(versionObj,result[0])
	# platformObj = re.compile(r"\[platform\]\s(.*)\s\s")
	# platform = re.findall(platformObj,result[0])
	# print(version)
	# print(platform)
	# print(result)


