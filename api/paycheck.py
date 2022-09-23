# -*- coding:utf-8 -*-
"""支付校验"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.payment import WxPay
        from kyger.common import xml_data
        wechat = WxPay(self.db, self.kg)
        post_param = self.kg['post']
        params = xml_data(post_param)

        sign = params.pop('sign')  # 取出签名
        back_sign = wechat.get_sign(params)  # 计算签名
        # 验证签名是否与回调签名相同
        # dict2json_file(params, file='temp/temp.json')
        if sign == back_sign and params['return_code'] == 'SUCCESS':
            # 修改支付状态
            order_number = params['out_trade_no']
            order_data = self.db.list(table='order', where='oid="%s"' % order_number, shift=1)
            if order_data['status'] == 0:
                if order_number.startswith('NR'):
                    # 如果为在线充值（给他充上）
                    res = self.db.list(
                        table='%sorder as a, %suser as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                        field="a.uid, a.oid, a.amount, b.id, b.money",
                        where="a.uid=b.id && a.oid='%s'" % order_number,
                        shift=1
                    )
                    self.db.edit('order', {'status': 4}, 'oid="%s"' % order_number)
                    self.db.edit('user', {'money': res['money'] + res['amount']}, res['id'])
                else:
                    self.db.edit('order', {'status': 1}, 'oid="%s"' % order_number)
            return '<xml><return_code>SUCCESS</return_code><return_msg>OK</return_msg></xml>'
        return '<xml><return_code>FAIL</return_code><return_msg>SIGNERROR</return_msg></xml>'