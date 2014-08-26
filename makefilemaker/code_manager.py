# -*- coding: utf-8 -*-

import re, pathlib
from   collections import namedtuple

class CodeDependence(namedtuple(
'CodeDependence', ('code_path', 'include_files', 'include_libs'))):
    """各コードの依存性
    code_name     : コード名
    include_files : #include "..." 
    include_libs  : #include <...>
    """
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('code_path    :{0}'.format(self.code_path))
        piece.append('include_files:')
        piece.extend('  {0}'.format(file) for file in self.include_files)
        piece.append('include_libs :')
        piece.append('  {0}'.format(', '.join(self.include_libs)))
        return '\n'.join(piece)

def check_dependence(source_path):
    # 検出したヘッダファイル, ライブラリ
    include_files = []
    include_libs  = []
    # 正規表現
    include_file_regex = re.compile('#include( +|)"(?P<header>.+)"')
    include_lib_regex  = re.compile('#include( +|)<(?P<header>.+)>')
    with source_path.open(encoding= 'utf-8', newline= '') as source_file:
        for line in source_file:
            # match
            include_file_match = include_file_regex.search(line)
            include_lib_match  = include_lib_regex.search(line)
            # include_file判定
            if include_file_match:
                # 絶対パス化
                header_path = source_path.parent.joinpath(
                    include_file_match.group('header')).resolve()
                include_files.append(header_path)
            # include_lib判定
            elif include_lib_match:
                include_libs.append(include_lib_match.group('header'))
    #出力
    return CodeDependence(source_path,
                          tuple(include_files),
                          tuple(include_libs))

def check_target(checked_list, dependence_list):
    # 検出されたファイル
    detected_list = set(file
        for checked_file in checked_list
        for file         in dependence_list[checked_file].include_files)
    # 差を出力
    return detected_list.difference(checked_list)

def full_dependence(source_path, dependence_list):
    # 初期設定
    include_files = set(dependence_list[source_path].include_files)
    include_libs  = set(dependence_list[source_path].include_libs)
    # 探索済みリスト
    checked_files = {source_path}
    target_files  = check_target(checked_files, dependence_list)
    while len(target_files) != 0:
        for target in target_files:
            include_files.update(dependence_list[target].include_files)
            include_libs .update(dependence_list[target].include_libs)
        checked_files.update(target_files)
        target_files  = check_target(checked_files, dependence_list)
    
    return CodeDependence(source_path,
                          tuple(sorted(include_files)),
                          tuple(sorted(include_libs)))

class CodeManager:
    def __init__(self):
        self._source_code = []
        self._dependence  = {}
    
    @property
    def source_code(self):
        return self._source_code
    
    def add_source(self, source_path):
        """ソースコードを追加"""
        # 絶対パス化
        source_path = pathlib.Path(source_path).resolve()
        if source_path in self._source_code:
            return
        self._source_code.append(source_path)
        # 依存性解析
        self._dependence[source_path] = (check_dependence(source_path))
        # 新たに検出したファイルの依存性解析
        target_list = check_target(self._dependence.keys(), self._dependence)
        while len(target_list) != 0:
            for target in target_list:
                self._dependence[target] = check_dependence(target)
            target_list = check_target(
                    self._dependence.keys(), self._dependence)
    
    def dependence_list(self):
        """各ソースコードの全依存関係を解析し出力"""
        result = {}
        for source_code in self._source_code:
           result[source_code] = full_dependence(source_code, self._dependence)
        return result
    
    def structure(self):
        """ディレクトリ構成を出力 {dirpath: (source_path, ...), ...}"""
        result = {}
        for source_path in self.source_code:
            if not source_path.parent in result:
                result[source_path.parent] = []
            result[source_path.parent].append(source_path)
        return dict((key, tuple(value)) for key, value in result.items())
