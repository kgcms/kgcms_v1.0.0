# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric, url_query2dict, url_update, str_replace, str_cutting
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
                self.db.edit('comment', {'audit': 1}, where='id in (%s)' % id_sql)  # 审核
            if action == 'unaudit':
                self.db.edit('comment', {'audit': 0}, where='id in (%s)' % id_sql)  # 未审核
            if action == 'del':
                self.db.dele('comment', where='id in (%s)' % id_sql)  # 删除
            return alert(act=2)
        # 一键审核
        if int(get_param.get('good', 0)) == 1:
            self.db.edit('comment', {'audit': 1}, where=0)
            return alert(act=2)
        # 数据库查询
        page = numeric(get_param.get('page', 1), 1)  # 当前页
        # 筛选
        filter = numeric(get_param.get('filter', 0), 0, 2)
        if filter == 1:
            audit_sql = "&& a.`audit` = 1"  # 通过审核
        elif filter == 2:
            audit_sql = "&& a.`audit` = 0"  # 未通过审核
        else:
            audit_sql = ""
        # 评论类型
        type = numeric(get_param.get('type', 0), 0, 3)
        if type == 0:
            table = " `%scomment` a, `%sarticle` b " % (self.db.cfg["prefix"], self.db.cfg["prefix"])
            type = "&& a.`type`=1"
        elif type == 1:
            table = " `%scomment` a, `%sproduct` b " % (self.db.cfg["prefix"], self.db.cfg["prefix"])
            type = "&& a.`type`=2"
        elif type == 2:
            table = " `%scomment` a, `%spicture` b " % (self.db.cfg["prefix"], self.db.cfg["prefix"])
            type = "&& a.`type`=3"
        else:
            table = " `%scomment` a, `%sdownload` b " % (self.db.cfg["prefix"], self.db.cfg["prefix"])
            type = "&& a.`type`=4"
        # 搜索查询
        search = int(get_param.get('search', 0))
        word = get_param.get('word', '')
        word_sql = "&& (a.`ip` like '%%%s%%'||b.`title` like '%%%s%%'||a.`content` like '%%%s%%' )" % (
        word, word, word) if word else ""
        webid = "&& a.`webid` = %s" % self.kg['web']['id']
        # 查询条件
        where = " %s %s %s %s%s" % ("a.`aid`=b.`id`", audit_sql, type, word_sql, webid)
        # 排序条件
        sort = int(get_param.get('sort', 0))
        sort_param = {
            0: '`addtime` DESC',  # 提交时间降序
            1: '`addtime` ASC',  # 提交时间升序
            2: '`agree` DESC',  # 顶帖数降序
            3: '`agree` ASC',  # 顶帖数升序
        }
        row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))  # 每页显示
        data_list = self.db.list(
            table=table,
            field="a.*, b.`title` as title, b.`commenttotal`as commenttotal ",
            where=where,
            order=sort_param[sort],
            page=page,
            limit=row
        )

        if page > self.db.total_page:  # 防止大于最大页码
            page = self.db.total_page
            data_list = self.db.list(
                table=table,
                field="a.*, b.`title` as title, b.`commenttotal`as commenttotal ",
                where=where,
                order=sort_param[sort],
                page=page,
                limit=row
            )
        page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
        # 时间过滤
        for i in data_list:
            i['addtime'] = date(i['addtime'], '%Y-%m-%d %H:%M')
            i['cut_content'] = str_cutting(i['content'], 60)

        # url参数合成

        sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param),
                                                                                          deld='sort') else ''
        filter_url = url_update(url_query2dict(get_param), deld='filter') + '&' if url_update(
            url_query2dict(get_param), deld='filter') else ''

        type_url = url_update(url_query2dict(get_param), deld='type') + '&' if url_update(
            url_query2dict(get_param), deld='type') else ''
        search_url = url_update(url_query2dict(get_param), deld='search') + '&' if url_update(
            url_query2dict(get_param), deld='search') else ''

        url = {
            'sort': sort_url,
            'filter': filter_url,
            'type': type_url,
            'search': search_url

        }
        # 返回页面
        return template(
            assign={
                'data': data_list,
                'page_html': page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL')),
                'sort': sort,
                'filter': filter,
                'type': numeric(get_param.get('type', 0), 0, 3),
                'search': search,
                'url': url,
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'page_data': page_data
            },
            function=[],
            tpl=self.kg['tpl'],
        )
