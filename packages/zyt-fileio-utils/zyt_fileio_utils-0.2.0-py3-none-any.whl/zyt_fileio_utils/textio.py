# -*- coding: utf-8 -*-
"""
Project Name: zyt_fileio_utils
File Created: 2025.07.14
Author: ZhangYuetao
File Name: textio.py
Update: 2025.08.01
"""

import ast
from pathlib import Path


def save_list_to_txt(txt_path, data_list, dedup=False, skip_empty=False, encoding="utf-8"):
    """
    将 list 存入 txt 文件，每个元素占一行，如果文件不存在则新建，存在则覆盖。

    :param txt_path: 保存的txt路径（str 或 Path）。
    :param data_list: 待保存的数据列表。
    :param dedup: 是否去重。
    :param skip_empty: 是否跳过空字符串。
    :param encoding: 文件编码。
    """
    _write_list_to_txt(txt_path, data_list, mode='w', dedup=dedup, skip_empty=skip_empty, encoding=encoding)


def add_list_to_txt(txt_path, data_list, dedup=False, skip_empty=False, encoding="utf-8"):
    """
    将 list 存入 txt 文件，每个元素占一行，如果文件不存在则新建，存在则追加。

    :param txt_path: 保存的txt路径（str 或 Path）。
    :param data_list: 待保存的数据列表。
    :param dedup: 是否去重。
    :param skip_empty: 是否跳过空字符串。
    :param encoding: 文件编码。
    """
    txt_path = Path(txt_path)
    mode = 'a' if txt_path.exists() else 'w'

    _write_list_to_txt(txt_path, data_list, mode, dedup=dedup, skip_empty=skip_empty, encoding=encoding)


def _write_list_to_txt(txt_path, data_list, mode='w', dedup=False, skip_empty=False, encoding="utf-8"):
    """
    将 list 存入 txt 文件，每个元素占一行。

    :param txt_path: 保存的txt路径（str 或 Path）。
    :param data_list: 待保存的数据列表。
    :param mode: 写入模式："w" 覆盖，"a" 追加。
    :param dedup: 是否去重。
    :param skip_empty: 是否跳过空字符串。
    :param encoding: 文件编码。
    """
    txt_path = Path(txt_path)
    txt_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if dedup:
            data_list = list(dict.fromkeys(data_list))
        
        if skip_empty:
            data_list = [x for x in data_list if str(x).strip()]

        with txt_path.open(mode=mode, encoding=encoding) as f:
            for item in data_list:
                f.write(str(item) + "\n")
    except TypeError as e:
        raise TypeError(f"数据类型错误，不能被写入文件：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def read_list_from_txt(txt_path, parse=False, encoding="utf-8"):
    """
    从 txt 文件读取 list，可选解析数据结构。

    :param txt_path: 读取的txt路径（str 或 Path）。
    :param parse: 是否解析数据结构，默认 False。
    :param encoding: 文件编码。
    :return: 读取的 list。
    """
    txt_path = Path(txt_path)

    if not txt_path.exists():
        raise FileNotFoundError(f"文件不存在：{txt_path}")
    
    try:
        with txt_path.open(mode="r", encoding=encoding) as f:
            lines = [line.strip() for line in f.readlines()]
            return [ast.literal_eval(line) for line in lines] if parse else lines
    except OSError as e:
        raise OSError(f"文件读取失败：{e}") from e
    except SyntaxError as e:
        raise SyntaxError(f"文件解析失败：{e}") from e
    except ValueError as e:
        raise ValueError(f"文件解析失败：{e}") from e
    

def save_text(txt_path, text, encoding="utf-8"):
    """
    保存纯文本内容，如果文件不存在则新建，存在则覆盖。

    :param txt_path: 保存路径（str 或 Path）。
    :param text: 字符串内容。
    :param encoding: 文件编码。
    """
    _write_text(txt_path, text, mode="w", encoding=encoding)


def add_text(txt_path, text, encoding="utf-8"):
    """
    保存纯文本内容，如果文件不存在则新建，存在则追加。

    :param txt_path: 保存路径（str 或 Path）。
    :param text: 字符串内容。
    :param encoding: 文件编码。
    """
    txt_path = Path(txt_path)
    mode = 'a' if txt_path.exists() else 'w'

    _write_text(txt_path, text, mode, encoding)


def _write_text(txt_path, text, mode="w", encoding="utf-8"):
    """
    保存纯文本内容，可指定写入模式（'w' 覆盖，'a' 追加等）。

    :param txt_path: 保存路径（str 或 Path）。
    :param text: 字符串内容。
    :param mode: 写入模式，默认覆盖写入 'w'。
    :param encoding: 文件编码。
    """
    txt_path = Path(txt_path)
    txt_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with txt_path.open(mode=mode, encoding=encoding) as f:
            f.write(text)
    except TypeError as e:
        raise TypeError(f"数据类型错误，不能被写入文件：{e}") from e
    except OSError as e:
        raise OSError(f"文件写入失败：{e}") from e


def read_text(txt_path, encoding="utf-8"):
    """
    读取整个文本文件为一个字符串。

    :param txt_path: 文本路径（str 或 Path）。
    :param encoding: 文件编码。
    :return: 文件内容字符串。
    """
    txt_path = Path(txt_path)

    if not txt_path.exists():
        raise FileNotFoundError(f"文件不存在：{txt_path}")
    
    try:
        with txt_path.open(mode="r", encoding=encoding) as f:
            return f.read()
    except OSError as e:
        raise OSError(f"文件读取失败：{e}") from e
