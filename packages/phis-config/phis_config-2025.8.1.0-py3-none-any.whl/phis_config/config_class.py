from .common import (
    get_raw_string,
    get_line_option,
    Path,
    get_line_option_as_bool,
    get_line_option_as_int,
)
import logging


class PhisConfig:
    def __init__(self, hospital_config_dir: Path):
        if not hospital_config_dir.exists():
            logging.warning(f'医院配置目录 {hospital_config_dir} 不存在，使用当前目录 {Path.cwd()}')
            self.hospital_config_dir = Path.cwd()
        else:
            self.hospital_config_dir = hospital_config_dir

    def get_config(self, file_relative_path: str) -> Path:
        return self.hospital_config_dir.joinpath(file_relative_path)

    def get_url(self) -> str:
        return get_raw_string(self.get_config('文档/admin.txt'), 1)

    def get_username(self) -> str:
        return get_raw_string(self.get_config('文档/admin.txt'), 2)

    def get_password(self) -> str:
        return get_raw_string(self.get_config('文档/admin.txt'), 3)

    def get_department_name(self) -> str:
        return get_raw_string(self.get_config('文档/admin.txt'), 4)

    def get_follow_up_start_date(self) -> str:
        return get_line_option(self.get_config('文档/admin.txt'), '随访新建起始时间')

    def get_follow_up_end_date(self) -> str:
        return get_line_option(self.get_config('文档/admin.txt'), '随访新建结束时间')

    def get_completed_count(self) -> int:
        return get_line_option_as_int(self.get_config('执行结果/env.txt'), '已完成数量')

    def get_organization_name(self) -> str:
        return get_line_option(self.get_config('执行结果/env.txt'), '机构名称')

    def use_other_doctor_records(self) -> bool:
        # 没有签约医生的门诊记录, 是否需要判别包含机构名称字样的其他医生的门诊记录
        return get_line_option_as_bool(
            self.get_config('执行结果/env.txt'), '没有签约医生的门诊'
        )

    def continue_save_if_already_done_test(self) -> bool:
        # 本季度已做过慢病随访，是否继续保存
        return get_line_option_as_bool(
            self.get_config('执行结果/env.txt'), '本季度已做过慢病随访，是否继续保存'
        )

    def no_diabetes_record_fasting_blood_sugar(self) -> bool:
        # 无糖尿病是否录入空腹血糖
        return get_line_option_as_bool(
            self.get_config('执行结果/env.txt'), '无糖尿病是否录入空腹血糖'
        )

    def introduction_medication_start_date(self) -> str:
        # 引入用药起始时间
        return get_line_option(self.get_config('执行结果/env.txt'), '引入用药起始时间')

    def introduction_medication_end_date(self) -> str:
        # 引入用药结束时间
        return get_line_option(self.get_config('执行结果/env.txt'), '引入用药结束时间')

    def get_line_option(self, file_relative_path: str, option_name: str) -> str:
        """
        获取指定配置文件中指定选项的值。
        """
        return get_line_option(self.get_config(file_relative_path), option_name)