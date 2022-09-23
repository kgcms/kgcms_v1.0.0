# -*- coding:utf-8 -*-
"""网站订单"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.user import User
        from kyger.utility import numeric, alert, url_query2dict, url_update, date, str_random, numeric
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = get_param.get('action', '')

        # 执行动作
        if action in ['audit', 'unaudit', 'login', 'unlogin', 'del'] and numeric(get_param.get('id', 0), 0):
            id = numeric(get_param.get('id', 0), 0)
            if action == 'audit': self.db.edit('user', {'audit': 0}, id)
            if action == 'unaudit': self.db.edit('user', {'audit': 2}, id)
            if action == 'login': self.db.edit('user', {'effective': 1}, id)
            if action == 'unlogin': self.db.edit('user', {'effective': 0}, id)
            if action == 'del': self.db.dele('user', id)
            return alert(act=2)
        if post_param.get('action') in ['audit', 'unaudit', 'login', 'unlogin', 'del'] and post_param.get('id', 0):
            id = post_param.get('id') if isinstance(post_param.get('id'), list) else [post_param.get('id')]
            if post_param.get('action') == 'audit': self.db.edit('user', {'audit': 0}, 'id in (%s)' % ','.join(id))
            if post_param.get('action') == 'unaudit': self.db.edit('user', {'audit': 2}, 'id in (%s)' % ','.join(id))
            if post_param.get('action') == 'login': self.db.edit('user', {'effective': 1}, 'id in (%s)' % ','.join(id))
            if post_param.get('action') == 'unlogin': self.db.edit('user', {'effective': 0},
                                                                   'id in (%s)' % ','.join(id))
            if post_param.get('action') == 'del': self.db.dele('user', 'id in (%s)' % ','.join(id))
            return alert(act=2)
        if post_param.get('action') == 'recharge':
            user_data = self.db.list(table='user', field='money', where=numeric(post_param.get('uid', 0), 0), shift=1)
            if not user_data:return alert(msg='该用户不存在', act=3)
            from decimal import Decimal
            try:
                add_money = float(post_param.get('money'))
            except:
                return alert(msg='输入的金额不合法', act=3)
            money = user_data['money'] + Decimal(add_money)
            rows = self.db.edit('user', {'money': money}, numeric(post_param.get('uid', 0), 0))
            result = 1 if rows else 0
            msg = post_param.get('msg') if post_param.get('msg') else '管理员后台充值'
            insert_data = {
                'oid': 'AR' + date(int(self.kg['run_start_time'][1]), '%Y%m%d%H%M%S') + str_random(3, 0, 1),
                'uid': numeric(post_param.get('uid', 0)),
                'type': 2,
                'amount': Decimal(post_param.get('money', 0)),
                'result': result,
                'info': msg,
                'ip': self.kg['server']['HTTP_ADDR'],
                'addtime': int(self.kg['run_start_time'][1])
            }
            self.db.add('transaction', insert_data)
            return alert(act=2)
        # 获取数据
        filter_id = numeric(get_param.get('filter', 0), 0, 6)
        filter_list = [0, 0, 0]  # 类型、审核、登录
        if filter_id: filter_list[(filter_id - 1) // 2] = (filter_id - 1) % 2
        data = User(self.db, self.kg).list_page(
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),
            sort=numeric(get_param.get('sort', 0), 0, 9),
            level=numeric(get_param.get('level', 0), 0),
            type=filter_list[0],
            audit=filter_list[1],
            effective=filter_list[2],
            word=get_param.get('word', ''),
            date_format='%Y-%m-%d'
        )

        # url参数合成
        button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
        sort_url = url_update(url_query2dict(get_param), deld=['sort', 'page'])
        sort_url = sort_url + '&' if sort_url else ''
        filter_url = url_update(url_query2dict(get_param), deld=['filter', 'page'])
        filter_url = filter_url + '&' if filter_url else ''
        level_url = url_update(url_query2dict(get_param), deld=['cid', 'level'])
        level_url = level_url + '&' if level_url else ''
        url = {
            'button': button_url,
            'sort': sort_url,
            'filter': filter_url,
            'level': level_url
        }

        rank = self.db.list(table='rank', field='id, rankname', where='webid = %s' % self.kg['web']['id'])
        return template(assign={
            'data': data['list'],
            'pagehtml': data['page_html'],
            'rank': rank,
            'level': numeric(get_param.get('level', 0), 0),
            'filter': filter_id,
            'sort': numeric(get_param.get('sort', 0), 0, 9),
            'word': get_param.get('word', ''),
            'url': url,
            'page_data': data['page_data']
        })
