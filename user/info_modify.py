# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check= {
            'nickname': [20, "昵称长度不允许超过20个字符"],
            'phone': [20, "手机号码长度不允许超过20个字符"],
            'fax': [20, "传真号码长度不允许超过20个字符"],
            'qq': [15, "QQ号码长度不允许超过15个字符"],
            'companyweb': [100, "公司网址长度不允许超过100个字符"],
            'companyaddress': [255, "公司地址长度不允许超过255个字符"],
            'companyname': [255, "公司名称长度不允许超过255个字符"],
        }
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, html_escape, alert
        from kyger.product import Product
        post_param = self.kg['post']

        if post_param.get('action', '') == "submit":
            data = {
                "nickname": html_escape(post_param.get('nick_name', '')),
                "sex": numeric(post_param.get('sex', 2), 0, 2),
                "phone": html_escape(post_param.get('phone', '')),
                "fax": html_escape(post_param.get('fax', '')),
                "qq": html_escape(post_param.get('qq', '')),
                "companyweb": html_escape(post_param.get('companyweb', '')),
                "companyaddress": html_escape(post_param.get('companyaddress', '')),
                "companyname": html_escape(post_param.get('companyname', '')),
            }
            # 数据长度检测
            for key in self.long_check:
                if len(data[key]) > self.long_check[key][0]: return alert(msg=self.long_check[key][1], act=3)
            msg = self.db.edit('user', data, self.kg['user']['id'], 1)
            if isinstance(msg, int):
                return alert(act=2)
            else:
                return alert(msg='修改失败：%s' % msg, act=3)

        return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
