# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.common import permission
        from kyger.kgcms import template
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc
        misc = Misc(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']

        return template(
            function=[
                {"category": Category(self.db, self.kg).list},
                {"article_list": Article(self.db, self.kg).list},
                {"article_single": Article(self.db, self.kg).single},
                {"article_page": Article(self.db, self.kg).list_page},
                {"product_page": Product(self.db, self.kg).list_page},
                {"product_single": Product(self.db, self.kg).single},
                {"ad_list": Advertise(self.db, self.kg).list},
                {"navigate_list": misc.navigate},
                {"app": misc.app},
                {"get_cart": Product(self.db, self.kg).get_cart},
            ]
        )
