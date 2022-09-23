# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.common import page_tpl
        get_param = self.kg['get']

        data = json2dict(get_contents('http://client.kgcms.com/template/page/template.json'))  # 总数据
        filter_id = numeric(get_param.get('filter', 0), 0, 4)
        filter_list = ['', 'auto', 'pc', 'm', 'wx']
        filter_data = []
        # 获取已安装模板
        dir_list = file_list('template/frontend', 2, 0)
        template_id = []
        for row in dir_list:
            if not exists(url_absolute('template/frontend/%s/config.json' % row), 'file'): continue
            config = json2dict(file='template/frontend/%s/config.json' % row)  # 读取配置文件
            template_id.append(config['tid'])
        for var in data:
            if filter_list[filter_id] in eval(var['type'])or 'auto' in eval(var['type']) or not filter_id:  # 数据筛选
                types = []
                var['code'] = cipher(var['download'], 1, 300)  # 下载链接有效期 300 秒
                var['state'] = 1 if var['tid'] in template_id else 0  # 是否启用
                if "auto" in var['type']:
                    types = ["电脑", "手机", "微信"]
                else:
                    title = {"pc": "电脑", "phone": "手机", "wx": "微信"}
                    for m in eval(var['type']):
                        types.append(title[m])
                var['types'] = '、'.join(types)  # 模板类型
                filter_data.append(var)
        total_page = (len(filter_data) // 10) + 1 if len(filter_data) % 10 else len(filter_data) // 10
        page = numeric(get_param.get('page', 1), 1, total_page)  # 当前页
        pagehtml = page_tpl(page, total_page, 10, self.kg['server'].get('WEB_URL'))  # 分页html
        page_data = {'page': page, 'total_page': total_page, 'total_rows': len(filter_data)}
        return template(assign={
            'list': filter_data[10 * (page - 1):10 * page],
            'page_html':pagehtml,
            'filter': filter_id,
            'page_data': page_data
        })
