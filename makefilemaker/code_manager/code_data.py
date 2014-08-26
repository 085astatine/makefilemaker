# -*- encoding: utf-8 -*-

from collections import namedtuple
from ..path_function  import path_to_string, path_sort

class CodeDependence(namedtuple('CodeDependence',
            ('code_path', 'include_files', 'include_libs'))):
    """各ファイルの依存性
    code_name     : コード名
    include_files : #include "..." 
    include_libs  : #include <...>
    """
    def __str__(self):
        str_piece = []
        str_piece.append(self.__class__.__name__)
        str_piece.append('code_path    :{0}'.format(
                    path_to_string(self.code_path)))
        str_piece.append('include_files:')
        if len(self.include_files) != 0:
            str_piece.extend('  {0}'.format(path_to_string(file))
                             for file in self.include_files)
        str_piece.append('include_libs :')
        if len(self.include_libs) != 0:
            str_piece.append('  {0}'.format(', '.join(self.include_libs)))
        return '\n'.join(str_piece)

