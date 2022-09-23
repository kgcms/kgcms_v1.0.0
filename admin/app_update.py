#二维码 / Qrcode# -*- coding:utf-8 -*-
"""应用修改/创建"""
from kyger.utility import json2dict, file_list, exists, url_absolute


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import file_list, alert, numeric, html_escape, str_random, url_absolute
        from kyger.upload import Upload
        from pathlib import Path
        # 1.获取数据
        post_param = self.kg['post']  # post参数
        get_param = self.kg['get']  # get参数

        # 2.动作判断
        webid = numeric(get_param.get("webid", 0), 0)
        action = "edit" if webid else "add"

        # 提交判断
        if post_param.get("action", '') == "submit":
            # 获取qq，域名，邮箱，电话
            info_set = {'domain': [], 'qq': [], 'email': [], 'phone': []}
            for var in ['domain', 'email', 'qq', 'phone']:
                if isinstance(post_param[var], str) and len(post_param[var]): post_param[var] = [post_param[var]]
                info_set[var] = json2dict(post_param.get(var, '')) if post_param.get(var, '') else json2dict([])

            # 自动切换模板或模板文件
            if 'template_auto' in post_param:
                template_auto = json2dict({"m": post_param['m'], "pc": post_param['pc'], "wx": post_param['wx']})
                template = ''
            else:
                template = post_param['template']
                template_auto = json2dict({})

            # 默认设置
            default = 1 if 'default' in post_param else 0
            enable = 1 if 'enable' in post_param else 0

            # 插入数据整合
            insert_data = {
                'default': default,
                'name': html_escape(post_param.get('name', '')),
                'domain': info_set['domain'],
                'language': post_param.get('language', ''),
                'template': template,
                'template_auto': template_auto,
                'title': html_escape(post_param.get('title', '')),
                'keyword': html_escape(post_param.get('keyword', '')),
                'description': html_escape(post_param.get('description', '')),
                'copyright': post_param.get('copyright', ''),
                'email': info_set['email'],
                'qq': info_set['qq'],
                'enable': enable,
                'phone': info_set['phone'],
                'address': html_escape(post_param.get('address', '')),
                'sort': numeric(post_param.get('sort', 20)),
            }

            # logo图片
            upload_image = post_param.get('image', '')  # 获取logo图片数据，一个列表第一条为原图，第二条为裁剪图
            image = ''
            if upload_image[0]: image = upload_image[0]
            if upload_image[1]: image = upload_image[1]
            if image:  # 如果有值就存储
                up = Upload(image, self.db, self.kg, base64=True)
                up.path = 0  # 不创建路径
                up.exist_rename = False
                up.filename = 'logo_{y}{mm}{dd}{hh}{ii}{ss}' if action == "add" else 'logo_%s' % webid
                msg = up.image('system/app')
                insert_data['logo'] = msg['url']
            else:  # 没有则为空
                if action == "add": insert_data['logo'] = ""

            # 二维码图片
            qrcode_image = post_param.get('qrcode', '')  # 取二维码图片数据
            if qrcode_image:
                if isinstance(qrcode_image, str):
                    qrcode_image = [qrcode_image]
                qrcode = []
                pic_index = 0
                for image in qrcode_image:
                    up = Upload(image, self.db, self.kg, base64=True)
                    up.path = 0  # 不创建路径
                    up.exist_rename = False
                    if action == "add":
                        up.filename = 'qrcode_{y}{mm}{dd}{hh}{ii}{ss}' + str_random(5, 0, 1)
                    else:
                        up.filename = 'qrcode_%s_%s' % (webid, pic_index)
                    msg = up.image('system/app')
                    qrcode.append(msg['url'])
                    pic_index += 1
                insert_data['qrcode'] = json2dict(qrcode)
            else:
                insert_data['qrcode'] = json2dict([])

            # 操作
            if action == "add":  # 添加
                insert_data['addtime'] = int(self.kg['run_start_time'][1])  # 添加时间
                msg = self.db.add('web', insert_data, log=True)
                if numeric(msg):  # 判断是否添加成功
                    if default: self.db.edit('web', {'default': 0}, where='`id` != %d' % msg)  # 如果默认其他修改为非默认
                    return alert(act="app_manage")
                return alert("添加失败", 3)
            else:  # 修改
                msg = self.db.edit('web', insert_data, webid, 1)
                if numeric(msg):  # 判断是否修改成功
                    if default: self.db.edit('web', {'default': 0}, where='`id` != %d' % webid)  # 如果默认其他修改为非默认
                    return alert(act="app_manage")
                return alert("修改失败", 3)
        # 非提交数据
        else:
            if action == "edit":
                import base64
                from kyger.utility import file_mime_type
                web_data = self.db.list(table='web', where=webid, shift=1)
                # 对JSON数据进行转换
                for row in ['domain', 'template_auto', 'phone', 'email', 'qq', 'qrcode']:
                    web_data[row] = json2dict(web_data[row])
                qrcode = []
                import os
                curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                for path in web_data['qrcode']:  # 二维码转Base64
                    isfile = Path(curPath+path)
                    if isfile.is_file():
                        with open(url_absolute(curPath+path), "rb") as f:
                            base64_data = base64.b64encode(f.read())
                        mime = file_mime_type(path)
                        qrcode.append({'MIME': mime, 'data': str(base64_data)[2: -1]})
                web_data['qrcode'] = qrcode
            else:
                web_data = {}
            data = {
                'default': web_data.get('default', 0),
                'name': web_data.get('name', ''),
                'domain': web_data.get('domain', [""]),
                'language': web_data.get('language', ''),
                'template': web_data.get('template', ''),
                'template_auto': web_data.get('template_auto', {"m": "", "pc": "", "wx": ""}),
                'title': web_data.get('title', ''),
                'logo': web_data.get('logo', self.kg['tpl_url'] + 'images/logo.png'),
                'qrcode': web_data.get('qrcode', []),
                'keyword': web_data.get('keyword', ''),
                'description': web_data.get('description', ''),
                'copyright': web_data.get('copyright', ''),
                'email': web_data.get('email', [""]),
                'qq': web_data.get('qq', [""]),
                'phone': web_data.get('phone', [""]),
                'address': web_data.get('address', ""),
                'enable': web_data.get('enable', 1),
                'sort': web_data.get('sort', 20)
            }

            language = file_list('language/frontend', 2, 0)  # 获取语言包
            temp = self.template_path('template/frontend', 0)  # 获取所有模板
            temp_auto = self.template_path('template/frontend', 1)  # 获取auto|wx|pc|m的模板
            return template(assign={'data': data, 'language': language, 'template': temp, 'temp_auto': temp_auto, 'action': action})

    def template_path(self, path, template_auto=0):
        """
        获取模板
        :param path: [str] 模板存放的路径
        :param template_auto: [int] 获取自动或通用模板，0表示通用，1表示自动。缺省值0
        :return: [list{}] 返回一个
        """
        dir_list = file_list(path, 2, 0)
        data = [[], [], []]
        # 判断是否存在路径
        if dir_list:
            for dir in dir_list:
                # json文件不存在执行下一个循环
                if not exists(url_absolute('template/frontend/%s/config.json' % dir), type='file'):
                    continue
                # json文件存在
                config = json2dict(file='template/frontend/%s/config.json' % dir)  # 读取配置文件
                config['dir'] = dir  # 添加目录名
                if template_auto:  # 自动模板
                    # 获取模板类型并添加
                    if 'auto' in config['type']:  # auto全部添加
                        for i in range(3):
                            data[i].append(config)
                        continue
                    if 'pc' in config['type']: data[0].append(config)  # pc
                    if 'wx' in config['type']: data[1].append(config)  # 微信
                    if 'm' in config['type']: data[2].append(config)  # 手机
                else:  # 获取通用模板
                    data.append(config)  # 追加
        return data
