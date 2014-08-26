# -*- coding: utf-8 -*-

import sys, pathlib

from .code_manager      import CodeManager
from .code_block \
import CodeBlock, MainCodeBlock, MakeBlock, RootMakeBlock
from .compiler_setting  import CompilerSetting
from .object_path_maker \
import same_source_name, same_source_dir, specific_directory
from .link_object_searcher import replace_suffix
from .command_line_option \
import basic_option, parse_option

class MakefileMaker:
    def __init__(self):
        # オプション取得
        option_parser = basic_option()
        self._option = parse_option(option_parser)
        print(self._option)
        # コード管理
        self._code_manager = CodeManager()
        # オブジェクトファイルのパスを生成する関数
        #   入力 root_path, source_path
        self._object_dir_maker  = same_source_dir()
        #   入力 source_path
        self._object_name_maker = same_source_name('o')
        # 依存しているヘッダファイルリストから
        # リンク対象のオブジェクトを取得する関数
        #   入力 include_files
        self._link_source_seacher = replace_suffix(('c','cpp',))
        # コンパイラ設定
        self._compiler_setting = CompilerSetting()
        # mainコードと対応する実行プログラム名
        self._main_code = {}
    
    def run(self):
        root_path = pathlib.Path(sys.argv[0]).parent.resolve()
        # ディレクトリ構造を取得
        structure = self._code_manager.structure()
        # 各コードの情報
        code_block_list = make_code_block_list(self, root_path)
        #show_code_block_list(code_block_list)
        # 各ディレクトリ毎にコード情報を分類
        #   root以外
        make_block_list = make_make_block_list(
                self, root_path, structure, code_block_list)
        #   root
        root_make_block = make_root_make_block(
            self, root_path, structure, code_block_list)
        #print(make_block_list)
        for make_block in make_block_list.values():
            #print(make_block._dir_path)
            make_block.make()
        root_make_block.make()
    
    def source_code(self, source_path):
        """ソースコードを追加"""
        self._code_manager.add_source(source_path)
    
    def source_code_list(self, source_path_list):
        """ソースコードをまとめて追加"""
        for source_path in source_path_list:
            self.source_code(source_path)
    
    def main_code(self, program_name, main_source_name):
        # 実行プログラム名と対応するmainコードを追加
        main_source_path = pathlib.Path(main_source_name).resolve()
        self._main_code[main_source_path] = program_name
        self._code_manager.add_source(main_source_name)
    
    def object_dir(self, dirname, relative= False):
        """オブジェクトファイルを置くディレクトリを設定
        relative= False -> root_path  にあるディレクトリ
        relative= True  -> source_pathにあるディレクトリ"""
        if relative:
            self._object_dir_maker  = same_source_dir(dirname)
        else:
            self._object_dir_maker  = specific_directory(dirname)
    
    def object_suffix(self, suffix):
        """オブジェクトファイルの拡張子設定を変更"""
        self._object_name_maker = same_source_name(suffix)
    
    # コンパイラ設定
    def compiler(self, compiler):
        """コンパイラを指定"""
        self._compiler_setting.compiler = compiler
    
    def compile_option(self, options):
        """コンパイルのオプションを指定"""
        if isinstance(options, str):# 文字列
            self._compiler_setting.option_list.extend(options.split())
        elif getattr(options, '__iter__', False):# シーケンス
            self._compiler_setting.option_list.extend(options)
        else:# その他
            self._compiler_setting.option_list.append(options)
    
    def include_path(self, lib, include_path):
        self._compiler_setting.include_setting[lib] = include_path
    
    def library(self, lib_name, *lib_list):
        self._compiler_setting.library_setting[lib_name] = tuple(lib_list)

# 関数
def object_path_maker(self, root_path, source_path):
    """オブジェクトファイルのパスを生成"""
    object_dir  = self._object_dir_maker(root_path, source_path)
    object_name = self._object_name_maker(source_path)
    return object_dir.joinpath(object_name)

def make_code_block_list(self, root_path):
    """各ソースコードのビルド情報をまとめる"""
    result = {}
    # 各ソースコードの依存性関係結果
    dependence_data = self._code_manager.dependence_list()
    # ソースコード毎に処理
    for source_path in self._code_manager.source_code:
        # オブジェクトファイルのパスを生成
        object_path = object_path_maker(self, root_path, source_path)
        # 追加
        result[source_path] = CodeBlock(
            source_path, object_path,
            dependence_data[source_path].include_files,
            dependence_data[source_path].include_libs)
    # mainコードの処理
    for source_path in self._main_code.keys():
        result[source_path] = MainCodeBlock(
                source_path, result[source_path].object_path,
                self._main_code[source_path],
                result[source_path].include_files,
                result[source_path].include_libs,
                link_objects(self, result[source_path].include_files, result))
    return result

def link_objects(self, include_files, code_block_list):
    """プログラム作成時にリンク対象となるオブジェクトのパスを取得"""
    objects_path = []
    target_source_code = self._link_source_seacher(include_files)
    for source_path in target_source_code:
        objects_path.append(code_block_list[source_path].object_path)
    return tuple(objects_path)

def show_code_block_list(code_block_list):
    """CodeBlockの一覧を表示"""
    for key in sorted(code_block_list.keys(), key= lambda path : path.parent):
        print(code_block_list[key])
        print()

def make_make_block_list(self, root_path, structure, code_block_list):
    """各ディレクトリ毎にCodeBlockを分類"""
    result = {}
    for dir_path, source_path_list in structure.items():
        # rootディレクトリは別の処理で実行
        if dir_path == root_path: continue
        result[dir_path] = MakeBlock(
                dir_path,
                tuple(code_block_list[source_path]
                      for source_path in source_path_list),
                self._compiler_setting)
    return result

def make_root_make_block(self, root_path, structure, code_block_list):
    """rootディレクトリのCodeBlockを分類"""
    subdirs = sorted(set(source_path.parent
            for source_path in code_block_list.keys()
            if source_path != root_path))
    make_block = RootMakeBlock(
        root_path,
        tuple(code_block_list[source_path]
                  for source_path in structure[root_path]),
        self._compiler_setting,
        subdirs)
    return make_block
