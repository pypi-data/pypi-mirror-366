# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/26 14:54
import logging
from functools import wraps


def save_bug(old_version: bool, testcase: str, bug_id: int, project_id: int, bug_title: str, controllerInfo,
             NtcipBugRecordeSerializer):
    controllerInfoDict = controllerInfo._asdict()
    controllerInfoDict.update({'old_version': old_version,
                               'status': 'opened',
                               'testcase': testcase,
                               'bug_id': bug_id,
                               'project_id': project_id,
                               'bug_title': bug_title
                               })
    print(controllerInfoDict)
    serializer = NtcipBugRecordeSerializer(data=controllerInfoDict)
    if serializer.is_valid():
        result = serializer.save()
        print("Bug created:", serializer.validated_data, result)
    else:
        print("Invalid data:", serializer.errors)


def deal_bug(bug_type="ntcip"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            report, case_status, case_infos = func(*args, **kwargs)
            if not case_status:
                (bug_title, bug_description, priority, testcase, version,
                 controllerInfo, issue, developer_id, default_project_id,
                 NtcipBugRecord, NtcipBugRecordeSerializer, single_case_log, debug) = case_infos
                if bug_type == "ntcip":
                    if version == "old":
                        print('old')
                        old_version = True
                        ntcip_bug_records = NtcipBugRecord.objects.filter(bug_title=bug_title, testcase=testcase,
                                                                          old_version=True,
                                                                          net_ntcip_version__lte=controllerInfo.net_ntcip_version)
                    else:
                        old_version = False
                        ntcip_bug_records = NtcipBugRecord.objects.filter(bug_title=bug_title, testcase=testcase,
                                                                          old_version=False,
                                                                          net_ntcip_version__lte=controllerInfo.net_ntcip_version)
                    print(f"ntcip_bug_records: {ntcip_bug_records}")
                    if ntcip_bug_records.exists():
                        logging.info(f"已存在bug")
                        record = ntcip_bug_records.first()
                        if record.status == "Rejected":
                            return
                        elif record.status == "closed":
                            # reopen bug
                            issue.reopen_bug(record.project_id, record.bug_id,
                                             f"{controllerInfo._asdict()}\n\n重现此问题,重新打开此Bug")
                            record.status = "opened"
                            record.reopen_num += 1
                            record.save()
                            issue.add_bug_label(record.project_id, record.bug_id, ["Reopen"])
                            issue.remove_bug_label(record.project_id, record.bug_id, ["closed::done"])
                        else:
                            state, labels = issue.get_bug_status(record.project_id, record.bug_id)
                            if state == "closed":
                                issue.reopen_bug(record.project_id, record.bug_id,
                                                 f"{controllerInfo._asdict()}\n\n重现此问题,重新打开此Bug")
                                record.status = "opened"
                                record.reopen_num += 1
                                record.save()
                                issue.add_bug_label(record.project_id, record.bug_id, ["Reopen"])
                                issue.remove_bug_label(record.project_id, record.bug_id, ["closed::done"])
                            elif state == "opened":
                                return
                            elif "Fixed" in labels or "stage::验证" in labels:
                                issue.add_bug_label(record.project_id, record.bug_id, ["Reopen"])
                                issue.remove_bug_label(record.project_id, record.bug_id,
                                                       ["Fixed", "stage::验证", "closed::done"])
                                issue.add_comment_to_issue(
                                    record.project_id, record.bug_id,
                                    f"{controllerInfo._asdict()}\n\n重现此问题")
                                record.status = "opened"
                                record.reopen_num += 1
                                record.save()
                            elif "Rejected" in labels:
                                record.status = "Rejected"
                                record.save()
                            else:
                                pass
                    else:
                        logging.info(f"未有相同bug")
                        if debug != 'true':
                            issue_iid, project_id = issue.create_bug(bug_title, bug_description, priority, version,
                                                                     testcase,
                                                                     controllerInfo,
                                                                     developer_id, default_project_id, single_case_log)

                            save_bug(old_version, testcase, issue_iid, project_id,
                                     bug_title, controllerInfo, NtcipBugRecordeSerializer)

            return report

        return wrapper

    return decorator
