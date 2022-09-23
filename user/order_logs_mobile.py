# -*- coding:utf-8 -*-
"""日志及交易记录"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None
    transaction_type = {
        1: "会员在线充值",
        2: "后台手动充值",
        3: "购买商品[消费支付]",
        4: "提交、删除或修改订单",
        5: "购买浏览权限",
        6: "操作日志"
    }

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.product import Product
        get_param = self.kg['get']

        page = numeric(get_param.get('page'), 1)
        # 交易记录
        data = self.db.list(
            table='transaction',
            field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
            where='uid=%s' % self.kg['user']['id'],
            order='addtime DESC',
            page=page,
            limit=10
        )
        if page > self.db.total_page:
            page = self.db.total_page
            data = self.db.list(
                table='transaction',
                field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                where='uid=%s' % self.kg['user']['id'],
                order='addtime DESC',
                page=page,
                limit=10
            )
        # 分页
        if self.db.total_page < 2:
            self.kg['page_html'] = ''
        else:
            from kyger.common import page_tpl
            page_html = page_tpl(page, self.db.total_page, 10, self.kg['server']['WEB_URL'])
            self.kg['page_html'] = page_html

        for row in data:
            row['type'] = self.transaction_type[row['type']]
        self.kg['order_logs'] = data

        return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
