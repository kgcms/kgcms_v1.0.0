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
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.ad import Advertise
        from kyger.product import Product
        post_param = self.kg['post']

        if post_param.get('action') == 'submit':
            payment = numeric(post_param.get('payment'), 1, 2)
            amount = numeric(post_param.get('amount'), 0)
            if amount == 0: return alert(msg='充值金额不能小于或等于0', act=3)
            if amount > 100000:
                return alert(msg='充值金额需小于十万', act=3)
            data = {
                'webid': self.kg['web']['id'],
                'type': 0,
                'oid': 'NR' + date(int(self.kg['run_start_time'][1]), '%Y%m%d%H%M%S') + str_random(3, 0, 1),
                'uid': self.kg['user']['id'],
                'pid': json2dict([0]),
                'number': json2dict([1]),
                'price': json2dict([amount]),
                'amount': amount,
                'attribute': json2dict([]),
                'status': 0,
                'dispatching': 0,
                'address': 0,
                'waybill': '',
                'freight': 0,
                'customer': 0,
                'vouch': 0,
                'payment': payment + 1,
                'message': '',
                'reply': '',
                'addtime': int(self.kg['run_start_time'][1])
            }
            msg = self.db.add('order', data)
            if isinstance(msg, int):
                url = '/api/unlimited_process?action=pay&code=%s'
                return alert(act=url % cipher(json2dict({'order_number': data['oid']}, trans=False), 1, 1800))
            else:
                return alert(msg='创建订单失败:%s' % msg, act=3)
        else:

            return template(
                function=[
                    {"category": Category(self.db, self.kg).list},
                    {"article_list": Article(self.db, self.kg).list},
                    {"article_single": Article(self.db, self.kg).single},
                    {"article_page": Article(self.db, self.kg).list_page},
                    {"ad_list": Advertise(self.db, self.kg).list},
                    {"get_cart": Product(self.db, self.kg).get_cart}
                ],
            )
