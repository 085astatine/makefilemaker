# -*- coding: utf-8 -*-
import copy
from ..build_data    import BuildData, ProgramBuildData
from ..path_function import path_to_string, path_sort
from .functions \
import get_source_code_list, source_to_object, object_to_include_libs
from .source_tree_maker   import SourceTreeMaker
from .source_tree_checker import SourceTreeChecker
from .directory_checker   import DirectoryChecker

class LinkObject:
    """リンクするオブジェクトファイルを設定
    出力{main_code: (object_path, ...), ...}"""
    def __init__(self,
                 build_data_list,
                 code_manager,
                 build_command_maker,
                 verbose= False):
        """main_code_list: main関数のソースコードのリスト
        code_manager  : CodeManager"""
        self._build_data_list  = build_data_list
        self._main_code_list   = code_manager.main_code
        self._source_code_list = code_manager.source_code
        self._code_manager     = code_manager
        self._build_command_maker = build_command_maker
        # verbose mode設定
        self._verbose          = verbose
        self._super_verbose    = False
        # 解析結果
        #   {main_code: (object_path, ...), ...}
        self._object_path = {}
        # SourceTreeCheckerのlog file
        self._log_file = None
    
    def search(self):
        for main_code in self._main_code_list:
            # SourceTreeを作成
            tree_maker = SourceTreeMaker(
                        main_code, self._code_manager,
                        verbose= self._super_verbose)
            tree_maker.make()
            source_tree = tree_maker.source_tree()
            # 解析結果をobjectへ
            self._object_path[main_code] = source_to_object(
                        source_tree.node_list(), self._build_data_list)
    
    def analyze(self):
        """ビルドを試行し、その結果を基に不必要なオブジェクトを判定する
        その結果、最小限のオブジェクトをリンク対象とする
        実際にビルドを行おうとするため、
        全てのオブジェクトファイルが生成されていることを前提とする"""
        for main_code in self._main_code_list:
            source_code_list = analyze_step(self, main_code)
            # 解析結果をobjectへ
            self._object_path[main_code] = source_to_object(
                        source_code_list, self._build_data_list)
    
    def full_analyze(self):
        """analyzeを除外対象がなくなるまで実行する"""
        for main_code in self._main_code_list:
            source_code_list = analyze_step(self, main_code)
            prev_source_code_list = copy.deepcopy(source_code_list)
            while True:
                source_code_list = analyze_step(
                            self, main_code, source_code_list)
                if source_code_list == prev_source_code_list:
                    break
                else:
                    prev_source_code_list = source_code_list
            # 解析結果をobjectへ
            self._object_path[main_code] = source_to_object(
                        source_code_list, self._build_data_list)
    
    def all(self):
        """リンク対象となりうる全てのオブジェクトを"""
        for main_code in self._main_code_list:
            source_list = get_source_code_list(main_code, self._code_manager)
            object_list = source_to_object(source_list, self._build_data_list)
            self._object_path[main_code] = object_list
    
    def object_path(self):
        """解析結果を出力"""
        return self._object_path.copy()
    
    def build_data_list(self):
        """build_data_list内のmain_codeを
        プログラム名, リンクするオブジェクトを含む
        ProgramBuildDataに変更して出力"""
        build_data = copy.deepcopy(self._build_data_list)
        build_data.update(self.program_build_data_list())
        return build_data
    
    def program_build_data_list(self):
        """build_data_list内のmain_codeを
        プログラム名, リンクするオブジェクトを含む
        ProgramBuildDataに変更して出力"""
        build_data = {}
        for main_code in self._main_code_list:
            object_list = self._object_path[main_code]
            build_data[main_code] = ProgramBuildData(
                        self._build_data_list[main_code].source_path,
                        self._build_data_list[main_code].object_path,
                        self._build_data_list[main_code].include_files,
                        object_to_include_libs(
                                    object_list, self._build_data_list),
                        self._code_manager.program_path(main_code),
                        object_list)
        return build_data
    
    def save(self, filepath):
        pass
    
    def load(self, filepath):
        pass
    
    def set_log_file(self, log_file_path):
        self._log_file = log_file_path

def analyze_step(self, main_code, source_code_list= None):
    """LinkObject.analyzeの手続き
    self            : LinkObject
    main_code       : mainとなるcode
    source_code_list: 対象となりうるソースコード"""
    # ソースコード設定
    if source_code_list is None:
        source_code_list = get_source_code_list(main_code, self._code_manager)
    if self._verbose:# 解析対象を表示
        print('LinkObject Analyze: {0}'.format(path_to_string(main_code)))
    # SourceCodeTreeを作成
    tree_maker = SourceTreeMaker(
                main_code,
                self._code_manager,
                source_code_list= source_code_list,
                verbose= self._super_verbose)
    tree_maker.make()
    source_tree = tree_maker.source_tree()
    if self._verbose:# SourceTreeを表示
        print(source_tree)
        print()
    # ディレクトリ毎に判定
    dir_checker = DirectoryChecker(
                source_tree.node_list(depth_sort= True),
                self._build_data_list,
                self._build_command_maker,
                verbose= self._verbose)
    if not self._log_file is None:# log file設定
        dir_checker.set_log_file(self._log_file)
    dir_checker.analyze()
    source_code_list = dir_checker.source_code_list()
    # SourceCodeTreeを作成
    tree_maker = SourceTreeMaker(
                main_code,
                self._code_manager,
                source_code_list= source_code_list,
                verbose= self._super_verbose)
    tree_maker.make()
    source_tree = tree_maker.source_tree()
    if self._verbose:# SourceTreeを表示
        print(source_tree)
        print()
    # SourceTreeから余分なsourceを取り除く
    tree_checker = SourceTreeChecker(
                source_tree,
                self._build_data_list,
                self._build_command_maker,
                verbose= self._verbose)
    if not self._log_file is None:# log file設定
        tree_checker.set_log_file(self._log_file)
    tree_checker.analyze()
    source_tree = tree_checker.source_tree()
    # 解析結果 source_code_list
    return source_tree.node_list()
