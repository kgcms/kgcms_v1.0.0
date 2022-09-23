# -*- coding:utf-8 -*-
"""后台模块管理"""


class KgcmsApi(object):
    """KGCMS框架接口"""


    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, numeric, alert, str_cutting, log
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 提交排序
        if post_param.get('action') == 'sort':
            sort = post_param.get('sort', [])
            sql = 'UPDATE %sadminpage SET sort = CASE id ' % self.db.cfg["prefix"]
            id_list = []
            for row in sort:
                sort_data = row.split(',')
                id_list.append(str(numeric(sort_data[0], 0)))
                sql += 'WHEN %s THEN %s ' % (numeric(sort_data[0], 0), numeric(sort_data[1], 0))
            self.db.run_sql(sql + 'END WHERE id IN (%s)' % (','.join(id_list)), act='edit', log=False)
            log(self.db, self.kg, 3, {"state": "SUCCESS", "table": "adminpage", "id": '[%s]' % (', '.join(id_list)), "edit_count": len(id_list)})
            return alert(act=2)
        action = get_param.get('action', '')

        if action == "del":  # 删除操作
            del_id = numeric(get_param.get('id', 0))
            row = self.db.list(table="adminpage", where='`id` = %d' % del_id)
            if not row: return alert(msg="该模块不存在", act=3)
            # 判断该模块下是否有子模块
            upper = self.db.list(table="adminpage", where='`upper` = %d' % del_id)
            if upper: return alert(msg="该模块下存在子模块", act=3)
            self.db.dele('adminpage', where="`id` = %d" % del_id, limit=1)
            return alert(act=2)
        elif action == "enable":  # 启用操作
            enable_id = numeric(get_param.get('id', 0))
            enable = numeric(get_param.get('enable', 0), 0, 1)
            row = self.db.list(table="adminpage", where='`id` = %d' % enable_id)
            if not row: return alert(msg="该模块不存在", act=3)
            self.db.edit('adminpage', data={'enable': enable}, where='`id` = %d' % enable_id,limit=1)
            return alert(act=2)
        else:
            mid = numeric(get_param.get('mid', 0), 0)
            if mid: module_data = self.db.list(table='adminpage', where='upper = %d' % mid, order='sort ASC,id ASC')
            else: module_data = self.db.list(table='adminpage', where='level = 1', order='sort ASC,id ASC')
            # 时间数据整形和字符串截取
            for var in module_data:
                var['addtime'] = date(var['addtime'], '%Y-%m-%d')
                var['name'] = str_cutting(var['name'], 21)
            # 字符串截取
            if mid:
                module = self.db.list(table='adminpage', field='id,name', where='level = 1')
                for var in module:
                    var['name'] = str_cutting(var['name'], 21)
            else: module = module_data
            return template(
                assign={
                    'data': module_data,
                    'module': module,
                    'select': mid
                }
            )

