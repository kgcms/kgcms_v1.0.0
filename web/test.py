# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *
from kyger.common import un_pack



class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        return Weixin(self.db, self.kg).get_groups()
        # import sys
        # sys.path.append(url_absolute('tools'))
        # try:
        #     from alipay import AliPay
        #
        #     app_private_key_string = get_contents("private_keys.pem")
        #     alipay_public_key_string = get_contents("public_key.pem")
        #
        #     alipay = AliPay(
        #         appid="2016101800717941",
        #         app_notify_url=None,
        #         app_private_key_string=app_private_key_string,
        #         alipay_public_key_string=alipay_public_key_string,
        #         sign_type="RSA2",
        #         debug=True,
        #     )
        #     order_string = alipay.api_alipay_trade_page_pay(
        #         out_trade_no='12312456486123',
        #         total_amount='0.01',
        #         subject='测试text%s' % 1,
        #         return_url=None,
        #         notify_url=None,
        #     )
        # except Exception as e:
        #     return e
        #
        # return alert(act='https://openapi.alipaydev.com/gateway.do?' + order_string)
