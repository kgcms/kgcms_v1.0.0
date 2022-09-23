# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric
        from kyger.common import page_tpl

        get_param = self.kg['get']
        post_param = self.kg['post']

        if get_param.get('action'):
            # get
            action = get_param.get('action', '')
            ids = get_param.get('id', '')
            p_lists = ['audit', 'unaudit', 'del']
            parm = get_param

        else:
            # 判断是否执行动作,以及执行动作的id
            action = post_param.get('action', '')
            ids = post_param.get('id', '')
            p_lists = ['audit', 'unaudit', 'del']
            parm = post_param

        if action in p_lists and ids:
            id_list = parm['id'] if isinstance(parm['id'], list) else [parm['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            if action == 'audit':
                self.db.edit('guestbook', {'audit': 1}, where='id in (%s)' % id_sql)  # 审核
            if action == 'unaudit':
                self.db.edit('guestbook', {'audit': 0}, where='id in (%s)' % id_sql)  # 未审核
            if action == 'del':
                self.db.dele('guestbook', where='id in (%s)' % id_sql)  # 删除

            return alert(act=2)
        # 提交回复
        reply_id = post_param.get('reply_id')
        reply = post_param.get('reply')
        if reply and reply_id:
            replytime = int(self.kg['run_start_time'][1])
            replyadmin = self.kg['session']['KGCMS_ADMIN_LOGIN_ID']
            re_set = {'reply': reply, 'replytime': replytime, 'replyadmin': replyadmin}
            self.db.edit('guestbook', re_set, where=int(reply_id))

        # 数据库查询
        page = numeric(get_param.get('page', 1), 1)  # 当前页
        where = "webid=%s" % self.kg['web']['id']
        row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))  # 每页显示
        data_list = self.db.list(
            table='guestbook',
            field="*",
            where=where,
            order='id DESC',
            page=page,
            limit=row
        )
        if page > self.db.total_page:  # 防止大于最大页码
            page = self.db.total_page
            data_list = self.db.list(
                table="guestbook",
                field="*",
                where=where,
                order='id DESC',
                page=page,
                limit=row,
            )
        page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
        # 时间过滤
        for i in data_list:
            i['addtime'] = date(i['addtime'], '%Y-%m-%d %H:%M')

        # 返回页面
        return template(
            assign={
                'data': data_list,
                'page_html': page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL')),
                'page_data': page_data
            },
            function=[],
            tpl=self.kg['tpl'],
        )
