# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.kgcms import template
from kyger.utility import date, alert, numeric
from time import time


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):

        did = numeric(self.kg['get'].get('del', 0))
        if did:
            if did == self.kg['admin']['id']:
                return alert('当前用户已登录，无法删除', 'admin_manage')
            else:
                self.db.dele('admin', did, 1)
                return alert(act='admin_manage')
        # 后台管理员数据
        data = self.db.list(
            table='`{pr}admin` a left join `{pr}role` b on a.`role` = b.`id`',
            field='a.*, b.`name` as `role_name`',
            order='`a`.`frequency` DESC, `a`.`id` ASC',
            where='a.`webid`=%s' % self.kg['web']['id']
        )
        # 日志数据
        near_time = self.db.list(
            table='log',
            field='max(addtime), adminid',
            where='1 group by adminid',
        )
        # 最近两次登录
        login_list = self.db.list(
            table='log',
            field='ip, adminid',
            where=' type=6 && adminid !=0',
            order='addtime DESC'
        )
        print(login_list)
        login_dir = {}
        for row in login_list:
            if row['adminid'] not in login_dir: login_dir[row['adminid']] = [row['ip']]
            else: login_dir[row['adminid']].append(row['ip'])

        res = {}
        for row in near_time:
            res[str(row['adminid'])] = row['max(addtime)']
        for row in data:
            row['near'] = res.get(str(row['id']), '')  # 添加最近登录时间
            if login_dir.get(row['id'], ''):
                if len(login_dir[row['id']]) > 1:
                    row['login_ip'] = [login_dir[row['id']][0], login_dir[row['id']][1]]
                else:
                    row['login_ip'] = [login_dir[row['id']][0], '-- --']
            else:
                row['login_ip'] = ['-- --', '-- --']

        return template({
            'admin_list': data,
            'time': int(time())
        }, function=[date])
