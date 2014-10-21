# -*- coding: utf-8 -*-
from .build_data    import BuildData, ProgramBuildData
from .path_function import relative_to, path_to_string, path_sort

class MakefileMacroName:
    programs = 'PROGRAMS'
    objects  = 'OBJECTS'
    subdirs  = 'SUBDIRS'

class MakefileGenerator:
    """"""
    def __init__(self,
                 dir_path,
                 build_data_list,
                 build_comamnd_maker,
                 subdir_list= tuple()):
        """コンストラクタ
        dir_path           : Makefileを生成するディレクトリ
        build_data_list    : ビルド情報
        build_command_maker: BuildCommandMaker
        subdir_list        : 派生するdirectory"""
        self._dir_path = dir_path
        self._build_data_list = build_data_list
        self._build_comamnd_maker = build_comamnd_maker
        self._subdir_list = subdir_list
    
    def exists_program(self):
        """ビルド情報にプログラム作成情報が含まれているか判定"""
        return any(isinstance(build_data, ProgramBuildData)
                   for build_data in self._build_data_list)
    
    def program_build_data_list(self):
        """ビルド情報の中からプログラム作成情報を抽出"""
        return tuple(build_data for build_data in self._build_data_list
                     if isinstance(build_data, ProgramBuildData))
    
    def make(self):
        makefile = self._dir_path.joinpath('Makefile')
        with makefile.open(mode= 'w', encoding= 'utf-8', newline= '') as file:
            file.write('\n'.join(self.make_code()))
    
    def make_code(self):
        """Makefileのコードを生成"""
        code = []
        # MACRO宣言
        code.extend(self.macro_programs())
        code.extend(self.macro_objects())
        code.extend(self.macro_subdirs())
        # all
        code.extend(self.target_all())
        # clean
        code.extend(self.target_clean())
        # link
        code.extend(self.link_rule())
        # compile
        code.extend(self.compile_rule())
        # header依存
        code.extend(self.dependent_header())
        return code
    
    def macro_programs(self):
        """実行プログラムのマクロ(PROGRAMS)を宣言"""
        code = []
        program_path_list = sorted(
                    (build_data.program_path
                     for build_data in self.program_build_data_list()),
                    key= path_sort)
        if self.exists_program():
            code.extend(macro_format(
                    MakefileMacroName.programs,
                    [path_to_string(program_path, self._dir_path)
                     for program_path in program_path_list]))
        return code
    
    def macro_objects(self):
        """全オブジェクトのマクロ(OBJECTS)を宣言"""
        code = []
        if len(self._build_data_list) != 0:
            code.extend(macro_format(
                    MakefileMacroName.objects,
                    [path_to_string(build_data.object_path, self._dir_path)
                     for build_data in self._build_data_list]))
        return code
    
    def macro_subdirs(self):
        """サブディレクトリのマクロ(SUBDIRS)を宣言"""
        code = []
        if len(self._subdir_list) != 0:
            code.extend(macro_format(
                    MakefileMacroName.subdirs,
                    [path_to_string(subdir, self._dir_path)
                     for subdir in self._subdir_list]))
        return code
    
    def target_all(self):
        """allを生成"""
        # allのtargetを得る
        target = []
        if len(self._subdir_list) != 0:
            target.append('$({0})'.format(MakefileMacroName.subdirs))
        if len(self._build_data_list) != 0:
            target.append('$({0})'.format(MakefileMacroName.objects))
        if self.exists_program():
            target.append('$({0})'.format(MakefileMacroName.programs))
        # code生成
        code = []
        code.append('.PHONY: all')
        code.extend(target_format('all', [' '.join(target)]))
        # subdirs用のcode
        if len(self._subdir_list) != 0:
            dummy_target = 'MAKE_SUBDIR'
            code.extend(target_format(
                    '$({0})'.format(MakefileMacroName.subdirs),
                    [dummy_target]))
            code.append('\t$(MAKE) all -C $@')
            code.extend(target_format(dummy_target))
        code.append('')# 空行
        return code
    
    def target_clean(self):
        """cleanを生成"""
        rm_target = []
        if len(self._build_data_list) != 0:
            rm_target.append('$({0})'.format(MakefileMacroName.objects))
        if self.exists_program():
            rm_target.append('$({0})'.format(MakefileMacroName.programs))
        # コード生成
        code = []
        code.append('.PHONY: clean')
        code.extend(target_format('clean'))
        if len(self._subdir_list) == 0:
            code.append('\trm -f {0}'.format(' '.join(rm_target)))
        else:
            code.append('\trm -f {0}; \\'.format(' '.join(rm_target)))
            code.extend(['\tfor subdir in $({0}); do \\'
                                 .format(MakefileMacroName.subdirs),
                         '\t    $(MAKE) clean -C $$subdir; \\',
                         '\tdone'])
        code.append('')# 空行
        return code
    
    def compile_rule(self):
        """各ソースコードのルールを生成"""
        code = []
        for build_data in self._build_data_list:
            code.extend(compile_rule(build_data,
                                     self._build_comamnd_maker,
                                     self._dir_path))
            code.append('')
        return code
    
    def link_rule(self):
        """各プログラムのリンクのルールを生成"""
        code = []
        # Program名でsortする
        build_data_list = sorted(
                    self.program_build_data_list(),
                    key= lambda build_data: path_sort(build_data.program_path))
        for build_data in build_data_list:
            code.extend(link_rule(build_data,
                                  self._build_comamnd_maker,
                                  self._dir_path))
            code.append('')
        return code
    
    def dependent_header(self):
        """各ソースコードの依存ヘッダファイルを列挙"""
        code = []
        for build_data in self._build_data_list:
            code.extend(dependent_header(build_data, self._dir_path))
            code.append('')
        return code
    
    def __repr__(self):
        return '{0}({1})'.format(
                   self.__class__.__name__,
                   ', '.join('{0}= {1}'.format(key, getattr(self, key))
                             for key in sorted(self.__dict__.keys())))

