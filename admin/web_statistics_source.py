# -*- coding:utf-8 -*-
"""实时流量"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, str_cutting, mk_time, date, url_query2dict, url_update
        from kyger.access import Access
        access = Access(self.db, self.kg)
        get_param = self.kg['get']

        # 来源域名
        if 'source' in get_param and not get_param['source']: source = 0
        else: source = get_param.get('source', '')
        arg_list = ['domain', 'source']
        data = access.list_page(
            field='DISTINCT %s as a, COUNT(*) as b' % arg_list[numeric(get_param.get('type', 0), 0, 1)],
            order='b DESC',
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),
            webid=numeric(get_param.get('webid', 0), 0),
            ip=get_param.get('ip', ''),
            domain=get_param.get('domain', ''),
            stime=get_param.get('start', ''),
            etime=get_param.get('end', ''),
            user=get_param.get('user', ''),
            access_page=get_param.get('model', ''),
            source=source,
            group='group by a'
        )

        for var in data['list']:
            var['a_cut'] = str_cutting(var['a'], 100)  # 限制长度
            var['rate'] = format(var['b'] / data['page_data']['group_rows'] * 100, '.2f')

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
        end_url = url_update(url_query2dict(get_param), deld='end') + '&' if url_update(url_query2dict(get_param),deld='end') else ''
        del_url = url_update(url_query2dict(get_param), deld=['action', 'id']) + '&' if url_update(url_query2dict(get_param), deld=['action', 'id']) else ''
        param_dict = {}
        if get_param.get('start', ''): param_dict['start'] = get_param.get('start', '')
        if get_param.get('end', ''): param_dict['end'] = get_param.get('end', '')
        if get_param.get('type', 0): param_dict['type'] = get_param.get('type', 0)
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
        for var in source_list: var['source_cut'] = str_cutting(var['source'], 100)
        return template(
            assign={
                'data': data['list'],
                'branch': data['page_html'],
                'type': numeric(get_param.get('type', 0), 0, 1),
                'start': date(start, format='%Y-%m-%d %H:%M'),
                'end': date(end, format='%Y-%m-%d %H:%M'),
                'filter': numeric(get_param.get('filter', 0), 0, 6),
                'web_list': self.db.list(table='web', field='id, name'),
                'page_list': self.db.list(table='access', field='distinct model, page', limit='0,100'),
                'word': [get_param.get('ip', ''), get_param.get('user', ''), get_param.get('domain', '')],
                'source': str_cutting(source_select, 100),
                'webid': numeric(get_param.get('webid', 0), 0),
                'source_list': source_list,
                'url': url,
                'page_data': data['page_data']
            }
        )


