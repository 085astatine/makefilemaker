# -*- coding: utf-8 -*-

import pathlib
import subprocess
import shlex
from .functions import object_to_include_libs
from ..build_data import ProgramBuildData

def build_test(build_data, build_command_maker, log_file= subprocess.DEVNULL):
    """ビルド情報を基にlinkコマンドを作成し実行
    build_data: ProgramBuildData
    return return_code 0 -> 正常終了
                       1 -> 異常終了"""
    command = build_command_maker.link_command(build_data)
    if log_file != subprocess.DEVNULL:
        log_file.write('{0}\n\n'.format(command))
    try:
        subprocess.check_output(shlex.split(command),
                                stderr= subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return_code = error.returncode
        if log_file != subprocess.DEVNULL:
            log_file.write('{0}\n\n'.format(error.output.decode('utf-8')))
    else:
        return_code = 0
    return return_code

def make_build_test_data(object_list, build_data_list):
    """ビルドテスト用のProgramBuildDataを作成"""
    # 関連する全ライブラリを取得
    build_data = ProgramBuildData(
                None, # source_path
                None, # object_path
                None, # include_files,
                object_to_include_libs(object_list, build_data_list),
                pathlib.Path('a.out'),
                object_list)
    return build_data
