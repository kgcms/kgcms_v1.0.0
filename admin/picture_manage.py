# -*- coding:utf-8 -*-
"""网站图片"""
from kyger.kgcms import template
from kyger.utility import date, json2dict, numeric, alert,str_replace,url_update,url_query2dict
from kyger.picture import Picture
from kyger.category import Category


class KgcmsApi(object):
    """KGCMS框架接口"""
    kg = db = None
    reder = None

    def __init__(self):
        pass

    def __call__(self):
        picture = Picture(self.db, self.kg)
        get_param = self.kg['get']
        action = get_param.get('action', '')

        # 动作判断
        action_list = ['audit', 'unaudit', 'del', 'recom', 'unrecom', 'del_true', 'recovery']
        if action in action_list and numeric(get_param.get('id', 0), 0):
            act_id = numeric(get_param.get('id', 0), 0)
            if action == "audit": self.db.edit('picture', {'audit': 1}, act_id)
            if action == "unaudit": self.db.edit('picture', {'audit': 0}, act_id)
            if action == "recom": self.db.edit('picture', {'recom': 1}, act_id)
            if action == "unrecom": self.db.edit('picture', {'recom': 0}, act_id)
            if action == "del": self.db.edit('picture', {'recycle': 1}, act_id)
            if action == "del_true": self.db.dele('picture', act_id)
            if action == "recovery": self.db.edit('picture', {'recycle': 0}, act_id)
            return alert(act=2)

        # 设置变量，获取参数
        recycle = numeric(get_param.get('trash', 0), 0, 1)

        # 添加了一条栏目
        category = Category(self.db, self.kg).rank('photo')
        category.insert(0, {'id': 0, 'title': '请选择栏目', 'level': 1})

        # 传递给函数的参数
        filter_list = [0, 0, 0]  # 推荐、审核、允许
        filter_id = numeric(get_param.get('filter'))  # 获取参数
        if filter_id:
            filter_id = filter_id - 1 if filter_id > 0 else 0  # 判断大于0 减1
            filter_list[filter_id // 2] = (filter_id % 2) + 1  # 取余2加一再取整2

        # 参数合成（混合筛选）
        cid_url = url_update(url_query2dict(get_param), deld='cid') + '&' if url_update(url_query2dict(get_param), deld='cid') else ''
        sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param), deld='sort') else ''
        filter_url = url_update(url_query2dict(get_param), deld='filter') + '&' if url_update(url_query2dict(get_param), deld='filter') else ''
        url = {'cid': cid_url,
               'sort': sort_url,
               'filter': filter_url
               }

        # 传递的参数
        data = picture.list_page(
            sort=numeric(get_param.get('sort', 0), 0, 8),
            row=numeric(self.kg['cookie'].get('KGCMS_PICTURE_ROWS', 9)),
            recom=filter_list[0],
            category=numeric(get_param.get('cid', 0), 0, 0),
            audit=filter_list[1],
            word=get_param.get('word', ''),
            comment=filter_list[2],
            recycle=recycle+1,
            dateformat='%Y-%m-%d'
        )

        return template(
            assign={
                'sort': numeric(get_param.get('sort', 0)),
                'filter': numeric(get_param.get('filter', 0), 0, 8),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'cid': numeric(get_param.get('cid', 0), 0),
                'data': data['list'],
                'branch': data['page_html'],
                'category': category,
                'trash': numeric(get_param.get('trash', 0), 0, 1),
                'url': url,
                'page_data': data['page_data']
            }
        )
