# -*- coding: utf-8 -*-

from ..path_function import path_to_string, path_sort

def get_source_code_list(main_code, code_manager):
    """link対象となりうるソースコード一覧を取得"""
    main_code_list = code_manager.main_code
    source_code_list = []
    source_code_list.append(main_code)
    source_code_list.extend(code for code in code_manager.source_code
                            if not code in main_code_list)
    source_code_list.sort(key= path_sort)
    return tuple(source_code_list)

def source_to_object(source_code_list, build_data_list):
    """ソースコードのpathをオブジェクトのpathに変換"""
    return tuple(sorted((build_data_list[source].object_path
                         for source in source_code_list),
                        key= path_sort))

def object_to_include_libs(object_list, build_data_list):
    """object listの関連する全ライブラリを取得"""
    lib_set = set()
    for code in build_data_list.keys():
        if build_data_list[code].object_path in object_list:
            lib_set.update(build_data_list[code].include_libs)
    return tuple(sorted(lib_set))
