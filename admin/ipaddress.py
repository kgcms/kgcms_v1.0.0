# -*- coding:utf-8 -*-
"""IP地址管理"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, url_query2dict, url_update, alert
        from kyger.common import page_tpl
        get_param = self.kg['get']

        action = get_param.get('action', '')
        # 一键清空
        if action == "clear":
            self.db.dele('ipaddress', where='1')
            return alert(act=2)
        # 单个删除
        elif action == "del" and get_param.get('id', 0):
            del_id = numeric(get_param.get('id'), 0)
            self.db.dele('ipaddress', where=del_id)
            return alert(act=2)
        # 获取数据
        else:
            # 条件
            page = numeric(get_param.get('page', 1), 1)  # 当前页
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))  # 每页显示
            province = '&& province = "%s"' % get_param['province'] if get_param.get('province', '') else ''
            city = '&& city = "%s"' % get_param['city'] if get_param.get('city', '') else ''
            ips = '&& ips = "%s"' % get_param['ips'] if get_param.get('ips', '') else ''
            ip = '&& ip like "%%%s%%"' % get_param['word'] if get_param.get('word', '') else ''
            # where语句
            where = '1 %s %s %s %s' % (province, city, ips, ip)
            data = self.db.list(
                table="ipaddress",
                field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                where=where,
                order='id DESC',
                page=page,
                limit=row,
            )
            if page > self.db.total_page:  # 防止大于最大页码
                page = self.db.total_page
                data = self.db.list(
                    table="ipaddress",
                    field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                    where=where,
                    order='id DESC',
                    page=page,
                    limit=row,
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            # 省
            province_data = self.db.list(
                table='ipaddress',
                field='province',
                where='1 group by province'
            )
            # 城市
            if province or city or ips:
                city_data = self.db.list(
                    table='ipaddress',
                    field='city',
                    where='1 %s group by city' % province
                )
            else:
                city_data = []
            # 运营商
            ips_data = self.db.list(
                table='ipaddress',
                field='ips',
                where='1 group by ips'
            )
            # url参数合成
            province_url = url_update(url_query2dict(get_param), deld=['city', 'page', 'province'])
            province_url = province_url + '&' if province_url else ''
            city_url = url_update(url_query2dict(get_param), deld=['city', 'page'])
            city_url = city_url + '&' if city_url else ''
            ips_url = url_update(url_query2dict(get_param), deld=['ips', 'page'])
            ips_url = ips_url + '&' if ips_url else ''
            url = {'city': city_url, 'ips': ips_url, 'province': province_url}

            return template(assign={
                'list': data,
                'word': get_param.get('word', ''),
                'city': get_param.get('city', ''),
                'province': get_param.get('province', ''),
                'ips': get_param.get('ips', ''),
                'page_html': page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL')),
                'province_data': province_data,
                'city_data': city_data,
                'ips_data': ips_data,
                'url': url,
                'page_data': page_data
            })
