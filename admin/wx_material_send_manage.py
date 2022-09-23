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

        if action == 'del':
            return alert(act=2)
        else:
            data = self.db.list(table="wx_material_send")
            for row in data:
                row['addtime'] = date(int(row['addtime']), '%Y-%m-%d')
                if row['status'] == 'sending':
                    ret = wechat.get_job_status(row['msg_id'])
                    if ret and not ret['errcode']:
                        msg_status = ret.get('msg_status', '')
                        row['status'] = msg_status.lower().replace("_", " ")
                        self.db.edit('wx_material_send', {'status': row['status']}, where='id = (%s)' %  row['id'])
                row['material'] = self.db.list(table='wx_material', where="media_id ='%s'" % row['media_id'], shift=1)
                if row['material']:
                    if row['material'] == 'news':
                        # 图文群发回调结果
                        result_list = self.db.list(table='wx_material_send_result', where="sid ='%s'" % row['id'])
                        if result_list:
                            for r in result_list:
                                row['result_list'][r['_index']] = r
                        # 图文素材
                        news_data = json2dict(file='temp/wx_news_data.json')
                        row['material']['articles']= news_data[row['media_id']] if row['media_id'] in news_data else []
            return template(assign={
                "data": data,
            })
