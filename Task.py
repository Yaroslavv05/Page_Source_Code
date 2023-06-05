import uuid
import json
from enum import Enum


class Task(object):
    ID: str = uuid.UUID(int=0).__str__()
    Uri: str = ""
    Page_Source: str = ""

    # CAPTCHA fields path's
    check_box_xpath: str = ""

    captcha_check_url_pattern: str = ""
    rep_xpath: str = ""
    submit_btn_xpath: str = ""

    captcha_img_xpath: str = ""

    def __init__(self, uri, check_box_xpath, captcha_check_url_pattern, rep_xpath, submit_btn_xpath,
                 captcha_img_xpath):
        self.ID = uuid.uuid4().__str__()
        self.Uri = uri
        self.check_box_xpath = check_box_xpath
        self.captcha_check_url_pattern = captcha_check_url_pattern
        self.rep_xpath = rep_xpath
        self.submit_btn_xpath = submit_btn_xpath
        self.captcha_img_xpath = captcha_img_xpath

    @staticmethod
    def from_json(json_data: str):
        return json.loads(json_data, object_hook=lambda d: Task(d['Uri'], d['check_box_xpath'],
                                                                d['captcha_check_url_pattern'], d['rep_xpath'],
                                                                d['submit_btn_xpath'], d['captcha_img_xpath']))


class TaskState(Enum):
    New = "New"
    InProgress = "InProgress"
    Completed = "Completed"
    Requested = "Requested"


class TaskContainerObj(object):
    task: Task
    taskState: TaskState

    def __init__(self, task: Task):
        self.task = task
        self.taskState = TaskState.New
