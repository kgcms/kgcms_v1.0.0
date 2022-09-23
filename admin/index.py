# -*- coding:utf-8 -*-
"""网站首页"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __call__(self):
        from kyger.utility import json2dict, str_replace, dict2json_file, alert, date
        from kyger.kgcms import App
        from kyger.parser_ini import Config  # 配置文件读取函数
        from kyger.common import get_python_version
        from kyger.log import Log
        from kyger.adminpage import Adminpage
        log = Log(self.db, self.kg)
        adminpage = Adminpage(self.db, self.kg)
        admin_page = []
        for var in adminpage.list(1):
            for row in var['submenu']:
                if row['plus']: admin_page.append(row['page'])
        post_param = self.kg['post']

        if post_param.get('action', '') == "submit":
            menu = post_param.get('name', '')
            url = post_param.get('page', '')
            res = []
            for i in range(len(menu)):
                res.append({"name": menu[i], "page": url[i]})
            dict2json_file(res, file='config/admin_custom_menu.json')
            return alert(act=2)

        kgcms_info = json2dict(file='temp/kgcms_info.json')  # 公告/最新版本信息
        if not isinstance(kgcms_info, dict):
            kgcms_info = {
                "latest_version": ["v1.0.0", "2019-09-01"],
                "official_notice": [{
                    "title": '<font color="#FF0000">KGCMS API Error.</font>',
                    "url": "http://www.kgcms.com",
                    "date": date()
                }]
            }
        
        # noinspection PyDictCreation
        index = {
            'kgcms_version': App.version,
            'kgcms_new_version': kgcms_info["latest_version"],
            'python_version': get_python_version(),
            'kgcms_notice': kgcms_info["official_notice"],
            'mysql_version': self.db.version(),
            'db_table_count': len(self.db.table_list(False)),
            'log': {
                'all': log.list(),
                'login': log.list(6),
                'mysql': log.list([1, 2, 3, 4, 5]),
                'upload': log.list(7),
            },
            'ip_find': Config('config/settings.ini').get('api')['ip_find'],
            'recent': adminpage.recent(0),
            'index_page': json2dict(file='config/admin_custom_menu.json'),
            'admin_page': admin_page
        }

        # 整形
        self.kg["server"]["SERVER_SOFTWARE"] = str_replace(self.kg["server"]["SERVER_SOFTWARE"], "/", "-")

        # 总数
        index['data_count'] = {
            'article_count': self.db.list(table='article', field='count(*)', shift=1)['count(*)'],
            'product_count': self.db.list(table='product', field='count(*)', shift=1)['count(*)'],
            'order_count': self.db.list(table='order', field='count(*)', shift=1)['count(*)'],
            'picture_count': self.db.list(table='picture', field='count(*)', shift=1)['count(*)']
        }

        from kyger.kgcms import template
        return template(assign=index)
