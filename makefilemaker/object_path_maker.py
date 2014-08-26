# -*- coding: utf-8 -*-

"""
object_name_maker
  source_pathからオブジェクトファイル名を生成する関数
  source_path ソースコードのパス

object_dir_maker
  root_pathとsource_pathからobject_pathを生成する関数
  root_path   実行ディレクトリ pathlib.Path(sys.argv[0]).parent
  source_path ソースコードのパス
"""

def same_source_name(suffix):
    """ソースコードの拡張子を指定した拡張子に変更する"""
    def maker(source_path):
        return source_path.with_suffix('.{0}'.format(suffix)).name
    return maker

def same_source_dir(dirname= '.'):
    """ソースコードと同じディレクトリに作成
    そのディレクトリ内の特定のディレクトリへと指定可"""
    def maker(root_path, source_path):
        return source_path.parent.joinpath(dirname)
    return maker

def specific_directory(dirname):
    """rootディレクトリの特定のディレクトリを基として
    ソースコードのディレクトリと同じ構造になるよう設定"""
    def maker(root_path, source_path):
        return root_path.joinpath(dirname).joinpath(
                   source_path.parent.relative_to(root_path))
    return maker
