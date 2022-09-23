# -*- coding:utf-8 -*-
"""角色管理"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert
        from kyger.role import Role
        role = Role(self.db, self.kg)
        get_param = self.kg['get']

        # 动作
        action = get_param.get('action', '')
        if action == 'del' and 'id' in get_param:  # 删除操作
            role_id = numeric(get_param.get('id', 0), 0)
            # 删除检测
            role_list = self.db.list(table='admin', field='id', where='`role` = %d' % role_id)
            if role_list: return alert(msg="无法删除，该角色组下有%d个用户" % len(role_list), act="role_manage")
            else:
                self.db.dele(table='role', where=role_id, log=True)
                return alert(act=2)

        data = role.list(row=50)  # 取50条数据
        return template(assign={'data': data})
