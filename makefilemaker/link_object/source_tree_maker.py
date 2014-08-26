# -*- coding: utf-8 -*-

import copy
from .functions      import get_source_code_list
from ..code_manager  import CodeTree
from ..path_function import path_to_string, path_sort

class SourceTreeMaker:
    
    def __init__(self,
                 main_code,
                 code_manager,
                 source_code_list= None,
                 verbose= False):
        """コンストラクタ
        main_code         : rootとなるsource code
        code_manager      : CodeManager
        source_code_list  : 木の対象となるsource code
        verbose           : verbose mode True or False"""
        # rootとなるsource_code
        self._main_code = main_code
        # source code設定
        if source_code_list is None:
            self._source_list = get_source_code_list(main_code, code_manager)
        else:
            self._source_list = source_code_list
        self._code_manager = code_manager
        self._verbose      = verbose
        # 被依存関係データ
        self._depended_data = self._code_manager.depended_data_list()
        # CodeTreeに含まれたことのあるcode
        self._detected_code = []
        # SourceCodeTree
        self._source_tree = CodeTree(*self.make_node(self._main_code))
    
    def make(self):
        """CodeTreeをclosedになるまで作成"""
        while not self._source_tree.is_closed():
            for source in self._source_tree.target_list():
                self._source_tree.add(*self.make_node(source))
    
    def source_tree(self):
        """CodeTreeを返す
        CodeTreeがclosedで無ければValueErrorを発生させる"""
        if not self._source_tree.is_closed():
           raise ValueError
        return self._source_tree.copy()
    
    def make_node(self, node_code):
        """SourceCodeTreeのノードを作成
        node_code: nodeのpath"""
        code_tree = self._code_manager.code_tree(
                            node_code)#, self._detected_code)
        if self._verbose:# 表示確認
            print(code_tree)
            print()
        # 木に含まれたことのあるcodeを更新
        self._detected_code.extend(code_tree.code_list())
        # 木に含まれるコードと被依存関係にあるsourceを検出
        depended_source = []
        for node in code_tree.node_list(depth_sort= True):
            for source in (code for code in self._depended_data.get(node, [])
                           if code in self._source_list):
                if not source in depended_source:
                    depended_source.append(source)
        return (node_code, tuple(depended_source))
