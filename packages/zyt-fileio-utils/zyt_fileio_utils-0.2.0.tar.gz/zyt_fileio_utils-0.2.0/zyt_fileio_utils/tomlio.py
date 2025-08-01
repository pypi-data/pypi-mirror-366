# -*- coding: utf-8 -*-
"""
Project Name: zyt_fileio_utils
File Created: 2025.07.31
Author: ZhangYuetao
File Name: tomlio.py
Update: 2025.08.01
"""

from pathlib import Path
from copy import deepcopy
from collections.abc import Mapping

import zyt_fileio_utils.utils as utils

try:
    import toml
except ImportError:
    toml = None


def save_dict_to_toml(toml_path, data_dict, encoding="utf-8"):
    """
    将 dict 保存为 TOML 文件。

    :param toml_path: 保存路径（str 或 Path）。
    :param data_dict: 要保存的字典。
    :param encoding: 文件编码。
    """
    if toml is None:
        raise ImportError("请先安装 toml 库：pip install toml")
    if not isinstance(data_dict, Mapping):
        raise TypeError("data_dict 参数必须是 Mapping 类型")

    toml_path = Path(toml_path)
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with toml_path.open(mode="w", encoding=encoding) as f:
            toml.dump(data_dict, f)
    except TypeError as e:
        raise TypeError(f"数据不能被 TOML 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def add_dict_to_toml(toml_path, update_dict, encoding="utf-8"):
    """
    向 TOML 文件中添加或更新字段，如果文件不存在则新建。

    :param toml_path: TOML 文件路径（str 或 Path）。
    :param update_dict: 要添加的键值对字典。
    :param encoding: 文件编码。
    """
    if toml is None:
        raise ImportError("请先安装 toml 库：pip install toml")
    if not isinstance(update_dict, Mapping):
        raise TypeError("update_dict 参数必须是 Mapping 类型")

    toml_path = Path(toml_path)
    toml_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取原始内容
    original = {}
    if toml_path.exists():
        try:
            with toml_path.open(mode="r", encoding=encoding) as f:
                original = toml.load(f)
        except toml.TomlDecodeError as e:
            raise toml.TomlDecodeError(f"TOML 文件解析失败：{e.msg}", e.doc, e.pos) from e
        except OSError as e:
            raise OSError(f"打开文件失败：{e}") from e

    if not isinstance(original, Mapping):
        raise ValueError(f"TOML 数据解析结果不是 Mapping 类型，无法更新")

    # 合并更新
    merged = utils.recursive_merge_dicts(original, update_dict)

    # 保存更新后内容
    try:
        with toml_path.open(mode="w", encoding=encoding) as f:
            toml.dump(merged, f)
    except TypeError as e:
        raise TypeError(f"数据不能被 TOML 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e.strerror}") from e


def read_dict_from_toml(toml_path, default=None, strict=False, encoding="utf-8"):
    """
    加载 TOML 配置文件，如果文件不存在或解析失败则使用默认配置，
    并递归补全缺失的键。

    :param toml_path: TOML 文件路径（str 或 Path）。
    :param default: 默认配置字典。
    :param strict: 是否严格模式，如果文件不存在或解析失败则抛出异常。
    :param encoding: 文件编码。
    :return: 合并后的配置字典。
    """
    if default is None:
        default = {}

    if toml is None:
        raise ImportError("请先安装 toml 库：pip install toml")
    if not isinstance(default, Mapping):
        raise TypeError("default 参数必须是 Mapping 类型")

    toml_path = Path(toml_path)

    if strict:
        if not toml_path.exists():
            raise FileNotFoundError(f"TOML 文件不存在：{toml_path}")
    
        try:
            with toml_path.open(mode="r", encoding=encoding) as f:
                loaded = toml.load(f)

            if not isinstance(loaded, Mapping):
                raise ValueError(f"解析结果不是 Mapping 类型")
            
            return utils.recursive_merge_dicts(default, loaded)
        
        except toml.TomlDecodeError as e:
            raise toml.TomlDecodeError(f"TOML 文件解析失败：{e.msg}", e.doc, e.pos) from e
        except OSError as e:
            raise OSError(f"打开 TOML 文件失败：{e}") from e
    
    if not toml_path.exists():
        return deepcopy(default)
    
    try:
        with toml_path.open(mode="r", encoding=encoding) as f:
            loaded = toml.load(f)
        if isinstance(loaded, Mapping):
            return utils.recursive_merge_dicts(default, loaded)
    except Exception:
        pass

    return deepcopy(default)
