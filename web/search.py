# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.utility import *
from kyger.common import *
from kyger.parser_ini import Config


class KgcmsApi(object):
    """KGCMS框架接口"""
    db = ''
    kg = ''

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.search import Search
        from kyger.ad import Advertise
        # 搜索限制
        config = Config('config/settings.ini').get('user')
        userid = self.kg['user'].get('id', 0)
        if config['search_open'] == 1 and not userid: return alert(msg="仅允许会员使用搜索功能", act=3)
        if config['search_open'] == 2: return alert(msg="搜索功能已禁用", act=3)
        # 搜索范围限制
        all_content = 1
        if config['search_fulltext'] == 1 and not userid: all_content = 0
        if config['search_fulltext'] == 2: all_content = 0

        search = Search(self.db, self.kg)
        get_param = self.kg['get']

        # 搜索类型
        type_id = numeric(get_param.get('type', 1), 1, 4)

        # 搜索关键字
        word = get_param.get('word', '')
        if word:
            data = search.data(word=word, type=type_id, all_content=all_content)
            if data.get('status', 1) == 0: return alert(msg=data.get('msg', ''), act=3)
            return template(
                assign={"word": get_param.get('word'), 'type': type_id, 'data': data},
                function=[
                    {"ad_list": Advertise(self.db, self.kg).list},
                ],
                tpl='search_list.tpl'
            )
        else:
            return template(assign={'type': type_id},)






























