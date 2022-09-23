# -*- coding:utf-8 -*-
"""会员添加"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric, json2dict, html_escape, str_random, md5, ip2address
        from kyger.user import User
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = post_param.get('action', '')
        # 添加/修改判断
        act_id = numeric(get_param.get('id', 0), 0)
        act = 'edit' if act_id else 'add'

        # 提交数据
        if action == "submit":
            data = {
                'image': '',
                'username': post_param.get('user-name', '').strip(),
                'email': post_param.get('email', '').strip(),
                'qq': post_param.get('qq', '').strip(),
                'problem': html_escape(post_param.get('contact', '')),
                'answer': html_escape(post_param.get('daan', '')),
                'companyname': html_escape(post_param.get('companyname', '')),
                'companyweb': html_escape(post_param.get('url', '')),
                'companyaddress': html_escape(post_param.get('site', '')),
                'audit': numeric(post_param.get('audit', 0), 0, 2),
                'type': numeric(post_param.get('type', 0), 0, 1),
                'sex': numeric(post_param.get('sex', 0), 0, 2),
                'money': numeric(post_param.get('balance', 0)),
                'usemoney': numeric(post_param.get('energy', 0)),
                'scores': numeric(post_param.get('integral', 0), 0),
                'nickname': html_escape(post_param.get('nickname', '')),
                'phone': html_escape(post_param.get('phone', '')),
                'fax': html_escape(post_param.get('fax', '')),
                'frequency': numeric(post_param.get('logins', 0), 0),
                'joinip': html_escape(post_param.get('registered', '')),
                'effective': numeric(post_param.get('effective', 0), 0, 1),
            }
            # ip地址
            ip_data = ip2address(self.db, data['joinip']) if ip2address(self.db, data['joinip']) else {}
            data['joinaddress'] = ip_data.get('province', '') + ip_data.get('city', '')
            # 密码
            password = [post_param.get('password', '').strip(), post_param.get('password_', '').strip()]
            # 会员级别
            level = numeric(post_param.get('level', 0), 0)
            if not level: return alert(msg='请选择会员等级', act=3)
            # 判断用户名是否被使用
            username_data = self.db.list(table='user', field='id', where='username="%s"' % data['username'], shift=1)
            if username_data and act == "add": return alert(msg='该用户名已存在', act=3)
            if username_data and username_data['id'] != act_id: return alert(msg='该用户名已存在', act=3)
            if act == "add":
                data['openid'] = self.kg['session'].get('openid', '')
                if not password[0]: return alert(msg='密码不能为空', act=3)
                if not password[1] or password[0] != password[1]: return alert(msg='两次输入的密码不一致', act=3)
                data['encryption'] = str_random(8, 3, 1)  # 加密字符串
                data['password'] = md5(md5(password[0]) + md5(data['encryption']))  # 加密密码
                data['level'] = json2dict([level])  # 会员组
                data['jointime'] = int(self.kg['run_start_time'][1])  # 创建时间
                msg = self.db.add('user', data)
                if not msg:
                    return alert(msg='添加失败', act=3)
                else:
                    return alert(act='user_manage')
            else:
                # 密码判断
                if password[0] and password[0] != password[1]: return alert(msg="两次输入的密码不一致", act=3)
                if password[0] and password[0] == password[1]:
                    data['encryption'] = str_random(8, 3, 1)  # 加密字符串
                    data['password'] = md5(md5(password[0]) + md5(data['encryption']))  # 加密密码
                # 用户组判断
                level_edit = numeric(post_param.get('level_edit', 0), 0)
                if level != level_edit:
                    level_source = eval(post_param.get('level_source'))
                    level_source[level_source.index(level_edit)] = level
                    data['level'] = json2dict(level_source)
                msg = self.db.edit('user', data, act_id)
                if not msg:
                    return alert(msg='修改失败', act=3)
                else:
                    return alert(act='user_manage')

        # 获取页面数据
        else:
            if act == "edit":
                act_data = User(self.db, self.kg).get(act_id)
            else:
                act_data = {}
            data = {
                'username': act_data.get('username', ''),
                'type': act_data.get('type', ''),
                'email': act_data.get('email', ''),
                'qq': act_data.get('qq', ''),
                'sex': act_data.get('sex', 2),
                'nickname': act_data.get('nickname', ''),
                'money': act_data.get('money', 0.00),
                'usemoney': act_data.get('usemoney', 0.00),
                'scores': act_data.get('scores', 0),
                'level': act_data.get('level', []),
                'problem': act_data.get('problem', ''),
                'answer': act_data.get('answer', ''),
                'companyname': act_data.get('companyname', ''),
                'companyweb': act_data.get('companyweb', ''),
                'companyaddress': act_data.get('companyaddress', ''),
                'phone': act_data.get('phone', ''),
                'fax': act_data.get('fax', ''),
                'frequency': act_data.get('frequency', 0),
                'joinip': act_data.get('joinip', ''),
                'jointime': act_data.get('date', date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M:%S')),
                'audit': act_data.get('audit', 0),
                'effective': act_data.get('effective', 0),
                'loginip': act_data.get('loginip', []),
                'logintime': act_data.get('logintime', []),
            }
            rank = self.db.list(table='rank', field='id, rankname', where='webid = %s' % self.kg['web']['id'])
            # 最近两次登录的ip和登录时间
            near_time = self.db.list(
                table='log',
                field='addtime',
                where='userid=%s' % self.kg['user']['id'],
                order='addtime DESC',
                limit='0,2'
            )
            # 最近两次登录
            login_list = self.db.list(
                table='log',
                field='ip',
                where='userid=%s group by ip,addtime' % act_id,
                order='addtime DESC',
                limit='0,2'
            )
            login_time = []
            login_ip = []
            if near_time:
                for i in range(len(near_time)): login_time.append(date(near_time[i]['addtime'], '%Y-%m-%d %H:%M:%S'))
            if login_list:
                for i in range(len(login_list)): login_ip.append(login_list[i]['ip'])
            data['login_time'] = ' / '.join(login_time)
            data['login_ip'] = ' / '.join(login_ip)
            return template(assign={'data': data, 'rank': rank})
