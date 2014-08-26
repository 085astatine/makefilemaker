# -*- coding: utf-8 -*-

import re
import pathlib
from   collections import namedtuple

from .code_data import CodeDependence
from .functions import check_dependence, full_dependence, check_target, reverse_dependence, save_dependent_graph, make_code_tree
from ..path_function  import path_to_string, path_sort
from ..print_function import print_indented

class CodeManager:
    def __init__(self, option):
        self._option = option
        # source_codeのリスト
        self._source_code = []
        # main_codeのリスト
        self._main_code   = []
        # main_codeとprogram_nameとの関連
        #   {main_code: program_path, ...}
        self._program_path_data = {}
        # 各codeの依存性解析結果
        #   {code_path: CodeDependence, ...}
        self._dependent_data_list = {}
    
    @property
    def source_code(self):
        """ソースコードをtupleで返す"""
        return tuple(sorted(self._source_code, key= path_sort))
    
    @property
    def main_code(self):
        """mainコードをtupleで返す"""
        return tuple(sorted(self._main_code, key= path_sort))
    
    @property
    def dependent_data_list(self):
        """コードの依存性解析結果を返す
        ((code, CodeDependence), ...)"""
        return self._dependent_data_list
    
    def depended_data_list(self):
        """コードの被依存解析結果を返す
        ((code, (depended_code, ...)), ...)"""
        data_list = reverse_dependence(self._dependent_data_list,
                                       self._option.verbose >= 3)
        return data_list
    
    def add_source(self, source_path):
        """ソースコードを追加"""
        # 絶対パス化
        source_path = pathlib.Path(source_path).resolve()
        if source_path in self._source_code:
            if self._option.verbose >= 1:# 表示
                print('source<0> is rlready appended'
                            .format(path_to_string(source_path)))
            return
        if self._option.verbose >= 1:# ソースコード表示
            print('add source<{0}>'.format(path_to_string(source_path)))
        self._source_code.append(source_path)
        # 依存性解析
        self._dependent_data_list[source_path] = check_dependence(source_path)
        if self._option.verbose >= 2:# 依存性解析結果を表示
            print_indented(self._dependent_data_list[source_path], 4)
            print()
        # 新たに検出したファイルの依存性解析
        #   初期の捜査対象
        target_list = check_target(self._dependent_data_list.keys(),
                                   self._dependent_data_list)
        while len(target_list) != 0:
            if self._option.verbose >= 3:# 対象ファイルを列挙
                print('target list:')
                for target in target_list:
                    print('  {0}'.format(path_to_string(target)))
                print()
            # 各対象を依存性関係結果に追加
            for target in target_list:
                self._dependent_data_list[target] = check_dependence(target)
                if self._option.verbose >= 1:# 検出したファイルを表示
                    print('  add file<{0}>'.format(path_to_string(target)))
                if self._option.verbose >= 2:# 依存性関係結果を表示
                    print_indented(self._dependent_data_list[target], 6)
                    print()
            # 新たに検出した対象ファイル
            target_list = check_target(
                    self._dependent_data_list.keys(),
                    self._dependent_data_list)
    
    def add_main_code(self, main_code_path, program_path):
        """mainコードを追加"""
        # pathlib化
        main_code_path = pathlib.Path(main_code_path).resolve()
        #   program_pathは実在しないので絶対パス化は不可
        program_path   = pathlib.Path(program_path)
        # データリストに追加
        self._main_code.append(main_code_path)
        self._program_path_data[main_code_path] = program_path
        # 依存性解析
        self.add_source(main_code_path)
    
    def source_code_data(self):
        """各ソースコードの全依存関係を解析し出力"""
        if self._option.verbose >= 2:# 依存性集計結果を表示
            print('Check FullDependence')
        result = {}
        for source_code in self.source_code:
            result[source_code] = full_dependence(
                        source_code, self._dependent_data_list)
            if self._option.verbose >= 2:# 依存性集計結果を表示
                print('full dependence<{0}>'
                            .format(path_to_string(source_code)))
                print_indented(result[source_code], 4)
                print()
        return result
    
    def structure(self):
        """ディレクトリ構成を出力
        {dirpath: (source_path, ...), ...}"""
        result = {}
        for source_path in self.source_code:
            if not source_path.parent in result:
                result[source_path.parent] = []
            result[source_path.parent].append(source_path)
        return dict((key, tuple(sorted(value, key= path_sort)))
                    for key, value in result.items())
    
    def code_tree(self, root_code_path, exceptions= []):
        """一つのコードを根としてコードの依存関係の木構造をつくる
        root_code_path: 木構造のrootとなるcode
        exceptions    : 木構造に含まれる対象外となるcode"""
        return make_code_tree(self, root_code_path, exceptions)
    
    def save_dependent_graph(self, file_path):
        save_dependent_graph(self, file_path)
    
    def program_path(self, main_code):
        """main_codeに対応した実行プログラム名を返す
          対応した実行プログラム名が見つからなければ a.out を返す"""
        return self._program_path_data.get(main_code, 'a.out')
