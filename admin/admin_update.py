# -*- coding:utf-8 -*-
"""网站首页"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):

        from kyger.kgcms import numeric, alert
        from kyger.admin import Admin
        from kyger.utility import date, mk_time

        # 改/增数据初始化
        id = numeric(self.kg['get'].get('id'))
        if id:  # 修改管理员
            action = 'edit'
            user = self.db.list('admin', where=id, limit=1, shift=1)
            if not user: return alert('用户不存在', 3)
            if user['period']: user['period'] = date(user['period'], '%Y-%m-%d %H:%M')
        else:  # 添加管理员
            action = 'add'
            # 初始化
            user = {'allow': 1, 'period': 0}
            
        # 用户图像
        user['image'] = user.get('image', '/static/image/admin_default_image.png')

        # 改/增数据操作处理
        if self.kg['post'].get('action') == 'submit':  # 表单提交处理

            admin = Admin(self.db, self.kg)
            post = self.kg['post']

            # 修改用户图像, 图片上传处理
            upload_image = post.get('image', '')
            if upload_image:
                from kyger.upload import Upload
                img = Upload(upload_image, self.db, self.kg, base64=True).image('userimage/admin')
                if img['state'] == 'SUCCESS':
                    user['image'] = img['url']
                else:
                    return alert(img['msg'], 2)

            # 帐号有效期
            period = post.get('period_time', 0)
            if period: period = mk_time(period, '%Y-%m-%d %H:%M')

            allow = 1 if post.get('allow', '') == 'on' else 0

            # 增加管理员
            if action == 'add':
                id = 0
                msg = '管理员创建成功'
            # 修改管理员
            elif action == 'edit': msg = '管理员信息修改成功'
            else: return alert('参数错误', 3)

            # 增/改处理
            r = admin.update(
                id=id,
                username=post['username'].strip(),
                password=post['password'].strip(),
                phone=post['phone'].strip(),
                email=post['email'].strip(),
                image=user['image'],
                role=numeric(post['role']),
                period=period,
                allow=allow,
                notes=post['notes'],
            )
            if r['state'] == 'SUCCESS': return alert(msg, 'admin_manage')
            else: return alert(r['msg'], 3)
        else:
            from kyger.kgcms import template
            return template(assign={'action': action, 'user': user, 'role': self.db.list('role', '`id`, `name`')})



