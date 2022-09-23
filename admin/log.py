# -*- coding:utf-8 -*-
"""系统日志"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.log import Log
        from kyger.parser_ini import Config  # 配置文件读取函数
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, url_query2dict, url_update, str_replace
        log = Log(self.db, self.kg)
        get_param = self.kg['get']

        # 日志删除
        action = get_param.get('action', '')
        if action == 'del':
            # 将id转成列表
            id_list = get_param['id'] if isinstance(get_param['id'], list) else [get_param['id']]
            id_sql = ','.join(id_list)
            # 判断是否允许删除
            res = self.db.list(table='log', field='count(*)', shift=1)
            if res['count(*)'] > log.sql_row:  # 判断是否大于限制数
                where = '`id` in (%s) && `addtime` < %d' % (id_sql, (int(self.kg['run_start_time'][1]) - log.day * 86400))  # 判断是否大于设定天数
                rows = self.db.dele(table='log', where=where, log=True)  # 删除操作
                if rows: return alert(msg='成功删除%d条记录' % rows, act='log')
                else: return alert(msg='删除失败，近期的日志不能删除', act=3)
            return alert(msg='删除失败，近期的日志不能删除', act=3)

        # 是否刷新参数
        if 'refresh' in get_param and get_param['refresh'] == '1':
            return alert(act='log')

        # 不符合以上条件则调用数据
        type = numeric(get_param.get('type', 0), 0, len(log.config_type) - 1) if numeric(get_param.get('type', 0),0, len(log.config_type) - 1) else 0

        data = log.list_page(
            type=type,
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),
            aid=numeric(get_param.get('aid', 0), 0),
            word=get_param.get('word', '')
        )

        # 获取分页模板
        branch_html = data['page_html']
        # 获取所有管理员的username和id
        admin = self.db.list(table='admin', field='`username`,`id`')
        admin.insert(0, {'username': '所有管理员', 'id': 0})

        # url合成
        # url参数合成
        button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
        aid_url = url_update(url_query2dict(get_param), deld='aid') + '&' if url_update(url_query2dict(get_param), deld='aid') else ''
        type_url = url_update(url_query2dict(get_param), deld='type') + '&' if url_update(url_query2dict(get_param), deld='type') else ''
        url = {
            'button': button_url,
            'aid': aid_url,
            'type': type_url,
        }
        return template(
            assign={
                'data': data['list'],
                'branch': branch_html,
                'admin': admin,
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'aid': numeric(get_param.get('aid', 0), 0),
                'filter': numeric(get_param.get('type', 0), 0, len(log.config_type) - 1),
                'log_type': log.config_type,
                'url': url,
                'ip_find': Config('/config/settings.ini').get('api')['ip_find'],
                'page_data': data['page_data']
            }
        )



