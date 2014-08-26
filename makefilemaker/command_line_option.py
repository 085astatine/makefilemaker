# -*- coding: utf-8 -*-

import sys, argparse

def basic_option():
    """基本となるオプション"""
    parser = argparse.ArgumentParser()
    # verbose mode
    parser.add_argument(
        '-v', '--verbose',
        dest= 'verbose', action='count', default= 0,
        help= 'add verbose level')
    # test mode
    parser.add_argument(
        '-t', '--test',
        dest= 'test', action= 'store_true', default= False,
        help= 'test mode')
    # version
    parser.add_argument(
        '--version',
        action='version', version= 'beta')
    # 出力
    return parser

def parse_option(option_parser, argv= None):
    """オプションをparseする"""
    if argv == None: argv = sys.argv[1:]
    option = option_parser.parse_args(argv)
    return option
