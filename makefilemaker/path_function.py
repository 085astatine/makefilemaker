# -*- coding: utf-8 -*-

import sys
import os.path
import pathlib

def relative_to(path, start= None):
    """startを基準としたpathの相対パスを返す"""
    if start is None: start = os.path.curdir
    try:
        return pathlib.Path(os.path.relpath(str(path), str(start)))
    except ValueError as e:
        return path

def path_to_string(path, start= None):
    """pathlib.Pathを相対化しposix形式で文字列化"""
    #if not isinstance(path, pathlib.Path):
    #    message = ('path_to_string(path, start= None):'
    #               'path<{0}> is not pathlib.Path'.format(repr(path)))
    #    raise ValueError(message)
    return relative_to(path, start).as_posix()

def print_path(path):
    """pathlib.Pathを相対化しposix形式で文字列化したものをprintする"""
    print(path_to_string(path))

def path_sort(path):
    """pathをdirectory, basenameの順でsortする"""
    return (path.parent, path)

