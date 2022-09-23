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
        from kyger.weixin import Weixin
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 添加分组
        if post_param.get("action", '') == "add":
            wechat = Weixin(self.db, self.kg)
            if not post_param.get('title', ''): return alert(msg="分组名不能为空", act=3)
            if len(post_param['title']) > 30: return alert(msg="分组名不能超过30个字符", act=3)
            wechat.new_group(post_param.get('title', ''))
            return alert(act=2)

        # 修改分组
        elif post_param.get("action", '') == "update":
            wechat = Weixin(self.db, self.kg)
            if not post_param.get('title', ''): alert(msg="分组名不能为空", act=3)
            if len(post_param['title']) > 30: return alert(msg="分组名不能超过30个字符", act=3)
            group_id = numeric(post_param.get('group_id', ''))
            if group_id < 3: return alert(msg="默认分组不允许修改", act=3)
            wechat.update_group(group_id, post_param.get('title', ''))
            return alert(act=2)

        # 获取分组信息
        else:
            data = self.db.list(table="wx_group")

            return template(assign={
                "data": data
            })
