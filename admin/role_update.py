# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, json2dict, html_escape
        config = json2dict(file='config/admin_role.json', force=True)  # 读取配置文件

        # 1.获取数据
        get_paramm = self.kg['get']
        post_param = self.kg['post']

        # 2.动作判断
        roleid = numeric(get_paramm.get('roleid', 0), 0)
        act = 'edit' if roleid else 'add'

        # 3.提交判断
        if post_param.get('action', '') == "submit":
            data = {
                'name': html_escape(post_param.get('name', '')),
                'description': html_escape(post_param.get('description', '')),
            }  # 数据库添加或修改的数据
            if post_param.get('permission', '') == "on":  # 所有权限
                data['type'] = 99  # 超级管理员权限
                data['permission'] = json2dict({})
            else:  # 非所有权限
                data['type'] = 0  # 自定义权限
                permission = {}
                for module in config:
                    contain_dict = dict()
                    if module in post_param:
                        contain_dict['list'] = post_param[module] if isinstance(post_param[module], list) else [post_param[module]]
                    else:
                        contain_dict['list'] = []  # 没有则空列表
                    if ('%s_open' % module) in post_param and post_param.get('%s_open' % module, '') == 'on':  # 模块许可
                        contain_dict['open'] = 1
                    else: contain_dict['open'] = 0
                    permission[module] = contain_dict
                data['permission'] = json2dict(permission)

            if act == "edit":  # 编辑
                rows = self.db.edit('role', data, where='`id` = %d' % roleid)
                if rows: return alert(msg="修改成功", act="role_manage")
                else: return alert(msg="修改失败", act=3)
            if act == "add":  # 添加
                data['webid'] = numeric(self.kg['web']['id'], 0)
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('role', data)
                if msg: return alert(msg="添加成功", act="role_manage")
                else: return alert(msg="添加失败", act=3)

        # 非提交数据
        else:
            if act == "edit":
                role_data = self.db.list(table='role', where=roleid, shift=1)  # 获取该ID的数据
                if not role_data: return alert(msg="该角色不存在", act=3)
                role_data['permission'] = json2dict(role_data['permission'])
            else: role_data = {}
            data = {
                "name": role_data.get("name", ''),
                "description": role_data.get("description", ''),
                "type": role_data.get("type", 99),
                "permission": role_data.get("permission", {}),
            }
            return template(assign={'data': data, 'module': config, 'action': act})


