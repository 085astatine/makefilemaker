# -*- encoding: utf-8 -*-

import copy
from collections import namedtuple
from ..path_function  import path_to_string, path_sort

class CodeTreeNood(namedtuple('CodeTreeNode',
            ('node_path', 'child_path_list'))):
    """CodeTreeのノード"""
    def __str__(self):
        str_piece = []
        str_piece.append('node_path      : {0}'.format(
                    path_to_string(self.node_path)))
        str_piece.append('child_path_list:')
        str_piece.extend('  {0}'.format(path_to_string(child_path))
                         for child_path in self.child_path_list)
        return '\n'.join(str_piece)

class CodeTree:
    """コードの依存性を基にして作られた一つのコードを根とした木構造"""
    def __init__(self, root_code, child_path_list, exceptions= []):
        """コンストラクタ
        root_code      : 根となるコード
        child_path_list: 根となるコードが持つ子のpath
        exceptions     : 除外対象"""
        # root
        self._root_code = root_code
        # 除外対象
        self._exceptions = tuple(sorted(exceptions, key= path_sort))
        # 木構造データ
        self._node_data = []
        self.add(root_code, child_path_list)
    
    def add(self, node_path, child_path_list):
        """ノードを加える
        その際、上の層に含まれているコードを子として持たないようにする
        node_path       : ノードのpath
        childe_path_list: ノードの子のpath"""
        # 木に含まれるべき対称か判定
        if len(self._node_data) != 0 and not node_path in self.target_list():
            message = '<{0}> is not tree\'s target'.format(
                                  path_to_string(node_path))
            raise ValueError(message)
        code_list = self.code_list()
        self._node_data.append(CodeTreeNood(
                    node_path,
                    tuple(child_path for child_path in child_path_list
                          if (not child_path in code_list)
                             and (child_path != node_path)
                             and (not child_path in self._exceptions))))
    
    def get(self, node_path):
        """指定したCodeTreeNodeを取得
        見つからなければNoneを返す
        node_path: CodeTreeNodeのnode_path"""
        for node in self._node_data:
            if node_path == node.node_path:
                return node
        else:
            return None
    
    def remove(self, node_path):
        """指定したノードを取り除く
        その際、そのノードから派生した子ノードも取り除く
        指定したノードが存在しない時例外を発生させる"""
        node = self.get(node_path)
        if node is None:# 例外発生
            message = '<{0}> is not found in node_data'.format(
                                  path_to_string(node_path))
            raise ValueError(message)
        remove_node(self, node)
    
    def root(self):
        """rootとなるノードを返す"""
        return self.get(self._root_code)
    
    def node_list(self, depth_sort= False):
        """木に含まれる全ノード
        depth_sort: 深さでソートするか否か True or False
                      Default False"""
        if not isinstance(depth_sort, bool):
            raise ValueError
        if depth_sort:
            return tuple(node.node_path for _, node
                         in self.node_data_with_depth(depth_sort= True))
        node_set = set(node.node_path for node in self._node_data)
        return tuple(sorted(node_set, key= path_sort))
    
    def node_data_with_depth(self, depth_sort= False):
        """木に含まれる全ノード 深さ付き
        ((depth, node), ...)
        depth_sort: 深さでソートするか否か
                      Dafault False"""
        return depth_mapping(self, depth_sort)
    
    def child_list(self):
        """全ノードが持つ子ノード"""
        code_set = set()
        for node in self._node_data:
            code_set.update(node.child_path_list)
        return tuple(sorted(code_set, key= path_sort))
    
    def code_list(self):
        """木に含まれる全ノードとその子ノードのリスト"""
        code_set = set()
        code_set.update(self.node_list())
        code_set.update(self.child_list())
        return tuple(sorted(code_set, key= path_sort))
    
    def target_list(self):
        """木構造の対象だが未だ含まれていないノード"""
        return tuple(sorted(
                       set(self.child_list()).difference(self.node_list()),
                       key= path_sort))
    
    def is_closed(self):
        """木に含まれるべきコードが全て含まれているか判定"""
        return len(self.target_list()) == 0
    
    def copy(self):
        """自身のcopy.deepcopyを返す"""
        return copy.deepcopy(self)
    
    def __str__(self):
        str_piece = []
        str_piece.append(self.__class__.__name__)
        for depth, node in self.node_data_with_depth():
            str_piece.append('{0}{1}'.format(
                        '  ' * depth,
                        path_to_string(node.node_path)))
        return '\n'.join(str_piece)
    
    def __repr__(self):
        return '{0}({1})'.format(
                   self.__class__.__name__,
                   ', '.join('{0}= {1}'.format(key, repr(getattr(self, key)))
                             for key in sorted(self.__dict__)))

def remove_node(self, node):
    """指定したノードを取り除く
    その際、そのノードから派生した子ノードも取り除く"""
    for child_path in node.child_path_list:
        child = self.get(child_path)
        if child is None: continue
        remove_node(self, child)
    self._node_data.remove(node)

def depth_mapping(self, depth_sort= False):
    """木に含まれる全ノード 深さ付き
        ((depth, node), ...)
        depth_sort: 深さでソートするか否か
                      Dafault False"""
    if not isinstance(depth_sort, bool):
        raise ValueError
    node_data = self._node_data.copy()
    data_list = []
    # 再帰関数
    def next(node_path, depth):
        node = self.get(node_path)
        if node is None: return
        data_list.append((depth, node))
        if node in node_data:
            node_data.remove(node)
        for child in node.child_path_list:
            next(child, depth + 1)
    # rootを基点に始動
    next(self._root_code, 0)
    # 深さが与えられ無かったノードが存在するか判定
    if len(node_data) != 0:
        message = 'nodes not all have a depth'
        raise ValueError(message)
    # 深さでソート
    if depth_sort:
        sort_function = lambda x: (x[0], path_sort(x[1].node_path))
        data_list.sort(key= sort_function)
    return tuple(data_list)
