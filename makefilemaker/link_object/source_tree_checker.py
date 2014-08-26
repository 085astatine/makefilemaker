# -*- coding: utf-8 -*-

import pathlib
import subprocess
from .functions         import source_to_object
from .checker_functions import build_test, make_build_test_data
from ..path_function   import path_to_string, path_sort

class SourceTreeChecker:
    def __init__(self,
                 source_tree,
                 build_data_list,
                 build_command_maker,
                 verbose= False):
        """コンストラクタ
        source_tree        : CodeTree
        build_data_list    : BuildDataのリスト
        build_command_maker: BuildCommandMaker
        verbose            :"""
        self._source_tree = source_tree
        self._build_data_list = build_data_list
        self._build_command_maker = build_command_maker
        self._verbose = verbose
        # build_test時のlog file
        self._analyze_log = subprocess.DEVNULL
    
    def analyze(self):
        if self._verbose:# 表示
            print('SourceTreeChecker analyze')
        for source in self._source_tree.node_list(depth_sort= True):
            if self._verbose:# 試行する除外対象を表示
                print('test removed code: {0}'.format(path_to_string(source)))
            node = self._source_tree.get(source)
            if node is None:
                print('  already removed')
                continue
            # 試行用のSourceTreeを作成
            test_tree = self._source_tree.copy()
            test_tree.remove(source)
            # SourceTreeからビルド情報を纏める
            object_list = source_to_object(test_tree.node_list(),
                                           self._build_data_list)
            build_data  = make_build_test_data(object_list,
                                               self._build_data_list)
            # ビルドを試行
            return_code = build_test(build_data,
                                    self._build_command_maker,
                                    self._analyze_log)
            if self._verbose:# 試行結果表示
                print('  ReturnCode<{0}>: {1}'.format(
                            return_code,
                            'Success' if return_code == 0 else 'Failed'))
            if return_code == 0:
                # 試行に成功したならば除外対象に追加
                self._source_tree.remove(source)
                if self._verbose:# 表示
                    print('  remove: {0}'.format(path_to_string(source)))
        if self._verbose:# 表示
            print()
    
    def full_analyze(self):
        prev_tree_size = len(self._source_tree.node_list())
        while True:
            self.analyze()
            tree_size = len(self._source_tree.node_list())
            if tree_size == prev_tree_size:
                break
            prev_tree_size = tree_size
    
    def source_tree(self):
        """SourceTreeを返す"""
        return self._source_tree.copy()
    
    def set_log_file(self, log_file_path):
        """build_test時のlog fileを設定する
        設定しなければlogは取らない
        log_file_path: pathlib.Path"""
        self._analyze_log = log_file_path.open(
                    mode= 'a', encoding= 'utf-8', newline= '')
