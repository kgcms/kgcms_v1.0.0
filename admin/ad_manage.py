# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, url_query2dict, url_update, str_replace
        from kyger.common import page_tpl
        # get参数
        get_param = self.kg['get']

        action = get_param.get('action', '')
        ad_id = numeric(get_param.get('id', 0), 0)
        if action == 'enable' and ad_id:  # 启用
            self.db.edit('ad', {'enable': 1}, ad_id)
            return alert(act=2)
        elif action == 'unenable' and ad_id:  # 禁用
            self.db.edit('ad', {'enable': 0}, ad_id)
            return alert(act=2)
        elif action == 'del' and ad_id:  # 删除
            self.db.dele('ad', ad_id)
            return alert(act=2)
        else:
            page = numeric(get_param.get('page', 1), 1)
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
            # 获取数据
            data = self.db.list(
                table='ad',
                where="webid=%s" % self.kg['web']['id'],
                page=page,
                limit=row,
                order='id desc'
            )
            if page > self.db.total_page:
                page = self.db.total_page
                data = self.db.list(
                    table='ad',
                    where="webid=%s" % self.kg['web']['id'],
                    page=page,
                    limit=row,
                    order='id desc'
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            for var in data:
                if var['expir']:
                    if var['end'] <= int(self.kg['run_start_time'][1]):
                        var['status'] = "已过期"
                    else:
                        if (var['end'] - int(self.kg['run_start_time'][1])) % 86400:
                            day = (var['end'] - int(self.kg['run_start_time'][1])) // 86400 + 1
                        else:
                            day = (var['end'] - int(self.kg['run_start_time'][1])) // 86400
                        var['status'] = "还剩%s天" % day
            page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'))
            return template(assign={"list": data, "pagehtml": page_html, 'page_data': page_data})
