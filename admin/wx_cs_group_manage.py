# -*- coding:utf-8 -*-
"""网站文章"""

from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'group_name': [32, "分组名称长度不允许超过32个字符"]
        }
        # 必填检测
        self.must_input = {
            'group_name': '分组名臣'
        }
    
    def __call__(self):
        from kyger.kgcms import template
        post_param = self.kg['post']

        if post_param.get('action', '') == 'submit':
            group_id = numeric(post_param.get('group_id', 0))

            image = self.kg['post'].get('img', '')  # 获取图片数据
            data = {
                'group_name': html_escape(post_param.get('title', ''))
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)
            if image:
                from kyger.upload import Upload
                up = Upload(image, self.db, self.kg, base64=True)
                up.path = 0  # 设置不创建路径
                up.filename = 'cs_group_%s' % group_id  # 设置文件名形式
                msg = up.image('client_services')  # 保存文件
                if msg['state'] == 'FAILURE': return alert(msg=msg['msg'], act=3)
                data['icon'] = msg['url']
            else:
                if not group_id:
                    data['icon'] = ''

            if group_id:
                self.db.edit('cs_group', data, group_id)
            else:
                data['cs_count'] = 0
                data['addtime'] = int(self.kg['run_start_time'][1])
                self.db.add('cs_group', data)
            return alert(act='wx_cs_group_manage')

        elif self.kg['get'].get('action', '') == 'del':
            del_id = numeric(self.kg['get'].get('id', 0), 0)
            group_data = self.db.list(table='cs_group', where=del_id, shift=1)
            if group_data.get('cs_count'): return alert(msg="该组一下有客服不能删除", act=3)
            self.db.dele('cs_group', del_id)
            return alert(act='wx_cs_group_manage')

        else:
            data = self.db.list(table='cs_group')
            return template(assign={
                "data": data
            })
