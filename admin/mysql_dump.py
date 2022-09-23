# -*- coding:utf-8 -*-
"""MySQL 镜像处理"""

from kyger.utility import alert, log, exists, file_list, numeric, url_absolute, cipher, str_shift
from threading import Thread
from kyger.common import mysql_backup, mysql_revert, page_tpl
from math import ceil
from kyger.kgcms import template


class KgcmsApi(object):
    """MySQL备份还原"""

    kg = db = None

    dump_dir = url_absolute("backup/mysql/")  # 备份文件目录

    def __init__(self):
        pass

    def __call__(self):

        action = self.kg["get"].get("action", "")

        # 备份数据库
        if action == "backup":
            log(self.db, self.kg, 5, {"msg": "进行数据库备份操作", "state": "SUCCESS"})  # 日志记录
            Thread(target=mysql_backup, args=(self.db,)).start()
            # self.backup(self.db)
            return alert("任务已提交，系统正在处理中。",
                         "../static/timing/?task=备份数据库&time=8&url=/" + self.kg["globals"]["admin_dir"] + "/mysql_dump")

        # 还原数据库
        elif action == "revert":
            file_name = str_shift(self.kg["get"].get("file", ""))
            if exists(self.dump_dir + file_name, "file"):
                mysql_revert(self.db, file_name)
                file_name = file_name[:14] + "***" + file_name[-9:]
                log(self.db, self.kg, 5, {"msg": "进行数据库还原操作", "sql_file": file_name, "state": "SUCCESS"})  # 日志记录

                return alert("数据库还原任务执行完毕，请重新登录。", "login")
            else:
                return alert("SQL 文件不存在。", "mysql_dump")

        # 删除备份文件
        elif action == "del":
            from os import remove
            file_name = str_shift(self.kg["get"].get("file", "-"))
            file = self.dump_dir + file_name
            if exists(file, "file"):
                remove(file)
                log(self.db, self.kg, 5, {"msg": "删除数据库备份文件", "sql_file": file_name, "state": "SUCCESS"})  # 日志记录
                return alert(act=2)
            else:
                return alert("文件不存在：" + file)

        # 检查数据库/优化数据库/修复数据库/分析数据库
        elif action in ("check", "optimize", "repair", "analyze"):
            table = "`" + "`, `".join(self.db.table_list(log=False)) + "`"
            return template(assign={
                "check_list": self.db.run_sql("%s TABLE %s" % (action, table), act="list", log=False),
                "prefix": self.db.cfg["prefix"],
                "dbname": self.db.cfg["dbname"],
            })

        # 正常读取所有备份文件列表
        else:
            from os.path import getsize

            sql_list = file_list(self.dump_dir, form=0)
            sql_list.reverse()  # 降序

            # 分页
            page = numeric(self.kg["get"].get("page", 1), 1)  # 页码
            row = numeric(self.kg["cookie"].get("KGCMS_PAGE_ROWS", 10), 1, 100)  # 每页要显示的记录数
            total_page = ceil(len(sql_list) / row)  # 总页数
            if page > total_page: page = total_page
            sql_list = sql_list[((page - 1) * row): ((page - 1) * row) + row]

            # 整形 20191111075043_MvZKh3C6DXobHs8N_manu.sql
            sql_dict = []
            for i in sql_list:
                size = numeric(getsize(self.dump_dir + i)) / 1024
                size = ("%s KB" % round(size, 2)) if size < 1024 else ("%s MB" % round(size / 1024, 2))
                time = "%s-%s-%s %s:%s:%s" % (i[:4], i[4:6], i[6:8], i[8:10], i[10:12], i[12:14])
                source = "计划任务" if i[32:36] == "auto" else "手动备份"
                sql_dict.append({
                    "id": i[15:31],  # 文件名
                    "name": "%s_%s.sql" % (self.db.cfg["dbname"], i[:14]),  # 下载保存的默认文件名
                    "file": i,  # 完整文件名
                    "size": size,  # 文件大小
                    "source": source,  # 文件来源
                    "time": time,  # 格式化后的日期
                    "code": cipher(self.dump_dir + i, 1, 300)  # 下载链接有效期 300 秒
                })

            return template(assign={
                "sql_list": sql_dict,
                "prefix": self.db.cfg["prefix"],
                "dbname": self.db.cfg["dbname"],
                "page_html": page_tpl(page, total_page, row, self.kg['server']['WEB_URL']),
                'page_data': {'page': page, 'total_page': total_page, 'total_rows': len(sql_list)}
            })


