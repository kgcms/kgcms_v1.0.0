
# -*- coding:utf-8 -*-
"""微信素材"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.utility import date, alert, numeric, url_query2dict, url_update, str_replace, json2dict,dict2json_file
        from kyger.kgcms import template
        from kyger.common import page_tpl, check_del_material
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
            p_lists = ['del_all']
            parm = post_param

        if action in p_lists and ids:
            id_list = parm['id'] if isinstance(parm['id'], list) else [parm['id']]  # 将单条转列表

            # 验证删除的素材id是否被引用
            id_list, udel_list = check_del_material(self.db, id_list)
            if id_list:
                if '1' in id_list: return alert(msg="系统数据无法删除", act=3)
                id_sql = ','.join(id_list)
                if action == 'del':
                    self.db.dele('material', where='id in (%s)' % id_sql)  # 删除
                if action == 'del_all':
                    self.db.dele('material', where='id in (%s)' % id_sql)  # 全选删除
                return alert(act='material_manage', msg="删除成功! 除部分被引用的素材无法删除!")
            else:
                return alert(act='material_manage', msg='已经被引用的素材无法删除!')

        # 类型筛选
        filter = numeric(get_param.get('type', 3), 0, 3)
        if filter == 0:
            status_sql = "`type` = 0"  # 单图
        elif filter == 1:
            status_sql = "`type` = 1"  # 多图
        elif filter == 2:
            status_sql = "`type` = 2"  # 文本
        else:
            status_sql = ""  # 不筛选

        # 搜索
        word = get_param.get('word', '')
        word_sql = "`name` like '%%%s%%'||`title` like '%%%s%%'" % (word, word) if word != '' else ""
        # 拼接查询条件
        if status_sql != ''and word_sql != '':
            where = ' %s && %s' % (status_sql, word_sql)
        elif status_sql != ''and word_sql == '':
            where = '%s' % status_sql
        elif status_sql == ''and word_sql != '':
            where = '%s' % word_sql
        else:
            where = ''
        # 排序
        sort = numeric(get_param.get('sort', 0), 0, 3)
        sort_param = {
            0: '`addtime` ASC',  # 添加时间降序
            1: '`addtime` DESC',  # 添加时间升序
        }
        # 分页
        page = numeric(get_param.get('page', 1), 1)  # 当前页
        row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))  # 每页显示
        # 数据库查询
        data_list = self.db.list(
            table='material',
            field="*",
            where=where,
            order=sort_param[sort],
            page=page,
            limit=row
        )
        if page > self.db.total_page:  # 防止大于最大页码
            page = self.db.total_page
            data_list = self.db.list(
                table='material',
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
            i['picture'] = json2dict(i['picture'])
            i['title'] = json2dict(i['title'])
            i['key2url'] = json2dict(i['key2url'])
            # i['update_time'] = date(i['update_time'], '%Y-%m-%d %H:%M')

        sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param),
                                                                                          deld='sort') else ''
        type_url = url_update(url_query2dict(get_param), deld='type') + '&' if url_update(
            url_query2dict(get_param), deld='type') else ''

        url = {
            'sort': sort_url,
            'type': type_url,
        }
        return template(
            assign={
                'data': data_list,
                'sort': sort,
                'type': numeric(get_param.get('type', 4), 0, 4),
                'url': url,
                'page_html': page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL')),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'page_data': page_data
            },
            function=[],
            tpl=self.kg['tpl'],
        )
