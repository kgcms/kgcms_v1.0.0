# -*- coding:utf-8 -*-
"""MySQL 镜像处理"""

from kyger.utility import alert, log, exists, file_list, numeric, url_absolute, cipher, str_shift, date, json2dict, file_mime_type
import os
import re
from kyger.common import page_tpl, un_pack
from zipfile import ZipFile
import tarfile
from kyger.kgcms import template


class KgcmsApi(object):
    """MySQL备份还原"""

    kg = db = None

    dump_dir = url_absolute("backup/template/")  # 备份文件目录

    def __init__(self):
        pass

    def __call__(self):
        get_param = self.kg['get']

        action = get_param.get('action', '')
        if action == "revert" and get_param.get('file', ''):  # 还原备份
            file = get_param.get('file', '')
            if file not in file_list('backup/template', 1, 0):  # 判断文件是否存在
                return alert(msg="该文件不存在", act=3)
            un_pack(self.dump_dir + file, 'template/frontend')  # 还原
            return alert(act=2)
        elif action == "del" and get_param.get('file', ''):  # 删除备份
            file = get_param.get('file', '')
            if file not in file_list('backup/template', 1, 0):  # 判断文件是否存在
                return alert(msg="该文件不存在", act=3)
            os.remove(self.dump_dir + file)
            return alert(act=2)
        else:
            files = file_list('backup/template', 1, 0)
            data = []
            for row in files:
                name_list = row.split('.')[0].split('_')
                # 读取压缩文件内的config.json获取模板名字
                if file_mime_type(row) == "application/zip":  # zip
                    myzip = ZipFile(url_absolute(self.dump_dir + row))
                    config = myzip.open(name_list[3] + '/config.json').read().decode()
                    config = json2dict(re.sub('/\*.*\*/', '', config))
                elif file_mime_type(row) == "application/x-tar":  # tar
                    mytar = tarfile.open(url_absolute(self.dump_dir + row), "r:gz")
                    config = mytar.extractfile(name_list[3] + '/config.json').read().decode()
                    config = json2dict(re.sub('/\*.*\*/', '', config))
                # 文件大小
                size = numeric(os.path.getsize(self.dump_dir + row)) / 1024
                size = ("%s KB" % round(size, 2)) if size < 1024 else ("%s MB" % round(size / 1024, 2))
                # 文件来源
                source = "计划任务" if name_list[2] == "auto" else "手动备份"
                data.append({
                    'file': row,
                    'id': name_list[1],
                    'name': '%s_%s.%s' % (name_list[3], name_list[0], row.split('.')[1]),
                    'addtime': date(os.path.getctime(url_absolute('backup/template/' + row)), '%Y-%m-%d %H:%M:%S'),
                    'size': size,
                    "source": source,  # 文件来源
                    "code": cipher(self.dump_dir + row, 1, 300),  # 下载链接有效期 300 秒,
                    "title": config['name'],
                })
            return template(assign={"list": data})


