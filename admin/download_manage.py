# -*- coding:utf-8 -*-
"""下资源载管理页面"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.download import Download
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, url_query2dict, url_update, str_replace
        download = Download(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']

        if get_param.get('action'):
            # get
            action = get_param.get('action', '')
            ids = get_param.get('id', '')
            p_lists = ['recom', 'unrecom', 'audit', 'unaudit', 'del', 'del_true', 'recovery']
            parm = get_param

        else:
            # 判断是否执行动作,以及执行动作的id
            action = post_param.get('action', '')
            ids = post_param.get('id', '')
            p_lists = ['recom', 'unrecom', 'audit', 'unaudit', 'del', 'del_true', 'recovery']
            parm = post_param

        if action in p_lists and ids:
            id_list = parm['id'] if isinstance(parm['id'], list) else [parm['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            if action == 'recom':
                self.db.edit('download', {'recom': 1}, where='id in (%s)' % id_sql)  # 推荐
            if action == 'unrecom':
                self.db.edit('download', {'recom': 0}, where='id in (%s)' % id_sql)  # 不推荐
            if action == 'audit':
                self.db.edit('download', {'audit': 1}, where='id in (%s)' % id_sql)  # 审核
            if action == 'unaudit':
                self.db.edit('download', {'audit': 0}, where='id in (%s)' % id_sql)  # 未审核
            if action == 'del':
                self.db.edit('download', {'recycle': 1}, where='id in (%s)' % id_sql)  # 删除
            if action == 'recovery':
                self.db.edit('download', {'recycle': 0}, where='id in (%s)' % id_sql)  # 还原
            if action == 'del_true':
                self.db.dele('download', where='id in (%s)' % id_sql)  # 彻底删除

            return alert(act='download_manage')

        # 判断是否执行刷新
        refresh = get_param.get('refresh', 0)
        if numeric(refresh) == 1:
            return alert(act='download_manage')

        # 不符合上面条件则调用数据
        filter_id = numeric(get_param.get('filter', 0), 0, 6)  # 数据筛选的序号
        recycle = numeric(get_param.get('trash', 0), 0, 1)  # 回收站
        # 数据筛选参数
        filter_list = [0, 0, 0]  # 推荐  审核 评论
        if filter_id:
            filter_id = filter_id - 1 if filter_id > 0 else 0
            filter_list[filter_id // 2] = (filter_id % 2)+1
        # 调用下载数据
        data = download.list_page(
            sort=numeric(get_param.get('sort', 0)),                     # 排序
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),  # 调用条数
            recom=filter_list[0],                                       # 推荐
            category=numeric(get_param.get('cid', 0)),                  # 栏目
            start=0,                                                    # 分页不设置开始
            picture=0,                                                  # 是否调用图片记录
            word=get_param.get('word', ''),                             # 搜索关键字
            audit=filter_list[1],                                       # 审核
            recycle=recycle+1,                                          # 回收
            comment=filter_list[2],                                     # 评论
            date='%Y-%m-%d'                                             # 日期格式
        )

        # 栏目数据
        from kyger.category import Category
        column = Category(self.db, self.kg)
        category_data = column.rank(cid="download")  # 获取栏目结构
        category_data.insert(0, {"title": "所有栏目", "id": 0, "level": 0})

        # url参数合成
        button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
        sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param), deld='sort') else ''
        filter_url = url_update(url_query2dict(get_param), deld='filter') + '&' if url_update(url_query2dict(get_param), deld='filter') else ''
        category_url = url_update(url_query2dict(get_param), deld='cid') + '&' if url_update(url_query2dict(get_param), deld='cid') else ''
        url = {
            'button': button_url,
            'sort': sort_url,
            'filter': filter_url,
            'category': category_url
        }
        # print(data['pushtime'])
        return template(
            assign={
                'data': data['list'],
                'branch': data['page_html'],
                'sort': numeric(get_param.get('sort', 0)),
                'filter': numeric(get_param.get('filter', 0), 0, 6),
                'category': category_data,
                'cid': numeric(get_param.get('cid', 0)),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'url': url,
                'trash': recycle,
                'page_data': data['page_data']
            }
        )
