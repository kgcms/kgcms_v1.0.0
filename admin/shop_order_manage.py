# -*- coding:utf-8 -*-
"""网站订单"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, alert, numeric, url_query2dict, url_update, str_replace
        from kyger.common import page_tpl

        get_param = self.kg['get']
        post_param = self.kg['post']

        if get_param.get('action'):
            # get
            action = get_param.get('action', '')
            ids = get_param.get('id', '')
            p_lists = ['del']
            parm = get_param
        else:
            # 判断是否执行动作,以及执行动作的id
            action = post_param.get('action', '')
            ids = post_param.get('id', '')
            p_lists = ['del']
            parm = post_param

        if action in p_lists and ids:
            id_list = parm['id'] if isinstance(parm['id'], list) else [parm['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            if action == 'del':
                self.db.dele('order', where='id in (%s)' % id_sql)  # 删除
            return alert(act=2)

        # 筛选
        filter = numeric(get_param.get('filter', 8), 0, 8)
        if filter == 0:
            status_sql = "&& `status` = 0"  # 等待付款
        elif filter == 1:
            status_sql = "&& `status` = 1"  # 已支付，等待发货'
        elif filter == 2:
            status_sql = "&& `status` = 2"  # 订单已确认，配货中'
        elif filter == 3:
            status_sql = "&& `status` = 3"  # 已发货，等待用户签收'
        elif filter == 4:
            status_sql = "&& `status` = 4"  # 已签收，交易完毕'
        elif filter == 5:
            status_sql = "&& `status` = -1"  # 要求退货
        elif filter == 6:
            status_sql = "&& `status` = -2"  # '拒绝退货，前台交易完毕'
        elif filter == 7:
            status_sql = "&& `status` = -3"  # 退货完毕，订单结束'
        else:
            status_sql = ""  # 退货完毕，订单结束'

        # 排序条件
        sort = numeric(get_param.get('sort', 0), 0, 5)
        sort_param = {
            0: '`addtime` DESC',  # 下单时间降序
            1: '`addtime` ASC',  # 下的那时间升序
            2: '`oid` DESC',  # 订单号降序
            3: '`oid` ASC',  # 订单号升序
            4: '`amount` DESC',  # 订单总金额降序
            5: '`amount` ASC',  # 订单总金额升序
        }
        # 搜索
        word = get_param.get('word', '')
        word_sql = "&& (`oid` like '%%%s%%'||`amount` like '%%%s%%'||`consignee` like '%%%s%%'||`mobile` like '%%%s%%' )" % (
            word, word, word, word) if word else ""
        # 拼接查询条件
        where = 'webid=%s %s %s' % (self.kg['web']['id'], status_sql, word_sql)
        # 分页
        page = numeric(get_param.get('page', 1), 1)  # 当前页
        row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))  # 每页显示
        # 数据库查询
        data_list = self.db.list(
            table='order',
            field="*",
            where=where,
            order=sort_param[sort],
            page=page,
            limit=row
        )
        if page > self.db.total_page:  # 防止大于最大页码
            page = self.db.total_page
            data_list = self.db.list(
                table='order',
                field="*",
                where=where,
                order=sort_param[sort],
                page=page,
                limit=row
            )
        page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
        # 数据处理
        for i in data_list:
            # 时间格式化输出
            i['addtime'] = date(i['addtime'], '%Y-%m-%d %H:%M')
            # 订单状态
            if i['status'] == 0:
                i['status'] = '等待付款'
            elif i['status'] == 1:
                i['status'] = '已支付，等待发货'
            elif i['status'] == 2:
                i['status'] = '订单已确认，配货中'
            elif i['status'] == 3:
                i['status'] = '已发货，等待用户签收'
            elif i['status'] == 4:
                i['status'] = '已签收，交易完毕'
            elif i['status'] == -1:
                i['status'] = '要求退货'
            elif i['status'] == -2:
                i['status'] = '拒绝退货，前台交易完毕'
            else:
                i['status'] = '退货完毕，订单结束'
            # 会员名称处理
            if i['uid'] == 0:
                i['uid'] = '匿名用户'
            else:
                usernaem = self.db.list('user', field='username', where=i['uid'], log=True)
                if usernaem:
                    i['uid'] = usernaem[0]['username']
                else:
                    i['uid'] = '被删除的用户'

        # 数据筛选块,通过路由将上一个筛选条件保持
        sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param),
                                                                                          deld='sort') else ''
        filter_url = url_update(url_query2dict(get_param), deld='filter') + '&' if url_update(
            url_query2dict(get_param), deld='filter') else ''

        search_url = url_update(url_query2dict(get_param), deld='search') + '&' if url_update(
            url_query2dict(get_param), deld='search') else ''
        url = {
            'sort': sort_url,
            'filter': filter_url,
            'search': search_url
        }
        # 数据返回
        return template(
            assign={
                'data': data_list,
                'url': url,
                'sort': sort,
                'filter': filter,
                'page_html': page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL')),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'page_data': page_data
            },
            function=[],
            tpl=self.kg['tpl'],
        )
