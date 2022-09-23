# -*- coding:utf-8 -*-
"""产品首页"""

from kyger.utility import *


class KgcmsApi(object):
    """产品模块首页处理类"""

    def __init__(self):
        """
        初始化数据
        """
        pass

    def __call__(self):
        from kyger.common import permission
        from kyger.kgcms import template
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.picture import Picture
        from kyger.ad import Advertise
        from kyger.misc import Misc
        
        self.kg["get"]["id"] = numeric(self.kg["get"].get("id", 0))
        self.kg["get"]["cid"] = numeric(self.kg["get"].get("cid", 0))
        
        misc = Misc(self.db, self.kg)
        get_param = self.kg['get']

        # 权限检测
        res = permission(self.db, self.kg)
        if res['status'] == 1:
            # 登录状态
            if self.kg['user']['id'] != 0:
                return alert(msg='没有相关权限', act=3)
            else:
                return alert(act="%s/user/login" % self.kg['server']['HTTP_HOST'])
            # return alert(msg='没有访问权限', act=3)
        elif res['status'] == 404:return notfound_404()
        else:data = res['data']

        # 评论开关
        from kyger.parser_ini import Config
        config = Config('config/settings.ini').get('user')
        self.kg['comment_enabled'] = 0
        if data.get('comment') == 1 and 'picture' in json2dict(config['comment_enabled']): self.kg['comment_enabled'] = 1

        # 获取参数
        cid = numeric(get_param.get('cid', 0), 0)  # 频道ID
        id = numeric(get_param.get('id', 0), 0)  # 内容ID

        if id:
            # 浏览次数加一
            click = data['click'] + 1
            self.db.edit(table='picture', data={'click': click}, where='id=%s' % id, log=False)
            # 栏目数
            category_data = self.db.list(table='category', where=data['category'][-1], shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            self.kg['category'] = category_data
            self.kg['picture'] = data
            tpl = 'photo_view.tpl'

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
            tpl = "photo_list.tpl"
        return template(
            function=[
                {"category": Category(self.db, self.kg).list},
                {"article_list": Article(self.db, self.kg).list},
                {"article_single": Article(self.db, self.kg).single},
                {"article_page": Article(self.db, self.kg).list_page},
                {"ad_list": Advertise(self.db, self.kg).list},
                {"picture_list": Picture(self.db, self.kg).list},
                {"picture_single": Picture(self.db, self.kg).single},
                {"picture_page": Picture(self.db, self.kg).list_page},
                {"navigate_list": misc.navigate},
                {"app": misc.app},
                {"get_cart": Product(self.db, self.kg).get_cart},
            ],
            tpl=tpl
        )

