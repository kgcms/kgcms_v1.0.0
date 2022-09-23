# -*- coding:utf-8 -*-
"""前台登录"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    login_attempt = 5  # 登录尝试次数
    login_interval = 30  # 超过尝试次数后多久不能登录

    def __init__(self):
        pass

    def __call__(self):
        from kyger.parser_ini import Config
        from kyger.kgcms import template
        from kyger.utility import alert, url_code, log, dict2json_file, put_contents

        # put_contents("temp/post.json", data={"post":self.kg['post'],"get":self.kg['get']}, mode='a', charset="utf-8")

        if self.kg['get'].get('action', '') == 'logout' and self.kg['session'].get('KGCMS_USER_ID', ''):  # 退出登录
            self.del_session = True
            self.del_cookie = 'KGCMS_SESSION_ID'
            log(self.db, self.kg, 11, {'state': 'SUCCESS', 'id': self.kg['user']['id'], 'action': 'logout'})
            return alert(act='/user/')

        # if self.kg.get('user', {}).get('id', 0):
        #     dict2json_file({"123":"已登录"}, file=("temp/2.json"))
        #     agent = self.kg['server']['HTTP_USER_AGENT']
        #     ispc = tuple(filter(lambda x: x in agent, ["Windows NT", "Macintosh"]))
        #     if ispc:
        #         dict2json_file({"123": "已登录"}, file=("temp/2_1.json"))
        #         return alert(act='/user/center')
        #     else:
        #         dict2json_file({"123": "已登录"}, file=("temp/2_2.json"))
        #         return alert(act='/user/center_nav_mobile')  # 已登录

        username = self.kg['post'].get('username', '').strip()
        password = self.kg['post'].get('password', '').strip()
        if username and password:  # 登录
            from kyger.user import User
            user_class = User(self.db, self.kg)
            # 检测同一用户登录错误的次数
            login_count = user_class.login_freq(ip=self.kg['server']['HTTP_ADDR'], minute=self.login_interval)
            if login_count <= self.login_attempt:  # 登录失败次数是否超出规定
                login = user_class.login(username, password)
                # 登录成功添加积分(12小时间隔)
                if login['state'] == 'SUCCESS':  # 登录成功
                    last = self.db.list(
                        table='log',
                        where="type=11 && userid=%s" % login['id'],
                        order="addtime DESC",
                        shift=1
                    )
                    user_config = Config('config/settings.ini').get('user')
                    if int(self.kg['run_start_time'][1]) - last.get('addtime', 0) > 43200:
                        r = self.db.list(table='user', where=login['id'], shift=1)
                        self.db.edit('user', {'scores': r['scores'] + user_config['login_scores']}, login['id'])

                    # 登录日志
                    lkg = {
                        "web": {"id": self.kg["web"]["id"]},
                        "server": {"WEB_URL": self.kg['server']['WEB_URL'], "HTTP_ADDR": self.kg['server']['HTTP_ADDR']},
                        "admin": {"id": self.kg["session"].get("KGCMS_ADMIN_ID", 0)},
                        "session": {
                            "KGCMS_ADMIN_LOGIN_ID": self.kg["session"].get("KGCMS_ADMIN_LOGIN_ID", ""),
                            "KGCMS_USER_LOGIN_ID": login["loginid"],
                        },
                        "user": {"id": login.get("id", 0)},
                        "run_start_time": self.kg['run_start_time'],
                    }
                    log(self.db, lkg, 11, login)

                # if login['state'] == 'SUCCESS':  # 登录成功
                    self.set_session = {
                        'KGCMS_USER_ID': login['id'],  # user ID
                        'KGCMS_USER_FREQUECY': login['frequency'],  # 登录次数
                        'KGCMS_USER_LOGIN_ID': username,  # 登录帐号: phone|email|username
                    }

                    # goto = self.kg['get'].get('goto', None)
                    # if goto:
                    #     dict2json_file({"123": "已登录"}, file=("temp/7.json"))
                    #     return alert(act=url_code(goto))
                    # else:
                    dict2json_file({"123": "已登录"}, file=("temp/6.json"))
                    agent = self.kg['server']['HTTP_USER_AGENT']
                    ispc = tuple(filter(lambda x: x in agent, ["Windows NT", "Macintosh"]))
                    if ispc:
                        return alert(act='./')
                    else:
                        return alert(act='./center_nav_mobile')
                else:  # 登录失败
                    temp = self.login_attempt - login_count  # 剩余尝试次数
                    if temp:
                        return alert(self.kg['lang'][14] % (login['msg'], temp))
                    else:
                        return alert(self.kg['lang'][13] % (login['msg'], self.login_interval))
            else:  # 规定的时间内输入密码错误次数太多
                return alert(self.kg['lang'][15] % self.login_interval)
        else:
            return template()


