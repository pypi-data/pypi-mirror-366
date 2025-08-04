# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/24 17:07
import json
import os
import logging
from pybaselib.utils.appLayer.http import Http2Client, HttpClient


class Issue:
    def __init__(self, token, host):
        self.token = token
        self.host = host

        self.headers = {
            "PRIVATE-TOKEN": token,
            "Content-Type": "application/json"
        }

        self.gitlab_client = Http2Client(host,
                                         headers=self.headers)

    def uploads_alt(self, project_id: int, single_case_log: str):
        uri = f"api/v4/projects/{project_id}/uploads"
        self.gitlab_client.remove_header("Content-Type")
        with open(single_case_log, 'rb') as f:
            files = {'file': (os.path.basename(single_case_log), f)}
            upload_resp = self.gitlab_client.post(uri, files=files)
            #{'id': 94399, 'alt': 'single_case.log', 'url': '/uploads/42b93d51950766e9412093269c85aa09/single_case.log', 'full_path': '/-/project/1911/uploads/42b93d51950766e9412093269c85aa09/single_case.log', 'markdown': '[single_case.log](/uploads/42b93d51950766e9412093269c85aa09/single_case.log)'}
        markdown_link = upload_resp['markdown']
        filename = upload_resp['alt']
        download_url = f"{self.host}{upload_resp['full_path']}"
        logging.info(f"附件信息: {download_url}, {filename}")
        logging.debug(upload_resp)
        return download_url, filename

    def create_bug(self, bug_title: str, bug_description: str, priority: str, version: str, testcase: str,
                   controllerInfo, developer_id: list, project_id: int, single_case_log: str):
        uri = f"api/v4/projects/{project_id}/issues"
        download_url, filename = self.uploads_alt(project_id, single_case_log)
        if version == "old":
            gitlab_title = f"[Bug_自动提交] [旧版] [{controllerInfo.net_ntcip_version}] {bug_title}"
        else:
            gitlab_title = f"[Bug_自动提交] [新版] [{controllerInfo.net_ntcip_version}] {bug_title}"

        gitlab_description = f"# 前置条件 \n\n{controllerInfo._asdict()} \n\n # bug描述 \n\n {bug_description} \n\n # 对应自动化Case名称 \n\n{testcase} \n\n # 附件信息 \n\n 执行记录请参考附件：[{filename}]({download_url}) \n\n"

        if priority == "P1":
            lables = "type::bug,foundByAutoTest,priority::1,severity::1"
        elif priority == "P3":
            lables = "type::bug,foundByAutoTest,priority::3,severity::3"
        else:
            lables = "type::bug,foundByAutoTest,priority::2,severity::2"

        post_data = {
            "title": gitlab_title,
            "description": gitlab_description,
            "labels": lables,
            "assignee_ids": developer_id  # 车保康
        }
        logging.debug(f"创建issue_data: \n{json.dumps(post_data, indent=4)}")
        # gitlab_client = Http2Client(host,
        #                             headers=self.headers)
        gitlab_response = self.gitlab_client.post(uri, json=post_data)
        logging.debug(
            gitlab_response)  # {'id': 39974, 'iid': 178, 'project_id': 1911, 'title':...,'state': 'opened', 'closed_at': None, 'closed_by': None, 'labels': ['foundByAutoTest', 'priority::1', 'severity::1', 'type::bug']
        return gitlab_response.get("iid"), gitlab_response.get("project_id")

    def get_issue_info(self, project_id, issue_iid):
        uri = f"api/v4/projects/{project_id}/issues/{issue_iid}"
        gitlab_response = self.gitlab_client.get(uri)
        print(
            gitlab_response)  # {'id': 39974, 'iid': 178, 'project_id': 1911, 'state': 'closed', 'closed_at': '2025-02-24T19:35:34.165+08:00', 'closed_by': {'id': 306, 'username': 'maoyongfan','labels': ['foundByAutoTest', 'priority::1', 'severity::1', 'type::bug']
        return gitlab_response.get("state"), gitlab_response.get("labels")

    def get_bug_status(self, project_id, issue_iid):
        return self.get_issue_info(project_id, issue_iid)

    def update_issue_lables(self, project_id, issue_iid, lables):
        uri = f"api/v4/projects/{project_id}/issues/{issue_iid}"
        updated_labels = {
            "labels": lables
        }
        print(updated_labels)
        gitlab_response = self.gitlab_client.put(uri, json=updated_labels)
        print(gitlab_response)

    def add_bug_label(self, project_id, issue_iid, label_list):
        state, labels = self.get_issue_info(project_id, issue_iid)
        for label in label_list:
            labels.append(label)
        self.update_issue_lables(project_id, issue_iid, labels)

    def remove_bug_label(self, project_id, issue_iid, label_list):
        state, labels = self.get_issue_info(project_id, issue_iid)
        for label in label_list:
            if label in labels:
                labels.remove(label)
        self.update_issue_lables(project_id, issue_iid, labels)

    def close_reopen_issue(self, project_id, issue_iid, status="close"):
        """
        关闭或打开issue
        :param project_id:
        :param issue_iid:
        :param status:
        :return:
        """
        uri = f"api/v4/projects/{project_id}/issues/{issue_iid}"
        data = {
            "state_event": status
        }
        gitlab_response = self.gitlab_client.put(uri, json=data)
        print(gitlab_response)

    def add_comment_to_issue(self, project_id, issue_iid, comment):
        uri = f"api/v4/projects/{project_id}/issues/{issue_iid}/notes"
        data = {
            "body": comment
        }
        gitlab_response = self.gitlab_client.post(uri, json=data)
        print(gitlab_response)
        return gitlab_response.get("noteable_iid")

    def close_bug(self, project_id, issue_iid, comment):
        if isinstance(self.add_comment_to_issue(project_id, issue_iid, comment), int):
            self.close_reopen_issue(project_id, issue_iid)

    def reopen_bug(self, project_id, issue_iid, comment):
        if isinstance(self.add_comment_to_issue(project_id, issue_iid, comment), int):
            self.close_reopen_issue(project_id, issue_iid, status="reopen")


if __name__ == "__main__":
    issue = Issue("glpat-v-G528C4BYfeXzgXphhm", "https://git.sansi.net:6101")
    issue.uploads_alt(1911,"/Users/maoyongfan/self/code/pytest/AppNtcipTest/logs/single_case.log")
    # issue.get_issue_info(1911,173)
    # issue.close_bug(1911,173,"test")
    # issue.close_issue(1911,173)
    # issue.reopen_bug(1911,173)
    # issue.add_bug_label(1911,180,["Reopen"])
    # issue.remove_bug_label(1911,180,["Reopen"])
