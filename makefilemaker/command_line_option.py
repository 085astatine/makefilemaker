# -*- coding: utf-8 -*-

import sys, argparse
from .link_object import LinkObjectMode

def option_parser():
    parser = basic_option()
    link_object_option(parser)
    return parser

def basic_option():
    """基本となるオプション"""
    parser = argparse.ArgumentParser()
    # verbose mode
    parser.add_argument(
        '-v', '--verbose',
        dest= 'verbose', action='count', default= 0,
        help= 'add verbose level, max level is 3')
    # test mode
    parser.add_argument(
        '-t', '--test',
        dest= 'test', action= 'store_true', default= False,
        help= 'test mode')
    # add compile option
    parser.add_argument(
        '-c', nargs= argparse.REMAINDER,
        dest= 'compile_option', default= [],
        help= 'add to the compile options all elements of the following');
    # version
    parser.add_argument(
        '--version',
        action='version', version= 'beta')
    # 出力
    return parser

def link_object_option(parser):
    # LinkObjectMode
    parser.add_argument('--mode', 
                        dest= 'link_object_mode',
                        action= LinkObjectModeSelect,
                        default= None,
                        choices= [mode.value for mode in LinkObjectMode],
                        help= 'select link object mode')
    # 解析ログ
    parser.add_argument('--log',
                        dest= 'log_file',
                        action= 'store',
                        default= None,
                        metavar= 'LOGFILE',
                        help= 'set the file to take the log')

class LinkObjectModeSelect(argparse.Action):
    def __call__(self, parser, namespace, value, option_string= None):
        """"parser       : ArgumentParser object
        namespace    : parse_args() が返す Namespace
        values       : 関連付けられたコマンドライン引数
        option_string: このアクションを実行したオプション文字列"""
        for mode in LinkObjectMode:
            if mode.value == value:
                setattr(namespace, self.dest, mode)
                break
        else:
            default_mode = LinkObjectMode.Search,
            setattr(namespace, self.dest, default_mode)
