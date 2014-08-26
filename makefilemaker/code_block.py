# -*- coding: utf-8 -*-

import os.path, pathlib
from   collections import namedtuple

class CodeBlock(namedtuple('CodeBlock',
('source_path', 'object_path', 'include_files', 'include_libs',))):
    """ビルド時に必要となるコード情報"""
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('source_path  :{0}'.format(self.source_path))
        piece.append('object_path  :{0}'.format(self.object_path))
        piece.append('include_files:')
        piece.extend('  {0}'.format(file) for file in self.include_files)
        piece.append('include_libs :')
        piece.append('  {0}'.format(', '.join(self.include_libs)))
        return '\n'.join(piece)

class MainCodeBlock(namedtuple('MainCodeBlock',
('source_path', 'object_path', 'program_name',
 'include_files', 'include_libs', 'link_objects',))):
    """プログラムのビルドに必要なコード情報"""
    def __str__(self):
        piece = []
        piece.append(self.__class__.__name__)
        piece.append('program_name :{0}'.format(self.program_name))
        piece.append('source_path  :{0}'.format(self.source_path))
        piece.append('object_path  :{0}'.format(self.object_path))
        piece.append('include_files:')
        piece.extend('  {0}'.format(file) for file in self.include_files)
        piece.append('include_libs :')
        piece.append('  {0}'.format(', '.join(self.include_libs)))
        piece.append('link_objects :')
        piece.extend('  {0}'.format(object) for object in self.link_objects)
        return '\n'.join(piece)

class MakeBlock:
    """"""
    def __init__(self, dir_path, code_block_list, compiler_setting):
        self._dir_path         = dir_path
        self._code_block_list  = code_block_list
        self._compiler_setting = compiler_setting
        self._exists_program   = any(isinstance(code_block, MainCodeBlock)
                                     for code_block in code_block_list)
    def make(self):
        makefile = self._dir_path.joinpath('Makefile')
        with makefile.open(mode= 'w', encoding= 'utf-8', newline= '') as file:
            if self._exists_program:
                file.write(self.macro_PROGRAMS())
                file.write('\n\n')
            file.write(self.macro_OBJECTS())
            file.write('\n')
            file.write(self.target_all())
            file.write('\n\n')
            file.write(self.target_clean())
            file.write('\n\n')
            if self._exists_program:
                file.write(self.link_rule())
                file.write('\n\n')
            file.write(self.make_rule())
            file.write('\n\n')
            file.write(self.dependent_header())
            file.write('\n')
    
    def macro_PROGRAMS(self):
        """実行プログラムのマクロ(PROGRAMS)を宣言"""
        code = []
        programs = sorted(code_block.program_name
                for code_block in self._code_block_list
                if isinstance(code_block, MainCodeBlock))
        if len(programs) != 0:
            code.append('PROGRAMS = \\')
            code.extend('  {0} \\'.format(program)
                for program in programs[:-1])
            code.append('  {0}'.format(programs[-1]))
        return '\n'.join(code)
    
    def macro_OBJECTS(self):
        """全オブジェクトのマクロ(OBJECTS)を宣言"""
        code = []
        objects_abspath = tuple(code_block.object_path
                for code_block in self._code_block_list)
        objects = sorted((
                relative_to(object_path, self._dir_path)
                for object_path in objects_abspath),
                key= lambda path : (path.parent, path))
        if len(objects) != 0:
            code.append('OBJECTS = \\')
            code.extend('  {0} \\'.format(object.as_posix())
                    for object in objects[:-1])
            code.append('  {0}'.format(objects[-1].as_posix()))
            code.append('')
        return '\n'.join(code)
    
    def target_all(self):
        """allを生成"""
        code = ('.PHONY: all',
                 'all:{0}$(OBJECTS)'.format(
                     '$(PROGRAMS) ' if self._exists_program else ''),)
        return '\n'.join(code)
    
    def target_clean(self):
        """cleanを生成"""
        code = ('.PHONY: cleanl',
                 'clean:',
                 '\trm -f {0}$(OBJECTS)'.format(
                     '$(PROGRAMS) ' if self._exists_program else ''),)
        return '\n'.join(code)
    
    def make_rule(self):
        """各ソースコードのルールを生成"""
        return '\n\n'.join(
            make_rule(self._dir_path, code_block, self._compiler_setting)
            for code_block in sorted(self._code_block_list))
    
    def link_rule(self):
        """各プログラムのリンクのルールを生成"""
        return '\n\n'.join(
            link_rule(self._dir_path, code_block, self._compiler_setting)
            for code_block in sorted(self._code_block_list)
            if isinstance(code_block, MainCodeBlock))
    
    def dependent_header(self):
        """各ソースコードの依存ヘッダファイルを列挙"""
        return '\n\n'.join(dependent_header(self._dir_path, code_block)
                           for code_block in sorted(self._code_block_list))
    
    def __repr__(self):
        return '{0}({1})'.format(
                   self.__class__.__name__,
                   ', '.join('{0}= {1}'.format(key, getattr(self, key))
                             for key in sorted(self.__dict__.keys())))


