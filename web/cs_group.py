# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        group = self.db.list(table='cs_group')
        return template(assign={'data':group})
