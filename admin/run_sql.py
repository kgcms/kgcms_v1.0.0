# -*- coding:utf-8 -*-
"""执行SQL"""

from kyger.utility import numeric, get_contents, url_absolute


class KgcmsApi(object):
    """KGCMS框架接口"""
    
    kg = db = None
    frequency = 2  # 执行一次间隔时间，秒
    sqlfile = "temp/run.sql"
    
    def __call__(self):
        
        total = numeric(self.kg["get"].get("total", 0))
        current = numeric(self.kg["get"].get("current", 0))
        if total:
            current += 1
            
            if current >= total:
                return "任务完成，已执行 %s 次" % current
            else:
                import os
                if os.path.exists(url_absolute(self.sqlfile)):
                    sql = get_contents(self.sqlfile)
                    self.db.run_sql(sql, act="add")
                else:
                    return "SQL文件不存在：" + self.sqlfile
        from kyger.kgcms import template
        return template(assign={"total": total, "current": current, "frequency": self.frequency})
