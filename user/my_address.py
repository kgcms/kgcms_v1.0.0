# -*- coding:utf-8 -*-
"""收货地址管理"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert
        from kyger.product import Product
        get_param = self.kg['get']
        action = get_param.get('action', '')

        if action in ['del', 'default']:
            act_id = numeric(get_param.get('id', 0), 0)
            if action == 'del':
                self.db.dele("address", where='id=%s && uid=%s' % (act_id, self.kg['user']['id']))
                # self.db.edit('address', {'del': 1}, 'id=%s && uid=%s' % (act_id, self.kg['user']['id']))
            if action == 'default':
                msg = self.db.edit('address', {'default': 1}, 'id=%s && uid=%s' % (act_id, self.kg['user']['id']))
                if msg: self.db.edit('address', {'default': 0}, 'uid=%s && id != %s' % (self.kg['user']['id'], act_id))
            return alert(act=2)
        else:
            page = numeric(get_param.get('page', 1), 1)
            self.kg['address'] = self.db.list(
                table='address',
                where='uid=%s && del=0' % self.kg['user']['id'],
                page=page,
                limit=10
            )
            if page > self.db.total_page:
                page = self.db.total_page
                self.kg['address'] = self.db.list(
                    table='address',
                    where='uid=%s && del=0' % self.kg['user']['id'],
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
            return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
