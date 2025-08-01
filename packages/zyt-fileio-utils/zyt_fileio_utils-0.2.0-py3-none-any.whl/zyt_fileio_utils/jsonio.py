# -*- coding: utf-8 -*-
"""
Project Name: zyt_fileio_utils
File Created: 2025.07.14
Author: ZhangYuetao
File Name: jsonio.py
Update: 2025.07.31
"""

import json
from pathlib import Path
from copy import deepcopy
from collections.abc import Mapping

import zyt_fileio_utils.utils as utils


def save_dict_to_json(json_path, data_dict, encoding="utf-8"):
    """
    将 dict 保存为 JSON 文件。

    :param json_path: 保存路径（str 或 Path）。
    :param data_dict: 要保存的字典。
    :param encoding: 文件编码。
    """
    if not isinstance(data_dict, Mapping):
        raise TypeError("data_dict 参数必须是 Mapping 类型")
    
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with json_path.open(mode="w", encoding=encoding) as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
    except TypeError as e:
        raise TypeError(f"数据不能被 JSON 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def add_dict_to_json(json_path, update_dict, encoding="utf-8"):
    """
    向 JSON 文件中添加或更新字段，如果文件不存在则新建。

    :param json_path: JSON 文件路径（str 或 Path）。
    :param update_dict: 要添加的键值对字典。
    :param encoding: 文件编码。
    """
    if not isinstance(update_dict, Mapping):
        raise TypeError(f"update_dict 参数必须是 Mapping 类型")
    
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取原始内容
    original = {}
    if json_path.exists():
        try:
            with json_path.open(mode="r", encoding=encoding) as f:
                original = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON 文件解析失败：{e.msg}", e.doc, e.pos) from e
        except OSError as e:
            raise OSError(f"打开文件失败：{e}") from e

    if not isinstance(original, Mapping):
        raise ValueError(f"JSON 内容不是字典类型（Mapping），无法更新")

    # 合并更新
    merged = utils.recursive_merge_dicts(original, update_dict)

    # 保存更新后内容
    try:
        with json_path.open(mode="w", encoding=encoding) as f:
            json.dump(merged, f, ensure_ascii=False, indent=4)
    except TypeError as e:
        raise TypeError(f"数据不能被 JSON 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def read_dict_from_json(json_path, default=None, strict=False, encoding="utf-8"):
    """
    加载 JSON 文件为 dict，如果文件不存在或解析失败则使用默认配置，
    并递归补全缺失的键。

    :param json_path: JSON 文件路径（str 或 Path）。
    :param default: 默认配置。
    :param strict: 是否严格模式，如果文件不存在或解析失败则抛出异常。
    :param encoding: 文件编码。
    :return: 合并后的配置字典。
    """
    if default is None:
        default = {}

    if not isinstance(default, Mapping):
        raise TypeError("default 参数必须是 Mapping 类型")
    
    json_path = Path(json_path)

    if strict:
        if not json_path.exists():
            raise FileNotFoundError(f"JSON 文件不存在：{json_path}")

        try:
            with json_path.open(mode="r", encoding=encoding) as f:
                loaded = json.load(f)

            if not isinstance(loaded, Mapping):
                raise ValueError(f"解析结果不是 Mapping 类型")
            
            return utils.recursive_merge_dicts(default, loaded)
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON 文件解析失败：{e.msg}", e.doc, e.pos) from e
        except OSError as e:
            raise OSError(f"打开 JSON 文件失败：{e}") from e
    
    if not json_path.exists():
        return deepcopy(default)

    try:
        with json_path.open(mode="r", encoding=encoding) as f:
            loaded = json.load(f)
        if isinstance(loaded, Mapping):
            return utils.recursive_merge_dicts(default, loaded)
    except Exception:
        pass

    return deepcopy(default)


def save_json(json_path, data, encoding="utf-8"):
    """
    将任意合法 JSON 数据保存到文件。

    :param json_path: 保存路径（str 或 Path）。
    :param data: 任意合法 JSON 类型的数据。
    :param encoding: 文件编码。
    """
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with json_path.open(mode="w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except TypeError as e:
        raise TypeError(f"数据不能被 JSON 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def read_json(json_path, encoding="utf-8"):
    """
    从 JSON 文件中读取数据（支持任意类型）。

    :param json_path: JSON 文件路径（str 或 Path）。
    :param encoding: 文件编码。
    :return: JSON 解析后的数据。
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON 文件不存在：{json_path}") from e
    
    try:
        with json_path.open(mode="r", encoding=encoding) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON 文件解析失败：{e.msg}", e.doc, e.pos) from e
    except OSError as e:
        raise OSError(f"打开 JSON 文件失败：{e}") from e
