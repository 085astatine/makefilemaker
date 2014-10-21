# -*- coding: utf-8 -*-

import sys
import pathlib

from .code_manager        import CodeManager
from .compiler_setting    import CompilerSetting
from .build_command_maker import BuildCommandMaker
from .object_path_maker \
import same_source_name, same_source_dir, specific_directory
from .link_object import LinkObject, LinkObjectMode
from .command_line_option import option_parser
from .main_functions \
import load_option, make_build_data_list, make_makefile_generator
from .path_function import path_to_string, path_sort

class MakefileMaker:
    def __init__(self, argv= None):
        # オプション取得
        self._option = option_parser().parse_args(argv)
        if(self._option.verbose >= 1):
            print('option list:')
            print('  ', self._option)
        # root directory
        self._root_path = pathlib.Path(sys.argv[0]).parent.resolve()
        # コード管理
        self._code_manager = CodeManager(self._option)
        # オブジェクトファイルのパスを生成する関数
        #   入力 root_path, source_path
        self._object_dir_maker  = same_source_dir()
        #   入力 source_path
        self._object_name_maker = same_source_name('o')
        # コンパイラ設定
        self._compiler_setting = CompilerSetting()
        self._build_command_maker = BuildCommandMaker(
                    self._compiler_setting,
                    self._option.verbose >= 1)
        # LinkObjectMode
        self._link_object_mode = LinkObjectMode.Search
        # LinkObjectのlog file
        self._link_object_log = None
    
    def run(self):
        # option読み込み
        load_option(self)
        # 各コードのビルド情報をまとめる
        build_data_list = make_build_data_list(self)
        #   リンクするオブジェクトを解析
        link_object_searcher = LinkObject(
                build_data_list,
                self._code_manager,
                self._build_command_maker,
                self._option.verbose >= 1)
        if not self._link_object_log is None:# log file 設定
            link_object_searcher.set_log_file(self._link_object_log)
        # LikObjectMode毎に処理
        if self._link_object_mode is LinkObjectMode.All:
            link_object_searcher.all()
        elif self._link_object_mode is LinkObjectMode.Search:
            link_object_searcher.search()
        elif self._link_object_mode is LinkObjectMode.Analyze:
            link_object_searcher.analyze()
        elif self._link_object_mode is LinkObjectMode.FullAnalyze:
            link_object_searcher.full_analyze()
        build_data_list = link_object_searcher.build_data_list()
        # MakefileGeneratorを生成
        makefile_generators = make_makefile_generator(self, build_data_list)
        if self._option.test:# テストモードならばファイルを生成せず終了
            return
        for makefile_generator in makefile_generators:
            makefile_generator.make()
    
    def source_code(self, source_path):
        """ソースコードを追加"""
        self._code_manager.add_source(source_path)
    
    def source_code_list(self, source_path_list):
        """ソースコードをまとめて追加"""
        for source_path in source_path_list:
            self.source_code(source_path)
    
    def main_code(self, program_name, main_code_path):
        # 実行プログラム名と対応するmainコードを追加
        self._code_manager.add_main_code(main_code_path, program_name)
    
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
        # 変更を反映
        self._build_command_maker.update_compiler(self._compiler_setting)
    
    def compile_option(self, options):
        """コンパイルのオプションを指定"""
        if isinstance(options, str):# 文字列
            self._compiler_setting.option_list.extend(options.split())
        elif getattr(options, '__iter__', False):# シーケンス
            self._compiler_setting.option_list.extend(options)
        else:# その他
            self._compiler_setting.option_list.append(options)
        # 変更を反映
        self._build_command_maker.update_compiler(self._compiler_setting)
    
    def include_path(self, include_path, target_header= None):
        """include設定を読み込む
        include_path (pathlib.Path or str): includeに追加されるpath
        target_header (sequence(str) or str or None)
                    : 対象となるheader名
                      None ならば全てに適用"""
        self._build_command_maker.add_include_setting(
                    include_path, formalize_target_header(target_header))
    
    def library(self, library, target_header= None):
        """library設定を読み込む
        library (sequence(str) or str) : リンクするライブラリ名
        target_header (sequense(str)) or str or None)
                    : 対象となるheader名
                      None ならば全てに適用"""
        self._build_command_maker.add_library_setting(
                    library, formalize_target_header(target_header))
    
    def save_dependence_graph(self, filename):
        file_path = self._root_path.joinpath(filename)
        self._code_manager.save_dependent_graph(file_path)
    
    def link_object_mode(self, mode_name):
        """LinkObjectModeを設定
        mode_name= search, all, analyze, full-analyze"""
        for mode in LinkObjectMode:
            if mode.value == mode_name:
                self._link_object_mode = mode
                break
        else:
            message= 'mode_name<{0}> is not LinkObjectMode'
            raise ValueError(message);
    
    def set_link_object_log(self, log_file):
        """LinkObjectのlog fileを設定
        log_file: log file名 (str or pahlib.Path)"""
        log_path = pathlib.Path(log_file)
        self._link_object_log = log_path

def formalize_target_header(target_header):
    """入力された対象headerを整形して返す
    target_header (sequense(str)) or str or None): 対象となるheader名
    return sequence(str) or None"""
    header_list = []
    if target_header == None:
        # None
        header_list = None
    elif isinstance(target_header, str):
        # 文字列
        header_list.append(target_header)
    elif getattr(target_header, '__iter__', False):
        # シーケンス
        header_list.extend(target_header)
    else:
        # その他
        header_list.append(target_header)
    return header_list
