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

        # 权限检测
        cate = self.db.list(table='category', where='template="%s.tpl"' % self.kg['current_path'][-1], shift=1)
        self.kg['get']['cid'] = cate['id']
        res = permission(self.db, self.kg)
        if res['status'] == 1:
            # return alert(msg='没有访问权限', act=3)
            if self.kg['user']['id'] != 0:
                return alert(msg='没有相关权限', act=3)
            else:
                return alert(act="%s/user/login" % self.kg['server']['HTTP_HOST'])
        elif res['status'] == 404:
            return notfound_404()
        else:
            data = res['data']

        if data['upper']:
            up_cate = self.db.list(
                table='category',
                field='id,title',
                where=data['upper'][-1],
                shift=1
            )
            up_data = (up_cate['title'], up_cate['id']) if up_cate else ('', 0)
            data['up_name'], data['up_id'] = up_data
        else:
            data['up_name'], data['up_id'] = ('', 0)
        self.kg['category'] = data

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
