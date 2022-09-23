 # -*- coding:utf-8 -*-
"""文章页面"""

from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    def __init__(self):
        self.ajax_show_page = 3  # 允许ajax异步加载的最大页数
        self.ajax_show_rows = 10  # ajax异步的每页条数

    def __call__(self):
        from kyger.common import permission
        from kyger.comment import Comment
        from kyger.kgcms import template
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc
        
        self.kg["get"]["id"] = numeric(self.kg["get"].get("id", 0))
        self.kg["get"]["cid"] = numeric(self.kg["get"].get("cid", 0))
        
        get_param = self.kg['get']
        comment = Comment(self.db, self.kg)
        misc = Misc(self.db, self.kg)

        # 权限检测
        res = permission(self.db, self.kg)
        if res['status'] == 1:
            if self.kg['user']['id'] != 0:
                return alert(msg='没有相关权限', act=3)
            else:
                return alert(act="%s/user/login" % self.kg['server']['HTTP_HOST'])
            # return alert(msg='没有访问权限', act=3)
        elif res['status'] == 404: return notfound_404()
        else: data = res['data']

        # 评论开关
        from kyger.parser_ini import Config
        config = Config('config/settings.ini').get('user')
        self.kg['comment_enabled'] = 0
        if data.get('comment') == 1 and 'article' in json2dict(config['comment_enabled']):self.kg['comment_enabled'] = 1

        # 获取参数
        cid = numeric(get_param.get('cid', 0), 0)  # 频道ID
        id = numeric(get_param.get('id', 0), 0)  # 内容ID

        if id:
            # 浏览次数加一
            click = data['click'] + 1
            self.db.edit(table='article', data={'click': click}, where='id=%s' % id, log=False)
            # 栏目数
            category_data = self.db.list(table='category', where=data['category'][-1], shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            self.kg['category'] = category_data
            self.kg['article'] = data
            tpl = 'article_view.tpl'
        else:
            # 获取上级频道id和名称
            if data['upper']:
                up_cate = self.db.list(
                    table='category',
                    field='id,title',
                    where=data['upper'][-1],
                    shift=1
                )
                up_data = (up_cate['title'], up_cate['id']) if up_cate else ('', 0)
                data['up_name'], data['up_id'] = up_data
            else:
                data['up_name'], data['up_id'] = ('', 0)
            self.kg['category'] = data

            tpl = data['template'] if data['template'] else 'article_list.tpl'
        return template(
            function=[
                {"category": Category(self.db, self.kg).list},
                {"article_list": Article(self.db, self.kg).list},
                {"article_single": Article(self.db, self.kg).single},
                {"article_page": Article(self.db, self.kg).list_page},
                {"navigate_list": misc.navigate},
                {"ad_list": Advertise(self.db, self.kg).list},
                {"app": misc.app},
                {"comment": comment.list},
                {"get_cart": Product(self.db, self.kg).get_cart},
            ],
            tpl=tpl
        )



