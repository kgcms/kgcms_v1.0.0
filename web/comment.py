# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.utility import *
from kyger.kgcms import template
from kyger.common import *


class KgcmsApi(object):
    """KGCMS框架接口"""
    db = kg = None

    def __init__(self):
        self.ajax_show_page = 3  # 允许ajax异步加载的最大页数
        self.ajax_show_rows = 10  # ajax异步的每页条数

    def __call__(self):
        from kyger.kgcms import template
        from kyger.comment import Comment
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc
        misc = Misc(self.db, self.kg)
        comment = Comment(self.db, self.kg)

        if self.kg['post'].get('action', '') == 'comment':
            theme = numeric(self.kg['post'].get('theme', 0), 0)
            quote = numeric(self.kg['post'].get('quote', 0), 0)
            content = self.kg['post'].get('comment', '')
            type = numeric(self.kg['get'].get('type', 1), 1, 4)
            aid = numeric(self.kg['get'].get('id', 0))
            # 评论限制
            tables = {1: "article", 2: "product", 3: "picture", 4: "download"}
            module_data = self.db.list(table=tables[type], where=aid, shift=1)
            comment_open = module_data.get('comment', 0)
            from kyger.parser_ini import Config
            config = Config('config/settings.ini').get('user')
            if comment_open != 1 or tables[type] not in json2dict(config['comment_enabled']):
                return json2dict({'status': 0, 'msg': '该内容已被禁止评论'}, trans=False)
            # 评论结果
            if not content: return json2dict({'status': 0, 'msg': '请输入评论内容'}, trans=False)
            res = comment.insert(type, aid, content, quote, theme)
            if res.get('status') == 1:
                if res['audit'] == 1:return json2dict({"status": 1, 'msg': '', 'comment': res['comment']}, trans=False)
                else:return json2dict({"status": 1, 'msg': '评论成功,等待管理员审核'}, trans=False)
            else:
                return json2dict(res, trans=False)

        elif self.kg['get'].get('action', '') == 'agree':
            id = numeric(self.kg['get'].get('id', 0))
            if not id: return json2dict({'status': 0, 'msg': '不存在的评论'}, trans=False)
            res = comment.agree(id)
            return json2dict(res, trans=False)

        # 获取二三级
        elif self.kg['post'].get('action', '') == 'getcomment':
            theme = numeric(self.kg['post'].get('theme'), 0)
            page = numeric(self.kg['post'].get('page'), 1)
            row = self.ajax_show_rows
            if not all([theme, page, row]): return json2dict({'status': 1, "msg": '参数错误'}, trans=False)
            res = comment.get_quote(theme, page, rows=row)
            res['status'] = 0
            return json2dict(res, trans=False)

        # 获取一级
        elif self.kg['post'].get('action', '') == 'gettheme':
            page = numeric(self.kg['post'].get('page'), 1, self.ajax_show_page)
            self.kg['get']['page'] = page
            row = self.ajax_show_rows
            aid = numeric(self.kg['post'].get('aid'), 0)
            if not all([page, row, aid]): return json2dict({'status': 1, "msg": '参数错误'}, trans=False)
            res = comment.page_list(1, aid, sort=0, rows=row)
            re_data = {'comment': res['list'], 'page_data': res['page_data'], 'status': 0}
            return json2dict(re_data, trans=False)

        else:
            # 评论数据
            type = numeric(self.kg['get'].get('type', 1))
            aid = numeric(self.kg['get'].get('id', 0))
            if not aid: return alert(msg='不存在的评论内容', act=3)
            sort = numeric(self.kg['get'].get('sort', 0))
            data = comment.page_list(type, aid, sort)
            self.kg['comment'] = data
            self.kg['order'] = sort

            # 总记录数
            count_user = self.db.list(table='comment', field='COUNT(DISTINCT user) as count', where='audit=1 && aid=%s' % aid, shift=1)['count']
            count_rows = self.db.list(table='comment', field='COUNT(*) as count', where='audit=1 && aid=%s' % aid, shift=1)['count']
            self.kg['count'] = {'user': count_user, 'rows': count_rows}

            # 最新10条与热门10条文章
            new = self.db.list(table='comment', where='audit=1', order='addtime DESC', limit='0,10')
            for row in new:
                row['addtime'] = date(row['addtime'], '%Y-%m-%d %H:%M:%S')
                row['url'] = 'comment?type=%s&id=%s' % (row['type'], row['aid'])
            fire = Article(self.db, self.kg).list(6)
            self.kg['top'] = {'new': new, 'fire': fire}

            # id对应的标题
            tables = ['article', 'product', 'picture', 'download']
            url = ['article', 'product', 'photo', 'download']
            res = self.db.list(table=tables[type-1], where=aid, shift=1)
            self.kg['module'] = {'title': res.get('title', ''), 'url': '%s?id=%s' % (url[type-1], aid)}

            # url
            self.kg['sort'] = url_update(url_query2dict(self.kg['get']), deld='sort') + '&' if url_update(url_query2dict(self.kg['get']), deld='sort') else ''
            return template(
                assign={"path": str_replace(self.kg['server']['WEB_URL'], [self.kg['server']['HTTP_HOST'] + '/'], '')},
                function=[
                    {"category": Category(self.db, self.kg).list},
                    {"article_list": Article(self.db, self.kg).list},
                    {"article_single": Article(self.db, self.kg).single},
                    {"article_page": Article(self.db, self.kg).list_page},
                    {"ad_list": Advertise(self.db, self.kg).list},
                    {"navigate_list": misc.navigate},
                    {"app": misc.app},
                    {"get_cart": Product(self.db, self.kg).get_cart},
                ],
            )





























