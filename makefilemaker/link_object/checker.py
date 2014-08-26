# -*- coding: utf-8 -*-


import subprocess
from ..build_data    import BuildData, ProgramBuildData
from ..path_function import path_to_string, path_sort

class Checker:
    
    def __init__(self,
                 main_code_list,
                 build_data_list,
                 build_command_maker,
                 verbose= False):
        """"""
        self._main_code_list = main_code_list
        self._build_data_list     = build_data_list
        self._build_command_maker = build_command_maker
        self._verbose = verbose
        # 解析結果
        self._result = dict(
                    (main_code, self._build_data_list[main_code].link_objects)
                    for main_code in self._main_code_list)
    
    def check(self):
        for main_code in self._main_code_list:
            check(self, main_code)

def check(self, main_code):
    """main_codeにリンクするオブジェクトを調査する
    main_code: main関数を含む"""
    object_list = list(self._result[main_code])
    for object_file in object_list[:]:
        print('test', object_file)
        test_object_list = object_list[:]
        test_object_list.remove(object_file)
        print(len(test_object_list), len(object_list))
        test_build_data = make_test_build_data(
                    self, main_code, test_object_list)
        # ビルドを試行
        returncode = build_test(self, test_build_data)
        print(returncode)
        # 試行結果から不要か判定
        if returncode == 0:
            print('remove')
            object_list.remove(object_file)
    # 結果を反映
    self._result[main_code] = object_list

def build_test(self, build_data):
    """ビルド情報を基にlinkコマンドを作成し実行
    build_data: ProgramBuildData
    return returncode 0 -> 正常終了
                      1 -> 異常終了"""
    command = self._build_command_maker.link_command(build_data)
    print(command)
    returncode  = subprocess.call(command, shell= True)
    return returncode

def make_test_build_data(self, main_code, object_list):
    
    # 関連する全ライブラリを取得
    lib_set = set()
    for code in self._build_data_list.keys():
        if self._build_data_list[code].object_path in object_list:
            lib_set.update(self._build_data_list[code].include_libs)
    
    build_data = ProgramBuildData(
                self._build_data_list[main_code].source_path,
                self._build_data_list[main_code].object_path,
                'a.out',
                self._build_data_list[main_code].include_files,
                tuple(sorted(lib_set)),
                object_list)
    return build_data

