# -*- coding: utf-8 -*-

import sys
import enum
import pathlib
from collections import OrderedDict
from .path_function import relative_to, path_to_string

class MakefileMacro(enum.Enum):
    output = '$@'
    target = '$^'

class BuildCommandMaker:
    def __init__(self, compiler_setting, verbose):
        """コンストラクタ
        compiler_setting: CommpilerSetting
        verbose         : True ot False(Default)"""
        self._compiler_setting = compiler_setting
        # include設定
        #   {target_library: include_path, ...}
        self._include_setting = OrderedDict()
        # library設定
        #   {target_library: (library_name, ...), ...}
        #   target_library == Noneならば全てに適用
        self._library_setting = OrderedDict()
        # library設定
        #   {library_name: library_dir, ...}
        self._libdir_setting  = OrderedDict()
        # verbose mode
        self._verbose = verbose
    
    def update_compiler(self, compiler_setting):
        """CommpilerSettingを更新
        commpiler_setting: CommpilerSettting"""
        self._compiler_setting = compiler_setting
    
    def add_include_setting(self, target_lib, include_path):
        """include設定を読み込む
        target_lib  : 対象となるライブラリ名
                          シーケンス or str
        include_path: includeされるpath
                          str or pathlib.Path"""
        # path設定
        path = None
        if isinstance(include_path, str):# 文字列
            path = pathlib.Path(include_path)
        else:
            path = include_path
        # lib設定
        lib_list = []
        if isinstance(target_lib, str):# 文字列
            lib_list.append(target_lib)
        elif getattr(target_lib, '__iter__', False):# シーケンス
            lib_list.extend(target_lib)
        else:
            lib_list.append(target_lib)
        # 設定
        for lib in lib_list:
            self._include_setting[lib] = path
        # 表示
        if self._verbose:
            print('Update IncludeSetting')
            for lib in lib_list:
                print('  target      :{0}'.format(lib))
                print('  include_path:{0}'.format(
                            self._include_setting[lib].as_posix()))
                print()
    
    def add_library_setting(self, target_lib, library):
        """library設定を読み込む
        target_lib : 対象となるライブラリ名
                        シーケンス or str or None
                        None ならば全てに適用
        library    : ライブラリ名
                        シーケンス or str"""
        # library名設定
        lib_list = []
        if (not isinstance(library, str)
            and getattr(library, '__iter__', False)):# シーケンス
            lib_list.extend(library)
        else:
            lib_list.append(library)
        # terget設定
        target_list = []
        if target_lib == None:# None
            target_list = None
        elif isinstance(target_lib, str):# 文字列
            target_list.append(target_lib)
        elif getattr(target_lib, '__iter__', False):# シーケンス
            target_list.extend(target_lib)
        else:
            target_list.append(target_lib)
        # 設定
        if target_list == None:# Noneの場合
            if not None in self._library_setting.keys():# 初期化
                self._library_setting[None] = []
            self._library_setting[None].extend(lib_list)
        for target in target_list:
            self._library_setting[target] = tuple(lib_list)
        # 表示
        if self._verbose:
            print('Update LibrarySetting')
            for target in target_list:
                print('  target :{0}'.format(target))
                print('  library:{0}'.format(', '.join(
                            lib for lib in self._library_setting[target])))
                print()
    # ToDo
    # def add_library_path_setting(self, target_lib, library_path):
    
    def compile_command(self, build_data, dir= None):
        """コードをコンパイルするためのコマンドを作成
        build_data:
        dir       : コマンドを実行するディレクトリ
                      Default pathlib.Path(sys.argv[0]).parent.resolve()"""
        if dir == None: dir = pathlib.Path(sys.argv[0]).parent.resolve()
        command_base = compile_command_base(self, build_data.include_libs)
        command = command_base.format(
                    output= path_to_string(build_data.object_path, dir),
                    code=   path_to_string(build_data.source_path, dir))
        return command
    
    def compile_command_makefile_macro(self, build_data, dir= None):
        """コードをコンパイルするためのコマンドを作成
            Makefileのマクロを使用
        build_data
        dir       : コマンドを実行するディレクトリ
                      Default pathlib.Path(sys.argv[0]).parent.resolve()"""
        if dir == None: dir = pathlib.Path(sys.argv[0]).parent.resolve()
        command_base = compile_command_base(self, build_data.include_libs)
        command = command_base.format(
                    output= MakefileMacro.output.value,
                    code=   path_to_string(build_data.source_path, dir))
        return command
    
    def link_command(self, build_data, dir= None):
        """オブジェクトをリンクするためのコマンドを作成
        build_data:
        dir       : コマンドを実行するディレクトリ
                      Default pathlib.Path(sys.argv[0]).parent.resolve()"""
        if dir == None: dir = pathlib.Path(sys.argv[0]).parent.resolve()
        command_base = link_command_base(self, build_data.include_libs)
        object_list = ' '.join(path_to_string(object_path, dir)
                               for object_path in build_data.link_objects)
        command = command_base.format(
                    output= path_to_string(build_data.program_path, dir),
                    target= object_list)
        return command
    
    def link_command_makefile_macro(self, build_data, dir= None):
        """オブジェクトをリンクするためのコマンドを作成
            Makefileのマクロを使用
        build_data:
        dir       : コマンドを実行するディレクトリ
                      Default pathlib.Path(sys.argv[0]).parent.resolve()"""
        if dir == None: dir = pathlib.Path(sys.argv[0]).parent.resolve()
        command_base = link_command_base(self, build_data.include_libs)
        command = command_base.format(
                    output= MakefileMacro.output.value,
                    target= MakefileMacro.target.value)
        return command

