# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        wechat = Weixin(self.db, self.kg)
        post_param = self.kg['post']
        action = post_param.get('action', '')

        if action == 'send':
            media_id = post_param.get('media_id', '')
            type = numeric(post_param.get('type', 0), 0, 2)
            if not all((media_id, type)): return alert(msg="没有选择素材或没有选择推送对象", act=3)
            if type == 1:
                res = wechat.wx_material_send_by_tagid('mpnews', media_id, 0)
            else:
                tag_id = numeric(post_param.get('group', 0))
                if not tag_id: return alert(msg='请选择群发组', act=3)
                res = wechat.wx_material_send_by_tagid('mpnews', media_id, tag_id, is_to_all=False)
            if res.get('errcode', '') == 0:
                import time
                data = {
                    'msg_id': res.get('msg_id', ''),
                    'msg_data_id': res.get('msg_data_id', ''),
                    'media_id': media_id,
                    'type': type,
                    'status': 'sending',
                    'addtime': int(time.time())
                }
                sid = self.db.add('wx_material_send', data)
                return alert(msg='发送成功', act=2)
            else:
                return alert(msg=res.get('errmsg', '未知错误'), act=3)
        elif action == 'preview':
            openid = post_param.get('openid', '')
            media_id = post_param.get('media_id', '')
            if not openid:return alert(msg='请输入微信号或者OPENID', act=3)
            if not media_id: return alert(msg="请选择微信素材", act=3)
            res = wechat.wx_material_preview('mpnews', media_id, openid)
            if res.get('errcode', '') == 0:
                return alert(msg='发送成功', act=2)
            else:
                return alert(msg=res.get('errmsg', '未知错误'), act=3)

        else:
            data = self.db.list(table="wx_material", where="type='news'")
            news_data = json2dict(file='temp/wx_news_data.json')
            for row in data:
                row['update_time'] = date(row['update_time'], '%Y-%m-%d %H:%M:%S')
                row['news'] = news_data[row['media_id']] if row['media_id'] in news_data else []
            group = self.db.list(table='wx_group')
            return template(assign={
                "data": data,
                "group": group,
                "id": numeric(self.kg['get'].get('id', 0))
            })
