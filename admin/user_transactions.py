# -*- coding:utf-8 -*-
"""网站订单"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric, url_update, url_query2dict
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = post_param.get('action')

        # 删除操作
        if action == 'del' and post_param.get('id'):
            del_id = post_param.get('id')
            if isinstance(del_id, str): del_id = [del_id]
            self.db.dele('transaction', 'id in (%s)' % ','.join('%s' % v for v in del_id))
            return alert(act=2)

        # 获取数据
        word = get_param.get('word', '')  # 搜索关键字
        type_id = numeric(get_param.get('type', 0), 0, 6)  # 交易类型
        data = self.list(
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),
            page=numeric(get_param.get('page', 1), 1),
            type_id=type_id,
            word=word
        )

        return template(assign={'data': data['list'], 'pagehtml': data['page_html'], 'word': word, 'type': type_id, 'page_data': data['page_data']})

    def list(self, row=10, page=1, type_id=0, word=''):
        # 交易类型
        type_dir = {
            1: '会员在线充值',
            2: '后台手动充值[银行转账]',
            3: '购买商品[消费支付]',
            4: '提交、删除或修改订单',
            5: '购买浏览权限',
            6: '操作日志'
        }
        # 关键字搜索
        if word:
            like_id = self.db.list(table='user', field='id', where='username like "%%%s%%"' % word)
            id_list = ['0']
            for var in like_id:
                id_list.append(str(var['id']))
            word_sql = ' && (oid like "%%%s%%" or uid in (%s))' % (word, ','.join(id_list))
        else:
            word_sql = ''
        # 交易类型
        type_sql = ' && type = %s' % type_id if type_id else ''

        # 获取订单数据
        data = self.db.list(
            table='transaction',
            field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
            where='1%s%s' % (type_sql, word_sql),
            page=page,
            limit=row,
            order='id DESC'
        )
        if page > self.db.total_page:
            page = self.db.total_page
            data = self.db.list(
                table='transaction',
                field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                where='1%s%s' % (type_sql, word_sql),
                page=page,
                limit=row,
                order='id DESC'
            )
        page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
        # 获取用户名
        userid = []
        for var in data:
            if var['id'] not in userid: userid.append(str(var['uid']))
        if userid:
            username_list = self.db.list(
                table='user',
                field='username, id',
                where="id in (%s)" % ','.join(userid)
            )
            res = {}
            for var in username_list:
                res[var['id']] = var['username']
            for var in data:
                var['type_title'] = type_dir[var['type']]
                var['username'] = res.get(var['uid'], '')
        # 分页
        web_url = self.kg['server'].get('WEB_URL')
        from kyger.common import page_tpl
        page_html = page_tpl(self.db.page, self.db.total_page, row, web_url)  # 获取分页模板

        return {'list': data, 'page_html': page_html, 'page_data': page_data}


