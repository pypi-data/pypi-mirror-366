# -*- coding: utf-8 -*-
"""
Project Name: zyt_fileio_utils
File Created: 2025.07.31
Author: ZhangYuetao
File Name: yamlio.py
Update: 2025.08.01
"""

from pathlib import Path
from copy import deepcopy
from collections.abc import Mapping

import zyt_fileio_utils.utils as utils

try:
    import yaml
except ImportError:
    yaml = None


def save_dict_to_yaml(yaml_path, data_dict, encoding="utf-8"):
    """
    将 dict 保存为 YAML 文件。

    :param yaml_path: 保存路径（str 或 Path）。
    :param data_dict: 要保存的字典。
    :param encoding: 文件编码。
    """
    if yaml is None:
        raise ImportError("请先安装 PyYAML 库：pip install pyyaml")
    if not isinstance(data_dict, Mapping):
        raise TypeError("data_dict 参数必须是 Mapping 类型")

    yaml_path = Path(yaml_path)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with yaml_path.open(mode="w", encoding=encoding) as f:
            yaml.dump(data_dict, f, allow_unicode=True)
    except TypeError as e:
        raise TypeError(f"数据不能被 YAML 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e
    

def add_dict_to_yaml(yaml_path, update_dict, encoding="utf-8"):
    """
    向 YAML 文件中添加或更新字段，如果文件不存在则新建。

    :param yaml_path: YAML 文件路径（str 或 Path）。
    :param update_dict: 要添加的键值对字典。
    :param encoding: 文件编码。
    """
    if yaml is None:
        raise ImportError("请先安装 PyYAML 库：pip install pyyaml")
    if not isinstance(update_dict, Mapping):
        raise TypeError("default 参数必须是 Mapping 类型")

    yaml_path = Path(yaml_path)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取原始内容
    original = {}
    if yaml_path.exists():
        try:
            with yaml_path.open(mode="r", encoding=encoding) as f:
                original = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 文件解析失败：{e}") from e
        except OSError as e:
            raise OSError(f"打开文件失败：{e}") from e

    if not isinstance(original, Mapping):
        raise ValueError(f"YAML 数据解析结果不是 Mapping 类型，无法更新")

    # 合并更新
    merged = utils.recursive_merge_dicts(original, update_dict)

    # 保存更新后内容
    try:
        with yaml_path.open(mode="w", encoding=encoding) as f:
            yaml.dump(merged, f, allow_unicode=True)
    except TypeError as e:
        raise TypeError(f"数据不能被 YAML 序列化：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def read_dict_from_yaml(yaml_path, default=None, strict=False, encoding="utf-8"):
    """
    加载 YAML 配置文件，如果文件不存在或解析失败则使用默认配置，
    并递归补全缺失的键。

    :param yaml_path: YAML 文件路径（str 或 Path）。
    :param default: 默认配置字典。
    :param strict: 是否严格模式，如果文件不存在或解析失败则抛出异常。
    :param encoding: 文件编码。
    :return: 合并后的配置字典。
    """
    if default is None:
        default = {}

    if yaml is None:
        raise ImportError("请先安装 PyYAML 库：pip install pyyaml")
    if not isinstance(default, Mapping):
        raise TypeError("default 参数必须是 Mapping 类型")

    yaml_path = Path(yaml_path)

    if strict:
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML 文件不存在：{yaml_path}")
    
        try:
            with yaml_path.open(mode="r", encoding=encoding) as f:
                loaded = yaml.safe_load(f)

            if not isinstance(loaded, Mapping):
                raise ValueError(f"解析结果不是 Mapping 类型")
            
            return utils.recursive_merge_dicts(default, loaded)
        
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 文件解析失败：{e}") from e
        except OSError as e:
            raise OSError(f"打开 YAML 文件失败：{e}") from e
    
    if not yaml_path.exists():
        return deepcopy(default)
    
    try:
        with yaml_path.open(mode="r", encoding=encoding) as f:
            loaded = yaml.safe_load(f)
        if isinstance(loaded, Mapping):
            return utils.recursive_merge_dicts(default, loaded)
    except Exception:
        pass

    return deepcopy(default)
