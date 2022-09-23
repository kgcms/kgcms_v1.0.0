# -*- coding:utf-8 -*-
"""文章管理页面"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.article import Article
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, url_query2dict, url_update, str_replace
        article = Article(self.db, self.kg)
        get_param = self.kg['get']

        # 判断是否执行动作
        action = get_param.get('action', '')
        if action in ['recom', 'unrecom', 'published', 'unpublished', 'audit', 'unaudit', 'del', 'del_true', 'recovery'] and get_param.get('id', ''):
            id_list = get_param['id'] if isinstance(get_param['id'], list) else [get_param['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            if action == 'recom': self.db.edit('article', {'recom': 1}, where='id in (%s)' % id_sql)  # 推荐
            if action == 'unrecom': self.db.edit('article', {'recom': 0}, where='id in (%s)' % id_sql)  # 不推荐
            if action == 'published': self.db.edit('article', {'published': 1}, where='id in (%s)' % id_sql)  # 出版
            if action == 'unpublished': self.db.edit('article', {'published': 0}, where='id in (%s)' % id_sql)  # 草稿
            if action == 'audit': self.db.edit('article', {'audit': 1}, where='id in (%s)' % id_sql)  # 审核
            if action == 'unaudit': self.db.edit('article', {'audit': 0}, where='id in (%s)' % id_sql)  # 未审核
            if action == 'del': self.db.edit('article', {'recycle': 1}, where='id in (%s)' % id_sql)  # 删除
            if action == 'recovery': self.db.edit('article', {'recycle': 0}, where='id in (%s)' % id_sql)  # 还原
            if action == 'del_true': self.db.dele('article', where='id in (%s)' % id_sql)  # 彻底删除
            # 移除action和id参数
            return alert(act=2)

        # 判断是否执行刷新
        refresh = get_param.get('refresh', 0)
        if numeric(refresh) == 1:
            return alert(act='article_manage')

        # 不符合上面条件则调用数据
        filter_id = numeric(get_param.get('filter', 0), 0, 8)  # 数据筛选的序号
        recycle = numeric(get_param.get('trash', 0), 0, 1)  # 回收站
        # 数据筛选参数
        filter_list = [0, 0, 0, 0]  # 推荐 出版 审核 评论
        if filter_id:
            filter_id = filter_id - 1 if filter_id > 0 else 0
            filter_list[filter_id // 2] = (filter_id % 2)+1
        # 调用文章数据
        data = article.list_page(
            sort=numeric(get_param.get('sort', 0)),                     # 排序
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),  # 调用条数
            recom=filter_list[0],                                       # 推荐
            category=numeric(get_param.get('cid', 0)),                  # 栏目
            start=0,                                                    # 分页不设置开始
            picture=0,                                                  # 是否调用图片记录
            word=get_param.get('word', ''),                               # 搜索关键字
            published=filter_list[1],                                   # 出版
            audit=filter_list[2],                                       # 审核
            recycle=recycle+1,                                            # 回收
            comment=filter_list[3],                                     # 评论
            date='%Y-%m-%d'                                             # 日期格式
        )
        # 栏目数据
        from kyger.category import Category
        column = Category(self.db, self.kg)
        category_data = column.rank(cid="article")  # 获取栏目结构
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
        return template(
            assign={
                'data': data['list'],
                'branch': data['page_html'],
                'sort': numeric(get_param.get('sort', 0)),
                'filter': numeric(get_param.get('filter', 0), 0, 8),
                'category': category_data,
                'cid': numeric(get_param.get('cid', 0)),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'url': url,
                'trash': recycle,
                'page_data': data['page_data']
            }
        )