def macro_format(macro_name, value_list):
    """MakefileのMACRO宣言のformat
    macro_name: マクロ名
    value_list: マクロの値"""
    code = []
    if len(value_list) != 0:# 値が存在しない時は宣言しない
        code.append('{0} = \\'.format(macro_name))
        code.extend('  {0} \\'.format(value) for value in value_list[:-1])
        code.append('  {0}'.format(value_list[-1]))
        code.append('')# 末尾に空行
    return code

def target_format(target, depending_list= [], multiline= False):
    """Makefileのtarget宣言のformat
    target        : target名
    depending_list: targetが依存しているもの
    multiline     : depending_listが1つでも複数行に分割するか
                      Default False"""
    code = []
    # depending_listの値数によって分岐
    if len(depending_list) == 0:
        code.append('{0}:'.format(target))
    elif len(depending_list) == 1 and not multiline:
        code.append('{0}: {1}'.format(target, depending_list[0]))
    else:
        code.append('{0}: \\'.format(target))
        code.extend('  {0} \\'.format(depending)
                    for depending in depending_list[:-1])
        code.append('  {0}'.format(depending_list[-1]))
    return code

def compile_rule(build_data, build_command_maker, dir_path):
    """ルールを作成"""
    code = []
    # object : source_code
    code.append('{0}: {1}'.format(
            path_to_string(build_data.object_path, dir_path),
            path_to_string(build_data.source_path, dir_path)))
    # compile command
    code.append('\t{0}'.format(build_command_maker
                .compile_command_makefile_macro(build_data, dir_path)))
    return code


def link_rule(build_data, build_command_maker, dir_path):
    """オブジェクトリンクのルールを作成"""
    code = []
    # プログラム名
    code.extend(target_format(
                path_to_string(build_data.program_path, dir_path),
                [(path_to_string(object, dir_path))
                for object in build_data.link_objects]))
    # link command
    code.append('\t{0}'.format(build_command_maker
                .link_command_makefile_macro(build_data, dir_path)))
    return code

def dependent_header(build_data, dir_path):
    """オブジェクトとヘッダファイルの依存関係を表わすコード"""
    code = []
    header_list = sorted((relative_to(header, dir_path)
                          for header in build_data.include_files),
                         key= path_sort)
    if len(header_list) != 0:
        code.extend(target_format(
                path_to_string(build_data.object_path, dir_path),
                [header.as_posix() for header in header_list],
                multiline= True))
    return code
