# -*- coding:utf-8 -*-
"""实时流量"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, str_replace, alert, date, url_query2dict, url_update, str_replace, mk_time, str_cutting
        from kyger.parser_ini import Config  # 配置文件读取函数
        from kyger.access import Access
        access = Access(self.db, self.kg)
        get_param = self.kg['get']
        # 删除操作
        if get_param.get('action', '') == 'del':
            if 'id' in get_param:
                self.db.dele(table='access', where=numeric(get_param['id'], 0), log=True)  # 删除操作
                return alert(act=2)
            else:
                row = self.delete(
                    webid=numeric(get_param.get('webid', 0), 0),
                    ip=get_param.get('ip', ''),
                    domain=get_param.get('domain', ''),
                    stime=get_param.get('start', ''),
                    etime=get_param.get('end', ''),
                    user=get_param.get('user', ''),
                    access_page=get_param.get('model', '')
                )
                return alert(act=2)
        # 获取数据

        else:
            if 'source' in get_param and not get_param['source']:source = 0
            else:source = get_param.get('source', '')
            data = access.list_page(
                row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),
                webid=numeric(get_param.get('webid', 0), 0),
                ip=get_param.get('ip', ''),
                domain=get_param.get('domain', ''),
                stime=get_param.get('start', ''),
                etime=get_param.get('end', ''),
                user=get_param.get('user', ''),
                access_page=get_param.get('model', ''),
                source=source,
                date='%Y-%m-%d %H:%M:%S',
                url=get_param.get('url', '')
            )
            # 时间范围
            if 'start' in get_param: start = numeric(mk_time(get_param['start'], "%Y%m%d%H%M"), 0)
            else:
                start = self.db.list(table='access', field='addtime', order='id ASC', limit=1, shift=1)
                start = start['addtime'] if start else 0
            if 'end' in get_param: end = numeric(mk_time(get_param['end'], "%Y%m%d%H%M"), 0)
            else:
                end = self.db.list(table='access', field='addtime', order='id DESC', limit=1, shift=1)
                end = end['addtime'] if end else 0

        # url合成
        button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
        web_url = url_update(url_query2dict(get_param), deld=['webid', 'filter']) + '&' if url_update(url_query2dict(get_param), deld=['webid', 'filter']) else ''
        user_url = url_update(url_query2dict(get_param), deld=['user', 'filter']) + '&' if url_update(url_query2dict(get_param), deld=['user', 'filter']) else ''
        page_url = url_update(url_query2dict(get_param), deld=['model', 'filter']) + '&' if url_update(url_query2dict(get_param), deld=['model', 'filter']) else ''
        source_url = url_update(url_query2dict(get_param), deld=['domain', 'filter']) + '&' if url_update(url_query2dict(get_param), deld=['domain', 'filter']) else ''
        ip_url = url_update(url_query2dict(get_param), deld=['ip', 'filter']) + '&' if url_update(url_query2dict(get_param), deld=['ip', 'filter']) else ''
        start_url = url_update(url_query2dict(get_param), deld='start') + '&' if url_update(url_query2dict(get_param), deld='start') else ''
        end_url = url_update(url_query2dict(get_param), deld='end') + '&' if url_update(url_query2dict(get_param), deld='end') else ''
        del_url = url_update(url_query2dict(get_param), deld=['action', 'id']) + '&' if url_update(url_query2dict(get_param), deld=['action', 'id']) else ''
        param_dict = {}
        if get_param.get('start', ''): param_dict['start'] = get_param.get('start', '')
        if get_param.get('end', ''): param_dict['end'] = get_param.get('end', '')
        select_url = url_query2dict(param_dict) + '&' if url_query2dict(param_dict) else ''
        url = {
            'button': button_url,
            'web': web_url,
            'user': user_url,
            'page': page_url,
            'source': source_url,
            'ip': ip_url,
            'start': start_url,
            'end': end_url,
            'select': select_url,
            'del': del_url
        }
        source_select = "未知地址" if source == 0 else source
        source_list = self.db.list(table='access', field='distinct source', limit='0,100')
        for var in source_list:var['source_cut'] = str_cutting(var['source'], 100)
        url_list = self.db.list(table='access', field='distinct url', limit='0,100')
        for var in url_list: var['url_cut'] = str_cutting(var['url'], 100)
        return template(
            assign={
                'data': data['list'],
                'branch': data['page_html'],
                'ip_find': Config('/config/settings.ini').get('api')['ip_find'],
                'filter': numeric(get_param.get('filter', 0), 0, 7),
                'web_list': self.db.list(table='web', field='id, name'),
                'page_list': self.db.list(table='access', field='distinct model, page', limit='0,100'),
                'start': date(start, format='%Y-%m-%d %H:%M'),
                'end': date(end, format='%Y-%m-%d %H:%M'),
                'url': url,
                'word': [get_param.get('ip', ''), get_param.get('user', ''), get_param.get('domain', '')],
                'webid': numeric(get_param.get('webid', 0), 0),
                'page': get_param.get('model', ''),
                'page_data': data['page_data'],
                'source': str_cutting(source_select, 100),
                'source_list': source_list,
                'url_list': url_list,
                'access_url': str_cutting(get_param.get('url', ''), 100),
                'page_data': data['page_data']
            }
        )

    def delete(self, webid=0, ip='', domain='', stime='', etime='', user='', access_page=''):
        from kyger.utility import mk_time
        # sql语句
        ip_sql = ' && ip like"%%%s%%"' % ip if ip else ''  # ip地址
        domain_sql = ' && domain like "%%%s%%"' % domain if domain else ''  # 域名
        start_sql = ' && addtime > %d' % mk_time(stime, "%Y%m%d%H%M") if mk_time(stime, "%Y%m%d%H%M") else ''  # 开始时间
        end_sql = ' && addtime < %d' % mk_time(etime, "%Y%m%d%H%M") if mk_time(etime, "%Y%m%d%H%M") else ''  # 结束时间
        webid_sql = ' && webid = %d' % webid if webid else ''  # 系统应用
        # 访问页面
        if access_page:
            access_page = access_page.split('/')
            if access_page[1] == "index": access_page[1] = 'index", "'
            access_page_sql = ' && model = "%s" && page in ("%s")' % (access_page[0], access_page[1])
        else:
            access_page_sql = ''
        # 用户
        if user:
            user_data = self.db.list(table='admin', field='id', where='username like "%%%s%%"' % user)  # 查管理员表
            id_list = []
            for var in user_data:
                id_list.append(str(var['id']))
            if id_list:
                user_sql = '&& (adminid in (%s) or aid like "%%%s%%")' % (','.join(id_list), user)
            else:
                user_sql = '&& aid like "%%%s%%"' % user
        else:
            user_sql = ''

        # where
        where = '%s%s%s%s%s%s%s' % (start_sql, end_sql, ip_sql, domain_sql, webid_sql, access_page_sql, user_sql)
        where = where[3::1] if where else '1'
        return self.db.dele(table='access', where=where, log=True)
