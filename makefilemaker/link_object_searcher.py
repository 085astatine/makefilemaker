# -*- coding: utf-8 -*-

"""
link_object_searcher
    依存しているヘッダファイルリスト(include_files)から
    リンク対象のオブジェクトを生成するソースコード取得する関数
"""

def replace_suffix(code_suffixs):
    def searcher(include_files):
        target_list = []
        for include_file in include_files:
            for suffix in code_suffixs:
                suffix = '.{0}'.format(suffix)
                if include_file.with_suffix(suffix).exists():
                    target_list.append(include_file.with_suffix(suffix))
                    break
        return tuple(target_list)
    return searcher