def compile_command_base(self, include_libs= []):
    """コンパイル時のcommandの基本部分を作成
    include_libs: 依存しているlibrary
    <compiler> <output_option> {output} {target} <notlink_option>
        <include_setting>"""
    command = []
    # コンパイラ
    command.append('{0}'.format(self._compiler_setting.compiler))
    # 出力ファイル名指定
    command.append('{0}{{output}}'.format(
                self._compiler_setting.option.output))
    # ソースコード指定
    command.append('{code}')
    # notlinkオプション
    command.append(self._compiler_setting.option.notlink.strip())
    # コンパイルオプション
    command.extend(self._compiler_setting.option_list)
    # インクルード設定
    include_path_list = []
    for lib in (lib for lib in include_libs
                if lib in self._include_setting.keys()):
        if not self._include_setting[lib] in include_path_list:
            include_path_list.append(self._include_setting[lib])
    command.extend('{0}{1}'.format(self._compiler_setting.option.include_path,
                                   include_path.as_posix())
                   for include_path in include_path_list)
    # comamnd結合
    return ' '.join(command)

def link_command_base(self, include_libs):
    """オブジェクトリンク時のcommandの基本部分を作成
    include_libs: 依存しているlibrary
    <compiler> <output_option> {output} {target} <library_setting>"""
    command = []
    # コンパイラ
    command.append('{0}'.format(self._compiler_setting.compiler))
    # 出力ファイル名指定
    command.append('{0}{{output}}'.format(
                self._compiler_setting.option.output))
    # オブジェクト指定
    command.append('{target}')
    # ライブラリ指定
    lib_set = set()
    for target in self._library_setting.keys():
        if target in include_libs:
            command.extend('{0}{1}'.format(
                        self._compiler_setting.option.library, lib)
                        for lib in self._library_setting[target]
                        if not lib in lib_set)
            lib_set.update(self._library_setting[target])
    #   全適用ライブラリ
    if None in self._library_setting.keys():
        command.extend('{0}{1}'.format(
                        self._compiler_setting.option.library, lib)
                        for lib in self._library_setting[None]
                        if not lib in lib_set)
        lib_set.update(self._library_setting[None])
    # comamnd結合
    return ' '.join(command)