class RootMakeBlock(MakeBlock):
    def __init__(self, root_path, code_block_list, compiler_setting, subdirs):
        MakeBlock.__init__(self, root_path, code_block_list, compiler_setting)
        # サブディレクトリ
        self._subdirs = subdirs
    
    def make(self):
        makefile = self._dir_path.joinpath('Makefile')
        with makefile.open(mode= 'w', encoding= 'utf-8', newline= '') as file:
            if self._exists_program:
                file.write(self.macro_PROGRAMS())
                file.write('\n\n')
            file.write(self.macro_SUBDIRS())
            file.write('\n\n')
            file.write(self.macro_OBJECTS())
            file.write('\n')
            file.write(self.target_all())
            file.write('\n\n')
            file.write(self.target_clean())
            file.write('\n\n')
            if self._exists_program:
                file.write(self.link_rule())
                file.write('\n\n')
            file.write(self.make_rule())
            file.write('\n\n')
            file.write(self.dependent_header())
            file.write('\n')
    
    def macro_SUBDIRS(self):
        """サブディレクトリのマクロ(SUBDIRS)を宣言"""
        code = []
        subdirs = sorted(set(relative_to(dir_path, self._dir_path)
                for dir_path in self._subdirs
                if dir_path != self._dir_path))
        if len(subdirs) != 0:
            code.append('SUBDIRS = \\')
            code.extend('  {0} \\'.format(subdir.as_posix())
                            for subdir in subdirs[:-1])
            code.append('  {0}'.format(subdirs[-1]))
        return '\n'.join(code)
    
    def target_all(self):
        """allを生成"""
        code = ('.PHONY: all',
                'all: $(SUBDIRS) $(PROGRAMS)',
                '$(SUBDIRS): MAKE_SUBDIR',
                '\t$(MAKE) all -C $@',
                'MAKE_SUBDIR:')
        return '\n'.join(code)
    
    def target_clean(self):
        """cleanを生成"""
        code = ('.PHONY: clean',
                'clean:',
                '\trm -f $(OBJECTS) $(PROGRAMS); \\',
                '\tfor subdir in $(SUBDIRS); do \\',
                '\t    $(MAKE) clean -C $$subdir; \\',
                '\tdone')
        return '\n'.join(code)

def make_rule(dir_path, code_block, compiler_setting):
    """ルールを作成"""
    code = []
    code.append('{0}: {1}'.format(
            relative_to(code_block.object_path, dir_path).as_posix(),
            relative_to(code_block.source_path, dir_path).as_posix()))
    code.append('\t{0}'.format(
            compile_command(dir_path, code_block, compiler_setting)))
    return '\n'.join(code)

def link_rule(dir_path, main_code_block, compiler_setting):
    """オブジェクトリンクのルールを作成"""
    code = []
    code.append('{0}: \\'.format(main_code_block.program_name))
    # リンク対象オブジェクト
    objects_list = list(main_code_block.link_objects)
    #   自身のオブジェクトが含まれていなければ追加
    if not main_code_block.object_path in objects_list:
        objects_list.append(main_code_block.object_path)
    #   ソート
    objects_list = sorted((relative_to(object_path, dir_path)
            for object_path in objects_list),
            key= lambda path: (path.parent, path))
    #   書き込み
    code.extend('  {0} \\'.format(object.as_posix())
            for object in objects_list[:-1])
    code.append('  {0}'.format(objects_list[-1].as_posix()))
    code.append('\t{0}'.format(
            link_command(dir_path, main_code_block, compiler_setting)))
    return '\n'.join(code)

def compile_command(dir_path, code_block, compiler_setting):
    """コンパイル用のコマンドを作成"""
    command = []
    # コンパイラ指定
    command.append(compiler_setting.compiler)
    # 出力ファイル名指定
    command.append(compiler_setting.option.output + '$@')
    # ソースコード指定
    command.append(relative_to(code_block.source_path, dir_path).as_posix())
    # notlinkオプション
    command.append(compiler_setting.option.notlink.strip())
    # コンパイルオプション
    command.extend(compiler_setting.option_list)
    # インクルード設定
    command.extend(compiler_setting.option.include_path + include_path
        for include_path in sorted(set(compiler_setting.include_setting[lib]
            for lib in code_block.include_libs
            if  lib in compiler_setting.include_setting)))
    return ' '.join(command)

def link_command(dir_path, main_code_block, compiler_setting):
    """リンク用のコマンドを作成"""
    command = []
    # コンパイラ指定
    command.append(compiler_setting.compiler)
    # 出力ファイル名指定
    command.append(compiler_setting.option.output + '$@')
    # オブジェクト群指定
    command.append('$^')
    # ライブラリ指定
    for key, value in compiler_setting.library_setting.items():
        if key in main_code_block.include_libs:
            command.extend(compiler_setting.option.library + lib
                    for lib in value)
    return ' '.join(command)

def dependent_header(dir_path, code_block):
    """オブジェクトとヘッダファイルの依存関係を表わすコード"""
    code = []
    header_list = sorted((relative_to(header, dir_path)
            for header in code_block.include_files),
            key= lambda path: (path.parent, path))
    if len(header_list) != 0:
        code.append('{0}: \\'.format(
                relative_to(code_block.object_path, dir_path).as_posix()))
        code.extend('  {0} \\'.format(header.as_posix())
                for header in header_list[:-1])
        code.append('  {0}'.format(header_list[-1].as_posix()))
    return '\n'.join(code)

def relative_to(path, start):
    """startを基準としたpathの相対パスを返す"""
    return pathlib.Path(os.path.relpath(str(path), str(start)))
