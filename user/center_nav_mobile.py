# -*- coding:utf-8 -*-
"""手机端会员中心"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date
        from kyger.product import Product


        return template()
