# -*- coding: utf-8 -*-

from .build_data         import BuildData, ProgramBuildData
from .makefile_generator import MakefileGenerator
from .object_path_maker  import object_path_maker
from .path_function      import path_sort

def load_option(self):
    """コマンドラインオプションを読み込む"""
    # LinkObjectMode
    if not self._option.link_object_mode is None:
        self._link_object_mode = self._option.link_object_mode
    # logfile
    if not self._option.log_file is None:
        self.set_link_object_log(self._option.log_file)

def make_build_data_list(self):
    """各ソースコードのビルド情報をまとめる
    sourceコードのパス, objectファイル名、依存しているファイル, ライブラリ
    return {source_path: BuildData, ...}"""
    build_data_list = {}
    # 各ソースコードの依存性関係結果
    dependence_data = self._code_manager.source_code_data()
    # ソースコード毎に処理
    for source_path in self._code_manager.source_code:
        build_data_list[source_path] = BuildData(
                    source_path,
                    object_path_maker(self, source_path),
                    dependence_data[source_path].include_files,
                    dependence_data[source_path].include_libs)
    return build_data_list

def make_makefile_generator(self, build_data_list):
    """各ディレクトリ毎にMakefileGeneratorを生成"""
    # ディレクトリ設定
    dir_list = sorted(set(source.parent for source in build_data_list.keys()),
                      key= path_sort)
    sub_dir_list = dir_list.copy()
    if self._root_path in dir_list:
        sub_dir_list.remove(self._root_path)
    else:
        dir_list.append(self._root_path)
    # MakefileGeneratorを生成
    generator_list = []
    for dir in dir_list:
        dir_build_data_list = tuple(sorted((build_data_list[source]
                    for source in build_data_list.keys()
                    if source.parent == dir),
                    key= lambda build_data: path_sort(build_data.source_path)))
        # rootディレクトリとそれ以外で分岐
        if dir == self._root_path:
            generator_list.append(MakefileGenerator(
                    dir,
                    dir_build_data_list,
                    self._build_command_maker,
                    sub_dir_list))
        else:
            generator_list.append(MakefileGenerator(
                    dir,
                    dir_build_data_list,
                    self._build_command_maker))
    return generator_list
