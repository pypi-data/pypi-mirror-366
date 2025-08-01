"""
程序配置文件解析
"""

from pathlib import Path
from .common import get_line_option, get_raw_string


class ProgramConfig:
    """
    程序配置文件解析
    """

    def __init__(self, path):
        self.env_file = Path(path)

    @property
    def 已完成数量(self):
        return get_line_option(self.env_file, 3)

    @property
    def 机构名称(self):
        return get_line_option(self.env_file, 5)

    @property
    def continue_save_if_already_done_test(self):
        "本季度已做过慢病随访，是否继续保存"
        return get_line_option(self.env_file, 6)

    @property
    def 无糖尿病是否录入空腹血糖(self):
        return get_line_option(self.env_file, 7)

    @property
    def 引入用药起始时间(self):
        return get_line_option(self.env_file, 8)

    @property
    def 引入用药结束时间(self):
        return get_line_option(self.env_file, 9)


class AdminConfig1:
    def __init__(self, path):
        self.env_file = Path(path)

    @property
    def 随访新建起始时间(self):
        return get_line_option(self.env_file, 5)

    @property
    def 随访新建结束时间(self):
        return get_line_option(self.env_file, 6)

    @property
    def 登录网址(self):
        return get_raw_string(self.env_file, 1)

    @property
    def 登录用户名(self):
        return get_raw_string(self.env_file, 2)

    @property
    def 登录密码(self):
        return get_raw_string(self.env_file, 3)

    @property
    def 登录科室名称(self):
        return get_raw_string(self.env_file, 4)


Config = ProgramConfig('执行结果/env.txt')
"""执行结果配置"""

AdminConfig = AdminConfig1('文档/admin.txt')
"""Admin配置 （随访新建起始时间，随访新建结束时间）"""
