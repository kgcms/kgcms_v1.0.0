# -*- coding:utf-8 -*-
"""前台登录"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric

        get_param = self.kg['get']
        post_param = self.kg['post']

        action = get_param.get('action', '')
        id = get_param.get('id')

        if action == 'edit':
            where = "webid=%s && id=%s" % (self.kg['web']['id'], id)
            data = self.db.list(
                table='shipping',
                field="*",
                where=where,
                order='id DESC',
            )
        else:
            data = [{
                'title': '',
                'freight': 0,
                'topay': 0,
                'insure': 0,
                'description': '',
                'enable': 0
            }]
        title = post_param.get('title')

        if get_param.get('id') and post_param.get('action') == 'submit':
            where = numeric(get_param.get('id'), 0)
            data_list = {
                'title': title,
                'freight': numeric(post_param.get('freight', 0), 0),
                'topay': 1 if post_param.get('topay', 0) == 'on' else 0,
                'insure': numeric(post_param.get('insure', 0), 0),
                'description': post_param.get('description', ''),
                'enable': 1 if post_param.get('enable', 0) == 'on' else 0,
                'webid': self.kg['web']['id'],
            }
            row = self.db.edit('shipping', data_list, where)
            if row:
                return alert(msg="编辑成功", act='shipping_manage')
            else:
                return alert(msg="编辑失败", act=3)

        if title and get_param.get('id') == None:
            data_list = {
                'title': title,
                'freight': numeric(post_param.get('freight', 0), 0),
                'topay': 1 if post_param.get('topay', 0) == 'on' else 0,
                'insure': numeric(post_param.get('insure', 0), 0),
                'description': post_param.get('description', ''),
                'enable': 1 if post_param.get('enable', 0) == 'on' else 0,
                'webid': self.kg['web']['id'],
            }
            msg = self.db.add('shipping', data_list)
            if msg:
                return alert(msg="添加成功", act='shipping_manage')
            else:
                return alert(msg="添加失败", act=3)

        return template(
            assign={
                'data': data
            },
            function=[],
            tpl=self.kg['tpl'],
        )
