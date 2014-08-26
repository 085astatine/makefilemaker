# -*- coding: utf-8 -*-

from collections import namedtuple
from .path_function import path_to_string

class BuildData(namedtuple('BuildData',
('source_path', 'object_path', 'include_files', 'include_libs',))):
    """ビルド時に必要となるコード情報"""
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('source_path  :{0}'.format(
                    path_to_string(self.source_path)))
        piece.append('object_path  :{0}'.format(
                    path_to_string(self.object_path)))
        piece.append('include_files:')
        piece.extend('  {0}'.format(path_to_string(file))
                     for file in self.include_files)
        piece.append('include_libs :')
        if len(self.include_libs) != 0:
            piece.append('  {0}'.format(', '.join(self.include_libs)))
        return '\n'.join(piece)

class ProgramBuildData(namedtuple('ProgramBuildData',
('source_path', 'object_path', 'include_files', 'include_libs',
 'program_path', 'link_objects',))):
    """プログラムのビルドに必要なコード情報"""
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('program_path :{0}'.format(
                    path_to_string(self.program_name)))
        piece.append('source_path  :{0}'.format(
                    path_to_string(self.source_path)))
        piece.append('object_path  :{0}'.format(
                    path_to_string(self.object_path)))
        piece.append('include_files:')
        piece.extend('  {0}'.format(path_to_string(file))
                     for file in self.include_files)
        piece.append('include_libs :')
        if len(self.include_libs) != 0:
            piece.append('  {0}'.format(', '.join(self.include_libs)))
        piece.append('link_objects :')
        piece.extend('  {0}'.format(path_to_string(object))
                     for object in self.link_objects)
        return '\n'.join(piece)
