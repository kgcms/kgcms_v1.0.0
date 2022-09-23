# -*- coding:utf-8 -*-
"""后台模块添加"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {}
        # 必填检测
        self.must_input = {
            'name': '模块名称',
            'page': '页面文件'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, numeric, alert, str_cutting, html_escape
        from kyger.upload import Upload
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 动作判断
        module_id = numeric(get_param.get('id', 0), 0)
        act = "edit" if module_id else 'add'

        # 提交判断
        action = post_param.get('action')
        if action == "submit":
            if numeric(post_param.get('module', 0), 0): level, upper = (2, numeric(post_param.get('module', 0), 0))
            else: level, upper = (1, 0)
            enable = 1 if post_param.get('enable', '') else 0
            plus = 1 if post_param.get('plus', '') else 0
            insert_data = {
                'name': html_escape(post_param.get('title', '')),
                'level': level,
                'upper': upper,
                'page': html_escape(post_param.get('page', '')),
                'sort': numeric(post_param.get('sort', 0), 0),
                'enable': enable,
                'plus': plus,
                'icon': html_escape(post_param.get('icon', '')),
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(insert_data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(insert_data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)
            image = post_param.get('image')
            img = ''
            if image[0]: img = image[0]
            if image[1]: img = image[1]
            if img:  # 如果有值就存储
                up = Upload(img, self.db, self.kg, base64=True)
                up.path = 0  # 设置不创建路径
                up.filename = 'logo_{y}{mm}{dd}{hh}{ii}{ss}'  # 设置文件名形式
                msg = up.image('system/module')  # 保存文件
                insert_data['image'] = msg['url']
            if act == 'edit':
                msg = self.db.edit(table="adminpage", data=insert_data, where='`id` = %d' % module_id, limit=1)
                if msg: return alert(act='adminpage_manage?mid=%d' % upper)
                else: return alert(msg="修改失败", act=3)
            else:
                insert_data['addtime'] = int(self.kg['run_start_time'][1])
                if not img: insert_data['image'] = '',
                msg = self.db.add(table="adminpage", data=insert_data)
                if msg: return alert(act='adminpage_manage?mid=%d' % upper)
                else: return alert(msg="添加失败", act=3)
        else:
            if act == 'edit': data = self.db.list(table='adminpage', where='`id` = %d' % module_id, shift=1)
            else:
                data = {'upper': numeric(get_param.get('add', 0)), 'sort': 100}

            return template(
                assign={
                    'data': data,
                    "module": self.db.list(table='adminpage', field='id, name', where='`level` = 1', order='sort ASC'),
                    'action': act
                }
            )




