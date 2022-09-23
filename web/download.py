# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.utility import *
from kyger.kgcms import template
from kyger.common import *


class KgcmsApi(object):
    """KGCMS框架接口"""
    db = ''
    kg = ''

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.common import permission
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.download import Download
        from kyger.misc import Misc
        
        self.kg["get"]["id"] = numeric(self.kg["get"].get("id", 0))
        self.kg["get"]["cid"] = numeric(self.kg["get"].get("cid", 0))
        
        misc = Misc(self.db, self.kg)
        get_param = self.kg['get']

        # 页面访问权限检测
        res = permission(self.db, self.kg)
        if res['status'] == 1:
            # 登录状态
            if self.kg['user']['id'] != 0:
                return alert(msg='没有相关权限', act=3)
            else:
                return alert(act="%s/user/login" % self.kg['server']['HTTP_HOST'])
        elif res['status'] == 404:return notfound_404()
        else: data = res['data']

        # 评论开关
        from kyger.parser_ini import Config
        config = Config('config/settings.ini').get('user')
        self.kg['comment_enabled'] = 0
        if data.get('comment') == 1 and 'download' in json2dict(config['comment_enabled']): self.kg['comment_enabled'] = 1

        # 获取参数
        cid = numeric(get_param.get('cid', 0), 0)  # 频道ID
        id = numeric(get_param.get('id', 0), 0)  # 内容ID

        # 动作逻辑
        # 文件下载
        if get_param.get('action', '') == 'download':
            # 获取下载的记录
            download_id = numeric(get_param.get('download', 0), 0)
            down_data = Download(self.db, self.kg).single(download_id, '%Y-%m-%d')
            if not down_data: return notfound_404()

            # 下载权限判断
            if res['rank'] not in down_data['permission'] and 0 not in down_data['permission']:
                return alert(msg='没有下载权限', act=3)

            # 下载次数加一
            count = down_data['count'] + 1
            # 更新下载次数, 下载页面pageurl过长无法写日志, 暂时关闭日志
            self.db.edit(table='download', data={'count': count}, where='id=%s' % download_id, log=False)

            # 下载逻辑判断
            mirror = get_param.get('mirror', '')
            local_url = '/api/unlimited_process?action=download&id=%s&name=%s&code=%s'
            mirror_url = '/api/unlimited_process?action=download&id=%s&mirror=1&url=%s'

            # 使用默认下载
            if mirror == '':
                if down_data.get('defaultdown', 0) == 0:  # 默认使用本地下载
                    path = down_data.get('local', '')
                    return alert(act=local_url % (download_id, down_data['downname'], cipher(path, 1, 300)))
                else:  # 默认使用镜像下载
                    mirror_index = down_data.get('defaultdown', 0)
                    if len(down_data['mirror']) < mirror_index: return notfound_404()
                    return alert(act=mirror_url % (download_id, down_data['mirror'][mirror_index - 1].get('url')))

            # 使用本地下载
            elif numeric(mirror, 0) == 0:
                path = down_data.get('local', '')
                return alert(act=local_url % (download_id, down_data['downname'], cipher(path, 1, 300)))

            # 使用镜像下载
            else:
                mirror_index = numeric(mirror, 0)
                if len(down_data['mirror']) < mirror_index: return notfound_404()
                return alert(act=mirror_url % (download_id, down_data['mirror'][mirror_index - 1].get('url')))

        # 页面逻辑
        if id:
            # 没有详情页n
            if data['content'] == '':
                return alert(act="%s/download?action=download&download=%s" % (self.kg['server']['HTTP_HOST'], id))
            # 浏览次数加一
            click = data['click'] + 1
            self.db.edit(table='download', data={'click': click}, where='id=%s' % id, log=False)

            # 获取栏目设置全局变量
            category_data = self.db.list(table='category', where=data['category'][-1], shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            self.kg['category'] = category_data
            self.kg['download'] = data
            tpl = 'download_view.tpl'
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
            tpl = "download_list.tpl"
        return template(
            function=[
                {"category": Category(self.db, self.kg).list},
                {"article_list": Article(self.db, self.kg).list},
                {"article_single": Article(self.db, self.kg).single},
                {"article_page": Article(self.db, self.kg).list_page},
                {"ad_list": Advertise(self.db, self.kg).list},
                {"download_list": Download(self.db, self.kg).list},
                {"download_single": Download(self.db, self.kg).single},
                {"download_page": Download(self.db, self.kg).list_page},
                {"navigate_list": misc.navigate},
                {"app": misc.app},
                {"get_cart": Product(self.db, self.kg).get_cart},
            ],
            tpl=tpl
        )





























