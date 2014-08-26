# -*- coding: utf-8 -*-

from collections import namedtuple, OrderedDict

CompilerOption = namedtuple('CompilerOption',
    ('notlink', 'output', 'include_path', 'library', 'library_path'))
"""コンパイラのオプション
  コンパイルのみ実行 出力名設定 ライブラリ関連のみ
notlink
output
include_path
libraly
libraly_path
"""

GCCCompilerOption = CompilerOption(
    notlink      = '-c ',
    output       = '-o ',
    include_path = '-I ',
    library      = '-l ',
    library_path = '-L ',)

class CompilerSetting:
    """コンパイラの設定
    compiler             : コンパイラ名
    standard_option      : ビルド時に必要なオプション
    option_list          : コンパイル時に指定するオプション
    include_setting      : 
    library_setting      : 
    library_path_setting : 
    """
    def __init__(self):
        self.compiler    = 'g++'
        self.option      = GCCCompilerOption
        self.option_list = []
    
    def define_standard_option(self,
            notlink, output, include_path, library, library_path):
        """CompilerOptionを変更"""
        self.option = CompilerOption(
            notlink, output, include_path, library, library_path)
    
