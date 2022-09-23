# -*- coding:utf-8 -*-
"""网站模板管理"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        import os
        get_param = self.kg['get']

        action = get_param.get('action', '')
        # 通用模板
        if action == "enable" and get_param.get('template', '') and self.kg['web']['template']:  # 启用模板
            temp_name = get_param.get('template', '')
            self.db.edit('web', {'template': temp_name}, numeric(self.kg['web']['id'], 0))
            return alert(act=2)
        # 自动模板
        elif action in ['wx', 'm', 'pc'] and get_param.get('template', '') and not self.kg['web']['template']:
            temp_name = get_param.get('template', '')
            template_auto = self.kg['web']['template_auto']
            template_auto[action] = temp_name
            self.db.edit('web', {"template_auto": json2dict(template_auto)}, numeric(self.kg['web']['id'], 0))
            return alert(act=2)
        # 备份模板
        elif action == "backup" and get_param.get('template', ''):
            temp_name = get_param.get('template', '')
            if temp_name not in file_list('template/frontend', 2, 0): return alert(msg="没有找到该模板", act=3)
            from kyger.common import make_pack
            make_pack(
                source='template/frontend/%s' % temp_name,  # 要备份的文件
                path='backup/template/',  # 备份到的路径
                type=0,  # zip压缩
                file_name=date(int(self.kg['run_start_time'][1]), '%Y%m%d%H%M%S_') + str_random(16) + '_manu_' + temp_name  # 文件命名
            )  # 备份到backup/template
            return alert(act=2)
        # 删除模板
        elif action == "del" and get_param.get('template', ''):
            temp_name = get_param.get('template', '')
            res = self.db.list(table='web', where='template = "%s" or template_auto like \'%%"%s"%%\'' % (temp_name, temp_name))
            if res:
                return alert(msg="改模板正在被使用无法删除", act=3)
            else:
                import shutil
                shutil.rmtree(url_absolute('template/frontend/%s' % temp_name))
                return alert(act=2)
        else:
            dir_list = file_list('template/frontend', 2, 0)
            template_list = []
            for row in dir_list:
                if not exists(url_absolute('template/frontend/%s/config.json' % row), 'file'): continue
                config = json2dict(file='template/frontend/%s/config.json' % row)  # 读取配置文件
                config['dir'] = row  # 添加目录名
                config['thumbnail'] = 'template/frontend/%s/%s' % (row, config['thumbnail'])
                config['addtime'] = int(os.path.getctime(url_absolute('template/frontend/%s/config.json' % row)))
                types = []
                if "auto" in config['type']: types = ["电脑", "手机", "微信"]
                else:
                    title = {"pc": "电脑", "phone": "手机", "wx": "微信"}
                    for var in eval(config['type']):
                        types.append(title[var])
                config['types'] = '、'.join(types)
                # 启用的应用
                res = self.db.list(table='web', field='name', where='template = "%s" or template_auto like \'%%"%s"%%\'' % (row, row))
                config['app'] = []
                for var in res:
                    config['app'].append(var['name'])
                template_list.append(config)
            sorted(template_list, key=lambda template_list: template_list['addtime'], reverse=True)
            return template(assign={'list': template_list})




