# -*- coding:utf-8 -*-
"""添加收货地址"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'consignee': [16, "收货人长度不允许超过16个字符"],
            'areap': [32, "省长度不允许超过32个字符"],
            'areac': [32, "市长度不允许超过32个字符"],
            'aread': [32, "区、乡镇长度不允许超过32个字符"],
            'address': [64, "地址长度不允许超过64个字符"],
            'zipcode': [16, "邮编长度不允许超过16个字符"],
            'tel': [32, "联系电话长度不允许超过32个字符"],
            'mobile': [32, "收货人手机号码长度不允许超过32个字符"],
        }
        # 必填检测
        self.must_input = {
            'consignee': '收货人姓名',
            'areap': '收货地址',
            'areac': '收货地址',
            'aread': '收货地址',
            'address': '收货地址',
            'zipcode': '邮政编码',
            'tel': '联系电话',
            'mobile': '收货人手机号码'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, html_escape, alert
        from kyger.product import Product
        get_param = self.kg['get']
        post_param = self.kg['post']
        address_id = numeric(get_param.get('id', 0))
        act = 'edit' if address_id else 'add'
        if post_param.get('action') == "submit":
            data = {
                'uid': self.kg['user']['id'],
                'consignee': html_escape(post_param.get('consignee', '')),
                'areap': post_param.get('areap', ''),
                'areac': post_param.get('areac', ''),
                'aread': post_param.get('aread', ''),
                'address': html_escape(post_param.get('address', '')),
                'zipcode': html_escape(post_param.get('zipcode', '')),
                'tel': html_escape(post_param.get('tel', '')),
                'mobile': html_escape(post_param.get('mobile', '')),
                'default': numeric(post_param.get('default', 0), 0, 1),
            }
            # 数据长度检测
            for key in self.long_check:
                if len(data[key]) > self.long_check[key][0]: return alert(msg=self.long_check[key][1], act=3)

            # 必填数据检测
            for key in self.must_input:
                if not data[key]: return alert(msg='%s必须填写' % self.must_input[key], act=3)

            if act == 'edit':
                msg = self.db.edit('address', data, address_id)
                if isinstance(msg, int):
                    if data['default'] == 1:
                        self.db.edit('address', {'default': 0},
                                     'uid=%s && id != %s' % (self.kg['user']['id'], address_id))
                    return alert(act='/user/my_address_mobile')
                else:
                    return alert(msg='修改失败:%s' % msg, act=3)
            else:
                data['addtime'] = int(self.kg['run_start_time'][1])
                data['del'] = 0
                msg = self.db.add('address', data)
                if msg:
                    if data['default'] == 1:
                        self.db.edit('address', {'default': 0}, 'uid=%s && id != %s' % (self.kg['user']['id'], msg))
                    return alert(act='/user/my_address_mobile')
                else:
                    return alert(msg='添加失败:%s' % msg, act=3)

        else:
            if act == "edit":
                address_data = self.db.list(
                    table='address',
                    field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                    where='id=%s && del=0' % address_id,
                    shift=1
                )
                if not address_data: return alert(msg='该收货地址不存在', act=3)
            else:
                address_data = {}
            data = {
                'consignee': address_data.get('consignee', ''),
                'tel': address_data.get('tel', ''),
                'areap': address_data.get('areap', ''),
                'areac': address_data.get('areac', ''),
                'aread': address_data.get('aread', ''),
                'address': address_data.get('address', ''),
                'zipcode': address_data.get('zipcode', ''),
                'mobile': address_data.get('mobile', ''),
                'email': address_data.get('email', ''),
                'besttime': address_data.get('besttime', ''),
                'building': address_data.get('building', ''),
                'default': address_data.get('default', 0),
            }
            self.kg['address'] = data
            return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
