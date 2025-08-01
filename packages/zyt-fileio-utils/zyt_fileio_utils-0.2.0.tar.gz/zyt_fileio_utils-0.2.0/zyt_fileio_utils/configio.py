# -*- coding: utf-8 -*-
"""
Project Name: zyt_fileio_utils
File Created: 2025.07.14
Author: ZhangYuetao
File Name: configio.py
Update: 2025.08.01
"""

from pathlib import Path

import zyt_fileio_utils.jsonio as jsonio
import zyt_fileio_utils.tomlio as tomlio
import zyt_fileio_utils.yamlio as yamlio


def save_dict_to_auto_ext(dict_path, data_dict, encoding="utf-8"):
    """
    自动根据文件扩展名将字典保存为JSON、TOML或YAML文件。

    :param dict_path: 保存路径（str 或 Path）。
    :param data_dict: 要保存的字典。
    :param encoding: 文件编码。
    """
    ext = Path(dict_path).suffix.lower()

    if ext == '.json':
        return jsonio.save_dict_to_json(dict_path, data_dict, encoding)
    elif ext == '.toml':
        return tomlio.save_dict_to_toml(dict_path, data_dict, encoding)
    elif ext in ['.yaml', '.yml']:
        return yamlio.save_dict_to_yaml(dict_path, data_dict, encoding)
    else:
        raise ValueError(f"不支持的配置文件格式: {ext}")
    

def add_dict_to_auto_ext(dict_path, update_dict, encoding="utf-8"):
    """
    自动根据文件扩展名向配置字典中添加或更新字段，如果文件不存在则新建。

    :param dict_path: 文件路径（str 或 Path）。
    :param update_dict: 要添加的键值对字典。
    :param encoding: 文件编码。
    """
    ext = Path(dict_path).suffix.lower()

    if ext == '.json':
        return jsonio.add_dict_to_json(dict_path, update_dict, encoding)
    elif ext == '.toml':
        return tomlio.add_dict_to_toml(dict_path, update_dict, encoding)
    elif ext in ['.yaml', '.yml']:
        return yamlio.add_dict_to_yaml(dict_path, update_dict, encoding)
    else:
        raise ValueError(f"不支持的配置文件格式: {ext}")


def read_dict_from_auto_ext(dict_path, default=None, strict=False, encoding="utf-8"):
    """
    自动根据文件扩展名加载配置文件，并与默认值递归合并。若非严格模式，读取失败将返回默认值。

    :param dict_path: 文件路径（str 或 Path）。
    :param default: 默认配置字典。
    :param strict: 是否严格模式，如果文件不存在或解析失败则抛出异常。
    :param encoding: 文件编码。
    :return: 合并后的配置字典。
    """
    ext = Path(dict_path).suffix.lower()

    if ext == '.json':
        return jsonio.read_dict_from_json(dict_path, default, strict, encoding)
    elif ext == '.toml':
        return tomlio.read_dict_from_toml(dict_path, default, strict, encoding)
    elif ext in ['.yaml', '.yml']:
        return yamlio.read_dict_from_yaml(dict_path, default, strict, encoding)
    else:
        raise ValueError(f"不支持的配置文件格式: {ext}")
    