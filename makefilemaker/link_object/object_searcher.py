# -*- coding: utf-8 -*-
from fractions import Fraction
from .path_function import path_to_string, path_sort


class SearchedCode:
    __slots__ = ('code_path',
                 'from_list',
                 'to_list',
                 'step',
                 'base_score',
                 'score')
    def __init__(self, code_path, from_code= None):
        self.code_path = code_path
        self.to_list = []
        if from_code == None:
            # 初期
            self.from_list  = []
            self.step       = 0
            self.base_score = Fraction(1)
        else:
            self.from_list  = [from_code.code_path]
            self.step       = from_code.step + 1
            self.base_score = (from_code.base_score
                               * Fraction(1, len(from_code.to_list)))
        self.score = self.base_score
    
    def add_score(self, from_code):
        pass
    
    def __repr__(self):
        return '{0}({1})'.format(
                self.__class__.__name__,
                ', '.join('{0}= {1}'.format(key, repr(getattr(self, key)))
                          for key in self.__slots__))
    
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('code path : {0}'.format(path_to_string(self.code_path)))
        piece.append('from list :')
        piece.extend('    {0}'.format(path_to_string(from_code))
                     for from_code in self.from_list)
        piece.append('to list   :')
        piece.extend('    {0}'.format(path_to_string(to_code))
                     for to_code in self.to_list)
        piece.append('step      : {0}'.format(self.step))
        piece.append('base_score: {0}'.format(self.base_score))
        piece.append('score     : {0}'.format(self.score))
        return '\n'.join(piece)

class Searcher:
    def __init__(self,
                 main_code,
                 main_code_list,
                 depending_data_list,
                 depended_data_list,
                 verbose):
        self.main_code = main_code
        self._main_code_list = main_code_list
        self._depending_data_list = depending_data_list
        self._depended_data_list = depended_data_list
        self._verbose = verbose
        # 検出したファイルのリスト
        self._detected_code_list = []
        # 検出結果 SearchedCodeのリスト
        self._code_list = []
        #   main codeを追加
        self.add_new_code(main_code)
    
    def next_step(self):
        for code in self._code_list:
            pass
    
    def add_new_code(self, code_path, from_code_path= None):
        self._detected_code_list.append(code_path)
        if from_code_path == None:
            new_code = SearchedCode(code_path)
        else:
            if not from_code_path in self._detected_code_list:
                print('error')
                return
            i = code_list_index(self, from_code_path)
            print(i)
            new_code = SearchedCode(code_path, self._code_list[i])
        new_code.to_list.extend(code
                for code in self._depending_data_list[code_path].include_files
                if not code in self._main_code_list)
        self._code_list.append(new_code)

def code_list_index(self, code_path):
    return self._detected_code_list.find(code_path)

class ObjectSearchManager:
    def __init__(self,
                 code_list,
                 main_code_list,
                 depending_data_list,
                 depended_data_list,
                 object_converter,
                 verbose= False):
        self._code_list = code_list
        self._main_code_list = main_code_list
        self._depending_data_list = depending_data_list
        self._depended_data_list = depended_data_list
        self._object_converter = object_converter
        self._verbose = verbose
    
    def search(self):
        for main_code in self._main_code_list:
            searcher = Searcher(main_code,
                     self._main_code_list,
                     self._depending_data_list,
                     self._depended_data_list,
                     self._verbose)
            for code in searcher._code_list:
                print(code)
            break
