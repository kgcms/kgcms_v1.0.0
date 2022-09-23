# -*- coding:utf-8 -*-
"""开放过程处理，无限制，所有用户均可访问"""
from kyger.utility import *

class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        self.ajax_show_page = 3  # 允许ajax异步加载的最大页数
        self.ajax_show_rows = 10  # ajax异步的每页条数

    def __call__(self):
        action = self.kg['get'].get('action', '')  # 事件
        value = self.kg['get'].get('value', '')  # 参数
        post_param = self.kg['post']
        get_param = self.kg['get']

        if post_param.get('action') == '':
            return "ok"

        # 后台文件下载
        # local_url = '/api/unlimited_process?action=download&id=%s&name=%s&code=%s'
        # mirror_url = '/api/unlimited_process?action=download&id=%s&mirror=1&url=%s'
        elif action == "download":
            # 文件下载写日志
            self.kg['server']['WEB_URL'] = self.kg['server'].get('HTTP_REFERER')
            log_data = {
                'id': numeric(self.kg['get'].get('id', 0), 0),
                'url': self.kg['server'].get('HTTP_REFERER')
            }
            log(self.db, self.kg, type=12, info={"state": "SUCCESS", "msg": json2dict(log_data)})

            mirror = numeric(self.kg['get'].get('mirror', 0), 0, 1)

            # 镜像下载
            if mirror:
                return alert(act=self.kg['get'].get('url'))

            # 本地下载
            else:
                from os.path import basename, getsize
                save_name = self.kg['get'].get('name', '')  # 保存时默认新的文件名，为空时将采用旧文件名
                file = self.kg['get'].get('code', '')  # 下载路径，经过加密的路径

                file = url_absolute(cipher(file))  # 要下载的文件完整路径解密
                if save_name:
                    save_name = save_name + file_extension(file)
                else:
                    save_name = basename(file)

                self.response_headers = {
                    'code': '200 OK',
                    'headers': [
                        ('Accept', 'bytes'),
                        ("Cache-Control", "must-revalidate, post-check=0, pre-check=0"),
                        ("Content-Description", "File Transfer"),
                        ("Content-Type", "application/octet-stream"),
                        ("Content-Length", str(getsize(file))),
                        ("Content-Disposition", "attachment; filename=" + save_name),
                    ]
                }
                r = open(file, 'rb').read()
                return r

        elif action == "ad":
            from kyger.ad import Advertise
            ad_id = numeric(self.kg['get'].get('id', 0))  # 广告id
            index = numeric(self.kg['get'].get('index', 0))  # 第几个链接

            ad_data = self.db.list(table='ad', where=ad_id, shift=1)  # 通过id获取广告数据
            if not ad_data: return notfound_404()  # 没有这个id的广告

            # 获取链接
            ad = Advertise(self.db, self.kg)
            links = ad.ad_link(ad_data['code'])
            if index > (len(links['link']) - 1): return notfound_404()  # 超过链接索引值

            # 点击次数
            url = self.kg['server']['PATH_INFO'] + "?action=ad&id=%s" % ad_id
            limit_time = int(self.kg['run_start_time'][1]) - ad.limit_time  # 时间限制
            ip = self.kg['server']['HTTP_ADDR']
            where = '`ip` = "%s" && `addtime` > %s &&`url` like "%%%s%%"' % (ip, limit_time, url)
            record = self.db.list(table='access', where=where)
            if not record:  # 没有访问过
                self.db.edit('ad', {'click': ad_data['click'] + 1}, ad_id)
            return alert(act=links['link'][index])

        elif action == 'setapp':  # 设置系统应用
            webid = numeric(self.kg['get'].get('id', 0), 0)
            if webid and self.db.list(table='web', where='id = %d' % webid):
                self.set_cookie = {'KGCMS_APP_ID': webid}  # 设置cookie

            return alert(act=url_parse(self.kg['environ']['HTTP_REFERER'], 'path'))  # 返回上一页并刷新

        # 支付
        elif action == 'pay':
            code = get_param.get('code', '')
            if not code: return alert(msg='参数错误', act=3)

            # 解密code {'order_number': 'ES20191220155622255'}
            order = json2dict(cipher(code))
            if not isinstance(order, dict) or not order.get('order_number'):
                return alert(msg='参数错误', act=3)

            # 获取订单数据
            order_data = self.db.list(table='order', where='oid="%s"' % order['order_number'], shift=1)
            if not order_data: return alert(msg='订单不存在', act=3)

            # 判断订单过期时间
            if order_data['addtime'] + 7000 < int(self.kg['run_start_time'][1]):
                self.db.edit('order', {'status': -4}, order_data['id'])
                return alert(msg='订单已过期', act='/user/order')

            if order_data['payment'] == 2:
                from kyger.payment import WxPay
                weixin = WxPay(self.db, self.kg)
                order_type = {'BP': '浏览权限购买', 'NR': '在线充值', 'AR': '管理员手动充值', 'CS': '消费购买', 'ES': '订单提交', 'TE': '其它交易'}
                body = '%s-%s' % (self.kg['web']['title'], order_type[order_data['oid'][0:2]])
                res = weixin.wxpay(order_data['oid'], int(order_data['amount'] * 100), body)
                if res['status'] == 'success':
                    from kyger.kgcms import template
                    return template(
                        assign={
                            "qrcode": res['qrcode'],
                            "amount": order_data['amount'],
                            'oid': order_data['oid']
                        },
                        tpl='pay.tpl'
                    )
                else:
                    return alert(msg=res.get('msg', ''), act=3)

            # 支付宝
            elif order_data['payment'] == 3:
                pass

            # 账户余额支付
            elif order_data['payment'] == 1:
                if self.kg['user']['money'] < order_data['amount']: return alert(msg='余额不足', act=3)
                money = self.kg['user']['money'] - order_data['amount']
                self.db.run_sql('UPDATE `%suser` SET money=%s WHERE id=%s' % (self.db.cfg["prefix"], money, self.kg['user']['id']), log=False)
                self.db.run_sql('UPDATE `%sorder` SET status=1 WHERE id=%s' % (self.db.cfg["prefix"], order_data['id']), log=True)
                return alert(act='/user/order')
            else:
                return alert(msg='不支持的支付方式', act=3)

        elif action == 'set_view':  # 设置视图类型
            value = get_param.get('value', '')  # 参数
            if value == "list": self.set_cookie = {'KGCMS_PAGE_VIEW': 'list'}  # 设置cookie
            if value == "simple": self.set_cookie = {'KGCMS_PAGE_VIEW': 'simple'}  # 设置cookie
            return alert(act=2)

        elif action == 'ajax_load':  # 4大模块异步加载
            page = numeric(get_param.get('page', 1))
            module = get_param.get('module', '')
            category = numeric(get_param.get('cid', 0), 0)
            if not all[page, module]: return json2dict({'status': 1, "msg": '参数出错'}, trans=False)
            if page > self.ajax_show_page: return json2dict({'status': 2, "msg": '超出限制参数'}, trans=False)

            from kyger.article import Article
            from kyger.product import Product
            from kyger.picture import Picture
            from kyger.download import Download

            if module == 'article':
                data = Article(self.db, self.kg).list_page(0, self.ajax_show_rows, 0, category)
            elif module == 'product':
                data = Product(self.db, self.kg).list_page(0, self.ajax_show_rows, 0, category)
            elif module == 'download':
                data = Download(self.db, self.kg).list_page(0, self.ajax_show_rows, 0, category)
            elif module == 'picture':
                data = Picture(self.db, self.kg).list_page(0, self.ajax_show_rows, 0, category)
            else:
                return json2dict({'status': 1, "msg": '参数出错'}, trans=False)
            return json2dict({"status": 0, 'list': data['list'], 'page_data': data['page_data']}, trans=False)

        pass
