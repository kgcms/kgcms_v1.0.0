# -*- coding:utf-8 -*-
"""后台登录"""


class KgcmsApi(object):
    """接口API"""
    kg = db = None
    
    login_attempt = 5  # 登录尝试次数
    login_interval = 30  # 超过尝试次数后多久不能登录

    def __call__(self):
        from kyger.utility import alert, url_code, log, str_replace
        
        if self.kg['get'].get('action', '') == 'logout' and self.kg['session'].get('KGCMS_ADMIN_ID', ''):  # 退出登录
            self.del_session = True
            self.del_cookie = 'KGCMS_SESSION_ID'
            log(self.db, self.kg, 6, {'state': 'SUCCESS', 'id': self.kg['admin']['id'], 'action': 'logout'})
            return alert(act='login')

        if self.kg['admin']['id']: return alert(act='./')  # 已登录

        espec = ["'", '"', "/", "\\", "<", ">", " "]
        username = str_replace(self.kg['post'].get('username', '').strip(), espec, "")
        password = str_replace(self.kg['post'].get('password', '').strip(), espec, "")
        
        if username and password:  # 登录
            from kyger.admin import Admin
            admin_class = Admin(self.db, self.kg)
            # 检测同一用户登录错误的次数
            login_count = admin_class.login_freq(ip=self.kg['server']['HTTP_ADDR'], minute=self.login_interval)
            if login_count <= self.login_attempt:  # 登录失败次数是否超出规定
                login = admin_class.login(username, password)

                # 登录日志
                lkg = {
                    "web": {"id": self.kg["web"]["id"]},
                    "server": {"WEB_URL": self.kg['server']['WEB_URL'], "HTTP_ADDR": self.kg['server']['HTTP_ADDR']},
                    "admin": {"id": login.get("id", 0)},
                    "session": {
                        "KGCMS_ADMIN_LOGIN_ID": login["loginid"],
                        "KGCMS_USER_LOGIN_ID": self.kg["session"].get("KGCMS_USER_LOGIN_ID", ""),
                    },
                    "user": {"id": self.kg.get('user', {}).get('id', 0)},
                    "run_start_time": self.kg['run_start_time'],
                }
                log(self.db, lkg, 6, login)
                
                if login['state'] == 'SUCCESS':  # 登录成功
                    self.set_session = {
                        'KGCMS_ADMIN_ID': login['id'],  # admin ID
                        'KGCMS_ADMIM_FREQUECY': login['frequency'],  # 登录次数
                        'KGCMS_ADMIN_LOGIN_ID': username,  # 登录帐号: phone|email|username
                    }
                    
                    goto = self.kg['get'].get('goto', None)
                    if goto:
                        return alert(act=url_code(goto))
                    else:
                        return alert(act='./')
                else:  # 登录失败
                    temp = self.login_attempt - login_count  # 剩余尝试次数
                    if temp: return alert(self.kg['lang'][19] % (login['msg'], temp))
                    else: return alert(self.kg['lang'][18] % (login['msg'], self.login_interval))
            else:  # 规定的时间内输入密码错误次数太多
                return alert(self.kg['lang'][20] % self.login_interval)
        else:
            from kyger.kgcms import template
            return template()
