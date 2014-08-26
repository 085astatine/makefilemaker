# -*- encoding: utf-8 -*-

import re
from ..path_function  import path_to_string, path_sort
from .code_data import CodeDependence
from .code_tree import CodeTree

def check_dependence(code_path):
    """codeが依存しているファイル, ライブラリを検出
    code_path: 対象とするcodeのpath"""
    # 検出したヘッダファイル, ライブラリ
    include_files = []
    include_libs  = []
    # 正規表現
    include_file_regex = re.compile('#include( +|)"(?P<header>.+)"')
    include_lib_regex  = re.compile('#include( +|)<(?P<header>.+)>')
    with code_path.open(encoding= 'utf-8', newline= '') as code_file:
        for line in code_file:
            # match
            include_file_match = include_file_regex.match(line)
            include_lib_match  = include_lib_regex.match(line)
            # include_file判定
            if include_file_match:
                # 絶対パス化
                header_path = code_path.parent.joinpath(
                    include_file_match.group('header')).resolve()
                include_files.append(header_path)
            # include_lib判定
            elif include_lib_match:
                include_libs.append(include_lib_match.group('header'))
    #出力
    return CodeDependence(code_path,
                          tuple(sorted(include_files, key= path_sort)),
                          tuple(sorted(include_libs)))

def full_dependence(source_path, dependence_list):
    """sourceが依存しているファイルを全て纏める
    source_path    : 対象とするsourceのpath
    dependence_list: 依存性解析結果集"""
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
                          tuple(sorted(include_files, key= path_sort)),
                          tuple(sorted(include_libs)))

def check_target(checked_list, dependence_list):
    """解析されたファイルに関連するファイルで, 未だ調査されていないものを選出
    checked_list   : 依存性解析されたファイルのリスト
    dependence_list: 依存性解析結果集"""
    # 検出されたファイル
    detected_list = set(file
        for checked_file in checked_list
        for file         in dependence_list[checked_file].include_files)
    # 差を出力
    return sorted(detected_list.difference(checked_list), key= path_sort)

def reverse_dependence(dependence_list, verbose= False):
    """依存性解析結果を反転させる
    ファイルとそのファイルに依存しているファイルリストの組を出力
    dependence_list: 依存性解析結果集
    出力
    {code_path: (file that are dependent on code, ...), ...}"""
    reversed_list = {}
    # 被依存ファイルリストを取得
    included_list = sorted(set(
                file for dependence_data in dependence_list.values()
                     for file            in dependence_data.include_files),
                key= path_sort)
    if verbose:# 表示
        print('ReverseDependence')
        print('included list')
        for path in included_list:
            print('  {0}'.format(path_to_string(path)))
        print()
    # 初期化
    for file in included_list:
        reversed_list[file] = []
    # 各々を解析
    for code_path, dependence_data in dependence_list.items():
        for include_file in dependence_data.include_files:
            reversed_list[include_file].append(code_path)
    # ソート
    for code_list in reversed_list.values():
        code_list.sort(key= path_sort)
    if verbose:# 反転結果を表示
        print('ReverseDependence Result')
        for included_file in sorted(reversed_list.keys(), key= path_sort):
            print('included file: {0}'.format(
                        path_to_string(included_file)))
            for code_path in reversed_list[included_file]:
                print('  {0}'.format(path_to_string(code_path)))
            print()
    return reversed_list

def make_code_tree(self, root_code_path, exceptions= []):
    """一つのコードを根としてコードの依存関係の木構造をつくる
    root_code_path: CodeTreeのrootとなるコード
    exceptions    : CodeTreeに含まれる対象外となるコード"""
    code_tree = CodeTree(
                    root_code_path,
                    self._dependent_data_list[root_code_path].include_files,
                    exceptions)
    while not code_tree.is_closed():
        for code_path in code_tree.target_list():
            code_tree.add(code_path,
                          self._dependent_data_list[code_path].include_files)
    return code_tree

def save_dependent_graph(self, file_path):
    with file_path.open(mode= 'w', encoding= 'utf-8', newline= '') as file:
        for code in sorted(self._dependent_data_list.keys(), key= path_sort):
            for included_file in self._dependent_data_list[code].include_files:
                file.write('{0},{1}\n'.format(
                        path_to_string(code),
                        path_to_string(included_file)))
