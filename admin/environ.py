# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.utility import html_escape


class KgcmsApi(object):
    """KGCMS框架接口"""

    request = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        
        environ = '<span>kg</span>: {<br /><span style="color:#629755;">　　　# Example:<br />　　　# tpl: kg[n][...]<br />　　　# py: self.kg[n][...]</span>'
        for key, values in self.kg.items():
            environ = '%s<br><br>　　　<span style="color:#629755;"># ----------------------------------------------------------------</span><br><br>　　　<span>%s</span>' % (environ, key)
            if isinstance(values, dict):
                environ = '%s: {' % environ
                for k, v in values.items():
                    if v != '':
                        if isinstance(v, (int, list, dict, tuple)):
                            environ = '%s<br>　　　　　　<span>%s</span>: <span style="color:#8888C6;">%s</span>' % (environ, k, html_escape(v))
                        else:
                            environ = '%s<br>　　　　　　<span>%s</span>: "%s"' % (environ, k, html_escape(v))
                    else:
                        environ = '%s<br>　　　　　　<span>%s</span>: ""' % (environ, k)
                if values:
                    environ = '%s<br>　　　}' % environ
                else:  # 没有数据
                    environ = '%s }' % environ
            elif isinstance(values, str):
                environ = '%s: "%s"' % (environ, html_escape(values))
            else:
                environ = '%s: <span style="color:#8888C6;">%s</span>' % (environ, html_escape(values))
        environ += '<br />}<br /><br /><br />'
        from kyger.kgcms import template
        return template(assign={'environ': environ})
