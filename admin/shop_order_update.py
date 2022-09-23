# -*- coding:utf-8 -*-
"""网站导航"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import json2dict, numeric, alert

        get_param = self.kg['get']
        post_param = self.kg['post']
        product_list = []
        discount = 1  # 会员折扣
        # 计算商品价格
        count_money = 0
        table = " `{pr}order` a, `{pr}shipping` b "
        field = 'a.*, b.`title`, b.`id` as shipping_id '
        where = 'a.`dispatching`= b.`id` and  a.`webid`=%s and  a.`id`=%s  ' % (self.kg['web']['id'], get_param.get('id', 1))
        data_list = self.db.list(
            table=table,
            field=field,
            where=where,
            shift=1
        )
        if data_list:
            # 价格数量属性处理成list
            data_list['number'] = json2dict(data_list['number'])
            data_list['price'] = json2dict(data_list['price'])
            for i in range(len(data_list['number'])):
                count_money += data_list['number'][i] * data_list['price'][i]
            # 会员折扣
            if data_list['uid'] > 0:
                level_data = self.db.list(
                    table='user',
                    field='level',
                    where=data_list['uid'],
                    shift=1
                )
                level_list = level_data['level'][1:-1:1]
                discount = self.db.list(
                    table='rank',
                    field='discount',
                    where='webid=%s and id in (%s)' % (self.kg['web']['id'], level_list),
                    shift=1
                )['discount']

            # 属性处理成list
            if len(json2dict(data_list['attribute'])) != 0:
                data_list['attribute'] = json2dict(data_list['attribute'])
            # 商品信息表
            product_list = self.db.list(
                table='product',
                field='*',
                where='webid=%s and `id`in (%s)' % (self.kg['web']['id'], data_list['pid'][1:-1:1])
            )
        lens = len(product_list)
        # 配送方式
        shipping_list = self.db.list(
            table='shipping',
            field='id, title ',
            where=''
        )

        # ********************************接受提交的数据并处理
        # 会员ID
        if post_param.get('uid', 0) == '匿名用户':
            uid = 0
        else:
            uid = numeric(post_param.get('uid', 0), 0)
        # 商品信息处理
        pid = []
        number = []
        price = []
        attribute = []
        amount = 0
        for i in range(lens):
            pid.append(numeric(post_param.get('p_id%s' % (i + 1), 0), 0))
            n = numeric(post_param.get('p_number%s' % (i + 1), 0), 0)
            number.append(n)
            p = numeric(post_param.get('p_price%s' % (i + 1), 0), 0)
            price.append(p)
            attribute.append(post_param.get('p_attribute%s' % (i + 1), ''))
            amount += n * p

        # 总价格= 商品价格*会员折扣 + 手续费(包含保价费)
        amount = amount * discount + numeric(post_param.get('freight', 0), 0)

        edit_data = {
            'oid': post_param.get('oid', ''),
            'uid': uid,
            'type': 1 if post_param.get('type', 0) == '微信营销领奖' else 0,
            'waybill': post_param.get('waybill', ''),
            'freight': numeric(post_param.get('freight', 0), 0),
            'customer': 1 if post_param.get('customer', 0) == 'on' else 0,
            'vouch': 1 if post_param.get('vouch', 0) == 'on' else 0,
            'status': int(post_param.get('status', 0)),
            'dispatching': numeric(post_param.get('dispatching', 1), 1),
            'consignee': post_param.get('consignee', ''),
            'mobile': post_param.get('mobile', ''),
            'address': post_param.get('address', ''),
            'tel': post_param.get('tel', ''),
            'email': post_param.get('email', ''),
            'besttime': post_param.get('besttime', ''),
            'building': post_param.get('building', ''),
            'zipcode': post_param.get('zipcode', ''),
            'message': post_param.get('message', ''),
            'reply': post_param.get('reply', ''),
            'pid': json2dict(pid),
            'number': json2dict(number),
            'price': json2dict(price),
            'amount': amount,
            'attribute': json2dict(attribute),
        }

        if post_param.get('action', '') == 'submit':
            where = 'webid=%s and id=%s' % (self.kg['web']['id'], numeric(get_param.get('id', 1), 1))
            self.db.edit('order', edit_data, where)
            return alert(act=2)

        return template(
            assign={
                'data': data_list,
                'lens': lens,
                'product_list': product_list,
                'shipping_list': shipping_list,
                'count_money': count_money,
                'discount': discount,
            },
            function=[],
            tpl=self.kg['tpl'],
        )
