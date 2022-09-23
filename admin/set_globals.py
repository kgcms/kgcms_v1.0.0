# -*- coding:utf-8 -*-
"""全局设置"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.parser_ini import Config
        from kyger.utility import file_list, json2dict, alert, numeric, html_escape, str_replace, exists, url_absolute, dict2json_file

        # 1.获取数据
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 2.提交判断
        tab = 0
        if post_param.get('set', ''):
            set = post_param.get('set', '')
            if set == 'web':
                set_web = {
                    "debug_mode": (numeric(post_param.get('debug', 0), 0, 1), "调试模式开关"),
                    'cache_control': (numeric(post_param.get('static', 0), 0, 1), '静态文件缓存，0关闭/1开启'),
                    'cookie_expire': (numeric(post_param.get('cookie', 0)), 'Cookie过期时间，距离当前时间的小时数，支持小数：0.1H=6M，支持负数删除Cookie，0为浏览器进程'),
                    'server_protocol': (html_escape(post_param.get('protocol', '')), '服务器访问协议,http|https|auto,设置后将强制转向,auto为自动'),
                    'admin_dir': (html_escape(post_param.get('path', '')), '系统管理后台目录, 只定义该参数,不需要改物理目录名'),
                    'admin_language': (html_escape(post_param.get('language', '')), '后台语言包'),
                    'admin_template': (html_escape(post_param.get('template', '')), '后台模板'),
                    'static_path': (str_replace(html_escape(post_param.get('static_path', '')), ['，', '　', ' '], [',', '', '']), '设置项目静态文件访问目录，该目录下的文件可直接访问'),
                    'static_file': (str_replace(html_escape(post_param.get('static_file', '')), ['，', '　', ' '], [',', '', '']), '设置项目静态文件，设置的文件可直接访问'),
                    'upload_type': (str_replace(html_escape(post_param.get('filetype', '')), ['，', '　', ' '], [',', '', '']), '允许上传的文件类型, 后缀名'),
                    'upload_file_size': (numeric(post_param.get('filesize', 0), 0), '上传文件大小限制, 单位 M'),
                    'upload_imag_size': (numeric(post_param.get('imagesize', 0), 0), '上传图片大小限制, 单位 M'),
                    'mysql_log': (numeric(post_param.get('log', 0), 0, 1), '数据库操作日志是否开启, 开启后, 对数据库进行"增/删/改"操作时均将会被记录'),
                    'access_count': (numeric(post_param.get('access', 0), 0, 1), '访问统计开关，必须同时开启计划任务时有效'),
                    'task_plan': (numeric(post_param.get('task', 0), 0, 1), '自动计划任务开启，自动清理缓存文件、日志、流量统计等'),
                    'log_max_row': (int(numeric(post_param.get('log_max', 10), 0) * 10000), '日志保留最大记录数，超出将自动清理旧的日志，可根据硬件配置适当调大'),
                    'access_max_row': (int(numeric(post_param.get('access_max', 10), 0) * 10000), '访问记录保留最大数，超出将自动清理旧的记录'),
                    'editor_size': (html_escape(post_param.get('editor_width', '')) + ',' + html_escape(post_param.get('editor_height', '')), '富文本编辑器大小'),
                    'icp': (html_escape(post_param.get('icp', '')), '网站服务器/域名备案号'),
                }
                Config('config/settings.ini').set('globals', set_web)
                tab = 0
            elif set == 'weixin':
                # 微信
                set_weixin = {
                    "url": (html_escape(post_param.get('url', '')), "微信服务器接口URL"),
                    "number": (html_escape(post_param.get('number', '')), "微信公众号"),
                    "key": (html_escape(post_param.get('key', '')), "授权码"),
                    "token": (html_escape(post_param.get('token', '')), "微信接口"),
                    "id": (html_escape(post_param.get('id', '')), "微信账号原始ID"),
                    "appid": (html_escape(post_param.get('appid', '')), "开发者凭据(AppId)"),
                    "appsecret": (html_escape(post_param.get('appsecret', '')), "开发者凭据(AppSecret)"),
                    "valid_time": (numeric(post_param.get('valid_time', 7200)), '微信加密链接有效时间(秒)'),
                    "baidu_ak": (html_escape(post_param.get('ak', '')), "百度地图开发者秘钥"),
                    "nearby_search": (numeric(post_param.get('nearby_search', 0), 0, 1), '附近搜索功能，1开启，0关闭'),
                    "advanced": (numeric(post_param.get('advanced', 0), 0, 1), '高级接口，1开启，0关闭')
                }
                Config('config/settings.ini').set('weixin', set_weixin)
                tab = 1
            elif set == 'email':
                tab = 2
                # 邮箱
                set_email = {
                    "mailer": (html_escape(post_param.get('mailer', 'smtp')), "邮件发送方式"),
                    "frommail": (html_escape(post_param.get('frommail', '')), "发件箱地址"),
                    "fromname": (html_escape(post_param.get('fromname', '')), "发件人姓名"),
                    "smtphost": (html_escape(post_param.get('smtphost', '')), "SMTP服务器"),
                    "smptport": (html_escape(post_param.get('smptport', '')), "SMTP端口"),
                    "smtpauth": (html_escape(post_param.get('smtpauth', '')), "SMTP身份验证"),
                    "smtpuser": (html_escape(post_param.get('smtpuser', '')), "SMTP登陆用户名"),
                    "smtppass": (html_escape(post_param.get('smtppass', '')), 'SMTP登录密码'),
                    "starttls": (html_escape(post_param.get('starttls', 'none')), "SMTP安全连接"),
                    "enable": (numeric(post_param.get('enable', 0), 0, 1), '发送一封测试邮件，1开启，0关闭'),
                    "testaddress": (html_escape(post_param.get('testaddress', '')), "发送一封测试邮件")
                }
                Config('config/settings.ini').set('mail', set_email)
            elif set == 'ftp':
                tab = 3
                # ftp
                set_ftp = {
                    "enable": (numeric(post_param.get('enable', 0), 0, 1), '启用FTP上传文件，1开启，0关闭'),
                    "host": (html_escape(post_param.get('host', '')), "FTP主机地址"),
                    "port": (html_escape(post_param.get('port', '')), "FTP端口"),
                    "user": (html_escape(post_param.get('user', '')), "FTP用户名"),
                    "pwd": (html_escape(post_param.get('pwd', '')), "FTP密码"),
                    "root": (html_escape(post_param.get('root', '')), "网站位于FTP中的目录")
                }
                Config('config/settings.ini').set('ftp', set_ftp)
            elif set == 'sms':
                # 短信
                set_send = {
                    "sign": (html_escape(post_param.get('send_sign', '')), "签名"),
                    "id": (html_escape(post_param.get('send_account', '')), "Access Key Id"),
                    "secret": (html_escape(post_param.get('send_pswd', '')), "Access Key Secret"),
                    "url": (html_escape(post_param.get('send_url', '')), "接口地址"),
                }
                Config('config/settings.ini').set('send', set_send)
                tab = 4
            elif set == 'wxpay':
                set_wxpay = {
                    "appid": (html_escape(post_param.get('appid', '')), "APPID"),
                    "mchid": (html_escape(post_param.get('mchid', '')), "受理商ID"),
                    "key": (html_escape(post_param.get('key', '')), "密钥(key)"),
                    "appsecret": (html_escape(post_param.get('appsecret', '')), "APPSECRET"),
                    "enable": (html_escape(post_param.get('enable', '')), "是否启用"),
                }
                Config('config/settings.ini').set('wxpay', set_wxpay)
                tab = 5
            elif set == 'alipay':
                set_alipay = {
                    "account": (html_escape(post_param.get('account', '')), "支付宝登录帐号"),
                    "id": (html_escape(post_param.get('id', '')), "合作者身份(PID)"),
                    "key": (html_escape(post_param.get('key', '')), "安全校验码(Key)"),
                    "appid": (html_escape(post_param.get('appid', '')), "APPID"),
                    "rsaprivatekey": (html_escape(post_param.get('rsaprivatekey', '')), "开发者私钥"),
                    "alipayrsapublickey": (html_escape(post_param.get('alipayrsapublickey', '')), "支付宝公钥"),
                    "service": (html_escape(post_param.get('service', '')), "接口服务类型"),
                    "transport": (html_escape(post_param.get('transport', '')), "访问模式"),
                    "enable": (html_escape(post_param.get('enable', '')), "是否启用"),
                }
                Config('config/settings.ini').set('alipay', set_alipay)
                tab = 6
            elif set == "speci":
                # product = self.db.list(table='product')
                # if product: return alert(msg="清空商品才能修改规格", act=3)
                speci_name = post_param.get('speci_name', [])
                res = []
                for i in range(len(speci_name)):
                    data = {
                        "id": i,
                        "name": speci_name[i],
                        "param": post_param.get('speci_param%s' % i)
                    }
                    res.append(data)
                dict2json_file(res, file='config/speci.json')
                tab = 7
            else:
                return alert(msg='参数错误', act=3)


        # 系统设置
        config = Config('config/settings.ini').get()
        config['globals']['editor_size'] = config['globals']['editor_size'].split(',')
        if numeric(config['globals']['log_max_row']) % 10000:
            log_max_row = numeric(config['globals']['log_max_row']) / 10000
        else:
            log_max_row = numeric(config['globals']['log_max_row']) // 10000
        if numeric(config['globals']['access_max_row']) % 10000:
            access_max_row = numeric(config['globals']['access_max_row']) / 10000
        else:
            access_max_row = numeric(config['globals']['access_max_row']) // 10000
        config['globals']['log_max_row'] = log_max_row
        config['globals']['access_max_row'] = access_max_row
        language = file_list('language/backend', 2, 0)  # 获取语言包

        dir_list = file_list('template/backend', 2, 0)
        temp_data = []
        for dir_name in dir_list:
            # 如果json文件不存在不视为模板
            if not exists(url_absolute('template/backend/%s/config.json' % dir_name), 'file'):
                continue

            conf = json2dict(file='template/backend/%s/config.json' % dir_name)  # 读取配置文件
            conf['dir'] = dir_name  # 添加目录名
            temp_data.append(conf)  # 追加

        # 商品属性设置
        speci = json2dict(file='config/speci.json')
        return template(assign={'data': config, 'language': language, 'temp': temp_data, 'speci': speci, 'tab': tab})

