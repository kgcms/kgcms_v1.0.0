# -*- coding:utf-8 -*-
"""网站订单"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        post_param = self.kg['post']

        if post_param.get('action', '') == 'submit':
            material = numeric(post_param.get('material', 0))
            group = post_param.get('group', [])
            if not all((material, group)): return alert(msg="请选择分组和素材", act=4)
            fans = self.db.list(table='wx_fans', where='groupid in (%s)' % ','.join(group))
            openid_list = []
            for row in fans:
                openid_list.append(row['openid'])
            dict2json_file({'material': material, 'openid': openid_list, 'success': 0, 'failure': 0}, file='temp/push_openid.json')
            return alert(act='message_push?action=push&index=0')

        elif self.kg['get'].get('action', '') == 'push':
            from kyger.weixin import Weixin
            wechat = Weixin(self.db, self.kg)
            if not exists(url_absolute('temp/push_openid.json'), 'file'): return alert(msg="要推送的用户不存在", act=4)
            data = json2dict(file="temp/push_openid.json")
            index = numeric(self.kg['get'].get('index', 0), 0)
            res = wechat.push_material(data['openid'][index], data['material'])
            if res.get('errcode', '') == 0:data['success'] += 1
            else: data['failure'] += 1
            dict2json_file(data, file='temp/push_openid.json')
            if index == len(data['openid']) - 1:
                import os
                os.remove(url_absolute('temp/push_openid.json'))
                end = 1
            else:
                end = 0
                index += 1
            return template(
                assign={
                    'index': index,
                    'end': end,
                    'failure': data['failure'],
                    'success': data['success']
                },
                tpl='push_message.tpl',
            )
        else:
            # 本地素材
            data = self.db.list(table='material', field="id, name", where='type != 1')

            # 分组
            group = self.db.list(table='wx_group')
            return template(assign={
                "data": data,
                "group": group
            })
