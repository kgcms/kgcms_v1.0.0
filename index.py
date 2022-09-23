#! /usr/bin/env python
# -*- coding:utf-8 -*-
""" 项目启动入口 """
import sys, os.path
from wsgiref.simple_server import make_server
sys.path.append(os.path.dirname(__file__))
from kyger.kgcms import App

if __name__ == '__main__':
    httpd = make_server('', 8000, App())
    httpd.serve_forever()
