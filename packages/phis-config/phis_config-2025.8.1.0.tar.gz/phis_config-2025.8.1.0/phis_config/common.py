from pathlib import Path
import logging
from typing import Union


def check_exists(file: Union[str, Path]) -> None:
    file_path = Path(file).resolve()
    if not file_path.exists():
        logging.fatal(f'文件不存在，请检查文件路径是否正确. {file_path}')
        exit(-1)


def env_write(file_path, line_number, content):
    # 读取文件并将其内容存储到列表中
    check_exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 修改指定行的内容（注意列表是从0开始索引的）
    if 1 <= line_number <= len(lines):
        lines[line_number - 1] = content + '\n'
    elif line_number > len(lines):
        # 如果指定的行数超出了文件的总行数，将在末尾添加新行
        lines.extend(['\n'] * (line_number - len(lines) - 1))
        lines.append(content + '\n')

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def get_line_option(
    env_file: Path, line_number_or_start_string: Union[int, str]
) -> str:
    """
    获取配置文件中第N行数据的值 (格式: KEY:VALUE)
    或者：获取配置文件中以XXX开头的行的值
    """
    check_exists(env_file)
    if isinstance(line_number_or_start_string, int):
        config_content = env_file.read_text(encoding='utf8').split('\n')
        line_number_in_file = line_number_or_start_string - 1  # 实际行数从0开始
        if line_number_in_file < 0 or line_number_in_file >= len(config_content):
            logging.fatal('配置文件行数错误！', line_number_or_start_string)
        return (
            config_content[line_number_in_file].replace('：', ':').split(':')[1].strip()
        )
    elif isinstance(line_number_or_start_string, str):
        config_content = env_file.read_text(encoding='utf8').split('\n')
        for line in config_content:
            if line.startswith(line_number_or_start_string):
                return line.replace('：', ':').split(':')[1].strip()
        logging.fatal(f'配置文件中没有找到以"{line_number_or_start_string}"开头的行')

    else:
        logging.error('line_number_or_start_string 必须是 int 或 str 类型')


def get_line_option_as_int(
    env_file: Path, line_number_or_start_string: Union[int, str]
) -> int:
    """
    获取配置文件中第N行数据的值 (格式: KEY:VALUE) 并转换为整数
    """
    value = get_line_option(env_file, line_number_or_start_string)
    try:
        return int(value)
    except ValueError:
        logging.fatal(f'无法将 "{value}" 转换为整数')
        return 0  # 或者抛出异常，根据需要处理


def get_line_option_as_bool(
    env_file: Path, line_number_or_start_string: Union[int, str]
) -> bool:
    """
    获取配置文件中第N行数据的值 (格式: KEY:VALUE) 并转换为布尔值
    """
    value = get_line_option(env_file, line_number_or_start_string)
    if value.lower() in ['是', 'true', '1']:
        return True
    elif value.lower() in ['否', 'false', '0']:
        return False
    else:
        logging.fatal(f'无法将 "{value}" 转换为布尔值')
        return False  # 或者抛出异常，根据需要处理


def get_raw_string(env_file, line_number: int) -> str:
    "获取配置文件中第N行数据, 原字符串"
    check_exists(env_file)
    config_content = env_file.read_text(encoding='utf8').split('\n')
    line_number_in_file = line_number - 1  # 实际行数从0开始
    return config_content[line_number_in_file].strip()


def 重置已完成数量():
    env_write('执行结果/env.txt', 3, f'已完成数量:0')
