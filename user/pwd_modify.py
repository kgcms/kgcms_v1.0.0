# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, html_escape, alert, md5
        from kyger.product import Product
        post_param = self.kg['post']

        if post_param.get('action', '') == "submit":
            data = {
                'email': html_escape(post_param.get('email', '')),
                'problem': html_escape(post_param.get('problem', '')),
                'answer': html_escape(post_param.get('answer', ''))
            }
            # 必填检测
            old_password = post_param.get('old_password', '').strip()
            if not all((old_password, data['email'])) : return alert(msg='原密码和注册邮箱必须填写', act=3)
            # 原密码验证
            if md5(md5(old_password) + md5(self.kg['user']['encryption'])) != self.kg['user']['password']:
                return alert(msg='原密码错误', act=3)
            # 选填检测
            new_password = post_param.get('new_password', '').strip()
            re_new_password = post_param.get('new_password_', '').strip()
            edit_key = False
            if new_password:
                if new_password != re_new_password:
                    return alert(msg='两次密码不一致', act=3)
                else:
                    data['password'] = md5(md5(new_password) + md5(self.kg['user']['encryption']))
                    edit_key = True

            self.db.edit('user', data, self.kg['user']['id'])
            if edit_key: return alert(msg="密码已修改需要重新登录", act='/user/login?action=logout')
            else: return alert(act=2)

        return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
