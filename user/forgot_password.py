# -*- coding:utf-8 -*-
"""前台忘记用户名"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.user import User
        from kyger.utility import alert, is_format, md5, str_random
        from kyger.common import sms
        user = User(self.db, self.kg)
        post_param = self.kg['post']

        if post_param.get('action') == 'submit':
            password, retypePassword = (
                post_param.get('password', '').strip(), post_param.get('passwordxi', '').strip())
            # 判断密码
            if not (password and retypePassword): return alert(msg="密码不能为空", act=3)
            if password != retypePassword: return alert(msg="两次密码不一致", act=3)
            # 判断验证码
            check_code = self.kg['session'].get('info_modif_code', '')
            if not check_code: return alert(msg='请获取验证码', act=3)
            if int(self.kg['run_start_time'][1]) - self.kg['session']['info_modify_time'] > 300:
                self.del_session = True
                return alert(msg="验证码已过期", act=3)
            if md5(post_param.get('checkCode')) != check_code: return alert(msg="验证码不正确", act=3)
            # 判断手机
            check_phone = self.kg['session'].get('info_modif_phone')
            if md5(post_param.get('phone', '').strip()) != check_phone: return alert(msg='手机号有误', act=3)
            # 获取用户数据
            user_data = user.get(phone=post_param.get('phone'))
            user_data['password'] = password
            res = user.update(user_data['id'], user_data)
            if res['state'] == 'FAILURE':
                return alert(msg=res['msg'], act=3)
            else:
                self.del_session = True
                return alert(msg="修改成功", act='login')
        # 获取验证码
        elif post_param.get('action', '') == 'getcode':
            phone = post_param.get('phone', '')
            # 时间判断
            if self.kg['session'].get('info_modify_time', 0):
                code_time = int(self.kg['run_start_time'][1]) - self.kg['session']['info_modify_time']
                # 判断是否过了60s
                if code_time < 60:
                    return "短信已发送请%s秒后再试" % code_time

            # 判断电话是否存在
            if phone and is_format(phone, act='phone'):
                # 判断改手机是否被用于注册
                if not user.get(phone=phone): return "该手机没有被用于注册"
                code = str_random(4, 0, 1)
                res = sms(phone, code)
                self.set_session = {
                    'info_modify_time': int(self.kg['run_start_time'][1]),
                    'info_modif_code': md5(code),
                    'info_modif_phone': md5(phone)
                }
                return "发送成功"
            else:
                return "请输入正确的手机号码"
        else:
            return template(
                assign={},
                function=[],
                tpl=self.kg['tpl'],
            )
