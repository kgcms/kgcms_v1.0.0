# -*- coding:utf-8 -*-
"""系统应用管理页面"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import alert, numeric, json2dict

        url_param = self.kg['get']  # 获取get数据
        post_param = self.kg['post']
        # 判断是否为操作
        action = url_param.get('action', '')
        if action in ['set_default', 'del', 'enable', 'unenable']:
            webid = numeric(url_param.get('id', 0), 0)
            if action == 'set_default':
                row = self.db.edit('web', {'default': 1}, where=webid, limit=1)  # 修改默认
                if row:
                    self.db.edit('web', {'default': 0}, where='`id` != %d' % webid)  # 其他修改为非默认
                return alert(act="app_manage")
            if action == 'enable':
                self.db.edit('web', {'enable': 1}, where=webid, limit=1)  # 修改启用
                return alert(act="app_manage")
            if action == 'unenable':
                self.db.edit('web', {'enable': 0}, where=webid, limit=1)  # 修改
                return alert(act="app_manage")
            if action == 'del':
                category = self.db.list(table='category', field='id', where='`webid` = %d' % webid)
                if category: return alert(msg="该应用下存在栏目，无法删除", act=3)
                self.db.dele(table='web', where=webid, log=True)
                return alert(act=2)
        elif post_param.get('action', '') == 'sort':
            sort = post_param.get('sort', [])
            sql = 'UPDATE %sweb SET sort = CASE id ' % self.db.cfg["prefix"]
            id_list = []
            for row in sort:
                sort_data = row.split(',')
                id_list.append(str(numeric(sort_data[0], 0)))
                sql += 'WHEN %s THEN %s ' % (numeric(sort_data[0], 0), numeric(sort_data[1], 0))
            self.db.run_sql(sql + 'END WHERE id IN (%s)' % (','.join(id_list)), 'edit', log=False)
            return alert(act=2)

        # 获取数据
        data = self.db.list(table='web', order='`id` ASC')
        for var in data:
            var['domain'] = json2dict(var['domain'])
            var['template_auto'] = json2dict(var['template_auto'])
        return template(assign={'data': data})


