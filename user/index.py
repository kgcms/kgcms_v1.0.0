# -*- coding:utf-8 -*-
"""会员中心首页"""

from kyger.utility import alert


class KgcmsApi(object):
    """KGCMS框架接口"""
    
    def __init__(self):
        pass
    
    def __call__(self):
        return alert(act="/user/center")


