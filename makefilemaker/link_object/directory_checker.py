# -*- coding: utf-8 -*-

import pathlib
import subprocess
from .functions         import source_to_object
from .checker_functions import build_test, make_build_test_data
from ..path_function import path_to_string, path_sort

class DirectoryChecker:
    
    def __init__(self,
                 source_code_list,
                 build_data_list,
                 build_command_maker,
                 verbose= False):
        """コンストラクタ"""
        self._source_code_list = source_code_list
        self._build_data_list = build_data_list
        self._build_command_maker = build_command_maker
        self._verbose = verbose
        # ソースコードのディレクトリ
        dir_list = [source.parent for source in source_code_list]
        self._dir_list = tuple(sorted(set(dir_list),
                                      key= dir_list.index,
                                      reverse= True))
        # 除外対象となるディレクトリ
        self._removed_dir_list = []
        # build_test時のlog file
        self._analyze_log = subprocess.DEVNULL
    
    def analyze(self):
        if self._verbose:# 表示
            print('DirectoryChecker analyze')
        for dir in self._dir_list:
            if self._verbose:# 試行する除外directory
                print('test removed dir: {0}'.format(path_to_string(dir)))
            # 除外directory設定
            removed_dir_list = self._removed_dir_list.copy()
            removed_dir_list.append(dir)
            # ソースコード, オブジェクト, ビルド情報を設定
            source_code_list = dir_filtered_source_code_list(
                        self._source_code_list, removed_dir_list)
            object_list = source_to_object(source_code_list,
                                           self._build_data_list)
            build_data  = make_build_test_data(object_list,
                                               self._build_data_list)
            # ビルド試行
            return_code = build_test(build_data,
                                    self._build_command_maker,
                                    self._analyze_log)
            if self._verbose:# 試行結果表示
                print('  ReturnCode<{0}>: {1}'.format(
                            return_code,
                            'Success' if return_code == 0 else 'Failed'))
            if return_code == 0:
                # 試行に成功したならば除外対象に追加
                self._removed_dir_list.append(dir)
                if self._verbose:
                    print('  remove: {0}'.format(path_to_string(dir)))
        if self._verbose:# 空行挿入
            print()
    
    def source_code_list(self):
        """ソースコードのリストを返す
        不必要だとされたディレクトリ内のソースコードは除外されている"""
        return dir_filtered_source_code_list(
                           self._source_code_list, self._removed_dir_list)
    
    def set_log_file(self, log_file_path):
        """build_test時のlog fileを設定する
        設定しなければlogは取らない
        log_file_path: pathlib.Path"""
        self._analyze_log = log_file_path.open(
                    mode= 'a', encoding= 'utf-8', newline= '')

def dir_filtered_source_code_list(source_code_list, removed_dir_list):
    """source_code_listからremove_dir_listに含まれているものを除外して返す"""
    code_list = tuple(sorted((source for source in source_code_list
                              if not source.parent in removed_dir_list),
                             key= path_sort))
    return code_list

