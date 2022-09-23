# -*- coding:utf-8 -*-
"""ueditor编辑器调用演示"""

from kyger.kgcms import template
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    def __init__(self):
        pass

    def __call__(self):
        
        content = html_escape('<script>alert("支持脚本")</script>  测试<font color="#FF0000">数据</font>', False)
        
        return template({"data": {"content": content}})
