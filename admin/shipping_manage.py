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

        if get_param.get('action'):
            # get
            action = get_param.get('action', '')
            ids = get_param.get('id', '')
            p_lists = ['able', 'enable', 'del']
            parm = get_param

        else:
            # 判断是否执行动作,以及执行动作的id
            action = post_param.get('action', '')
            ids = post_param.get('id', '')
            p_lists = ['able', 'enable', 'del']
            parm = post_param

        if action in p_lists and ids:
            id_list = parm['id'] if isinstance(parm['id'], list) else [parm['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            if action == 'able':
                self.db.edit('shipping', {'enable': 1}, where='id in (%s)' % id_sql)  # 启用
            if action == 'enable':
                self.db.edit('shipping', {'enable': 0}, where='id in (%s)' % id_sql)  # 禁用
            if action == 'del':
                self.db.dele('shipping', where='id in (%s)' % id_sql)  # 删除
            return alert(act=2)

        where = "webid=%s" % self.kg['web']['id']

        data_list = self.db.list(
            table='shipping',
            field="*",
            where=where,
            order='id DESC',
        )

        return template(
            assign={
                'data': data_list,
            },
            function=[],
            tpl=self.kg['tpl'],
        )
