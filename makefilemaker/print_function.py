# -*- coding: utf-8 -*-

def print_indented(string, indent):
    """複数行に跨る文字列をindentして表示する"""
    for string_line in str(string).split('\n'):
        print((' ' * indent) + string_line)
