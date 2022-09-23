# -*- coding:utf-8 -*-
"""查看订单"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        self.order_try = 3  # 下单尝试次数
        self.status = {
            0: '等待付款',
            1: '已支付，等待发货',
            2: '订单已确认，配货中',
            3: '已发货，等待用户签收',
            4: '已签收，交易完毕',
            -1: '要求退货',
            -2: '拒绝退货，前台交易完毕',
            -3: '退货完毕，订单结束',
            -4: '订单已取消'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.product import Product
        post_param = self.kg['post']
        get_param = self.kg['get']

        if get_param.get('action', '') == 'return':
            id = numeric(get_param.get('id'))
            if not id: return alert(msg='参数错误', act=3)
            order_data = self.db.list(table='order', where=id, shift=1)
            if not order_data: return alert(msg='没有找到这条订单', act=3)
            if order_data['oid'].startswith('ES'):
                order_data['attribute'] = json2dict(order_data['attribute'])
                order_data['pid'] = json2dict(order_data['pid'])
                order_data['number'] = json2dict(order_data['number'])
                sql = 'INSERT INTO `%scart` (`uid`, `accessid`, `productid`, `speci`, `quantity`, `validtime`, `addtime`) VALUES ' % \
                      self.db.cfg["prefix"]
                values = []
                for i in range(len(order_data['pid'])):
                    current = int(self.kg['run_start_time'][1])
                    value = '(%s, "%s", %s, "%s", %s, %s, %s)' % (
                        self.kg['user']['id'], self.kg['cookie']['KGCMS_ACCESS_ID'], order_data['pid'][i],
                        json2dict(order_data['attribute'][i]), order_data['number'][i], current + 86400 * 30 * 3,
                        current)
                    values.append(value)
                self.db.run_sql(sql + ','.join(values), log=True)
                url = '/user/order?action=cancel&id=%s' % id
                return alert(act=url)
            elif order_data['oid'].startswith('NR'):
                url = '/user/order?action=cancel&id=%s' % id
                return alert(act=url)
            else:
                url = '/user/order?action=cancel&id=%s' % id
                return alert(act=url)

        if post_param.get('action', '') == 'submit':
            # 获取数据
            address_id = numeric(post_param.get('address'))
            shipping_id = numeric(post_param.get('shippingid'))
            topay = numeric(post_param.get('topay', 0), 0, 1)
            insure = numeric(post_param.get('insure', 0), 0, 1)
            message = post_param.get('message', '')
            product_id_list = post_param.get('productid', [])
            speci_list = post_param.get('speci', [])
            quantity_list = post_param.get('quantity', [])
            payment = numeric(post_param.get('payment'), 1, 3)
            order_id = numeric(get_param.get('id'), 0)
            order_id_data = self.db.list(table='order', where='uid=%s && id=%s' % (self.kg['user']['id'], order_id),
                                         shift=1)

            if order_id_data.get('oid', '').startswith('NR'):
                pass
            else:
                # 参数校验
                if not address_id: return alert(msg='请选择收货地址', act=3)
                if not shipping_id: return alert(msg='请选择配送方式', act=3)
                if not product_id_list: return alert(msg='没有选择商品', act=3)
                if not speci_list: return alert(msg='商品规格出错', act=3)
                if not quantity_list: return alert(msg='商品数目出错', act=3)

                # 收货地址数据
                address = self.db.list(table='address',
                                       where='del=0 && uid=%s && id=%s' % (self.kg['user']['id'], address_id), shift=1)
                if not address: return alert(msg='收货地址错误', act=3)

                # 获取快递信息
                shipping = self.db.list(table='shipping',
                                        where='id=%s && enable=1 && webid=%s' % (shipping_id, self.kg['web']['id']),
                                        shift=1)
                if not address: return alert(msg='快递错误', act=3)

            if order_id:  # 编辑订单
                res = self.db.list(table='order', where='uid=%s && id=%s' % (self.kg['user']['id'], order_id), shift=1)
                if not res: return alert(msg="这条订单不存在", act=3)
                if res['status'] != 0: return alert(msg="只允许修改未付款的订单", act=3)
                edit_data = {
                    'address': address_id,
                    'message': message,
                    'payment': payment
                }
                msg = self.db.edit('order', edit_data, order_id)
                if msg in (0, 1):
                    url = '/api/unlimited_process?action=pay&code=%s'
                    return alert(act=url % cipher(json2dict({'order_number': res['oid']}, trans=False), 1, 1800))
                else:
                    return alert(msg='添加失败', act=3)

            # 创建订单
            for i in range(1, self.order_try):
                # 商品数据
                product_data_list = []
                products = self.db.list(
                    table='product',
                    where='id in (%s) && status=1 && recycle=0 && published=1 && audit=1' % ','.join(product_id_list),
                )
                prodcuts_dict = {}
                for product in products:
                    product['speci'] = json2dict(product['speci'])
                    product['inventory'] = json2dict(product['inventory'])
                    product['price'] = json2dict(product['price'])
                    prodcuts_dict[product['id']] = product
                really_product_id_list = []
                for i in range(len(product_id_list)):
                    # 没有数据则跳过
                    product_data = prodcuts_dict.get(int(product_id_list[i]))
                    if not product_data: continue
                    really_product_id_list.append(str(product_data['id']))
                    current_speci = eval(speci_list[i])
                    current_speci.sort()
                    for speci in product_data['speci']:
                        index = product_data['speci'].index(speci)
                        speci.sort()
                        if current_speci == speci:
                            product_row = {
                                "id": product_data['id'],
                                "title": product_data['title'],
                                "speci": product_data['speci'][index],
                                "price": product_data['price'][index],
                                "inventory": product_data['inventory'][index],
                                "quantity": int(quantity_list[i]),
                                "index": index
                            }
                            product_data_list.append(product_row)

                # 插入数据整合
                price, amount, attribute = ([], 0, [])
                for var in product_data_list:
                    if var['quantity'] > var['inventory']: return alert(msg="商品：%s，库存不足" % var['title'], act=3)
                    amount += var['price'] * var['quantity']
                    price.append(var['price'])
                    attribute.append(var['speci'])

                # 计算费用
                freight = 0 if topay else float(shipping['freight'])
                if insure: freight += shipping['insure'] * amount
                amount += freight

                # 数据插入
                data = {
                    'webid': self.kg['web']['id'],
                    'type': 0,
                    'oid': 'ES' + date(int(self.kg['run_start_time'][1]), '%Y%m%d%H%M%S') + str_random(3, 0, 1),
                    'uid': self.kg['user']['id'],
                    'pid': json2dict(list(map(int, really_product_id_list))),
                    'number': json2dict(list(map(int, quantity_list))),
                    'price': json2dict(price),
                    'amount': amount,
                    'attribute': json2dict(attribute),
                    'status': 0,
                    'dispatching': shipping_id,
                    'waybill': '',
                    'freight': freight,
                    'customer': topay,
                    'vouch': insure,
                    'address': address_id,
                    'payment': payment,
                    'message': message,
                    'reply': '',
                    'addtime': int(self.kg['run_start_time'][1])
                }
                # 判断支付方式
                if data['payment'] == 1:  # 账号余额支付
                    if self.kg['user']['money'] < amount:
                        return alert(msg='余额不足', act=3)
                fields = list(data.keys())
                values = list(data.values())
                for n in range(len(values)):
                    if isinstance(values[n], str):
                        values[n] = '"%s"' % values[n]
                    else:
                        values[n] = str(values[n])

                # 数据库操作
                order_sql = 'INSERT INTO `%sorder`(%s) VALUES (%s)' % (
                    self.db.cfg["prefix"], ','.join(fields), ','.join(values))
                self.db.run_sql('SAVEPOINT roll_point1', log=False)  # 设置回滚点,开启事务
                self.db.run_sql(order_sql, log=False)  # 订单数据插入
                # 避免幻读创建新的对象读取商品数据
                from kyger.db import MySQL
                current_product_list = MySQL().list(table='product', field="id, inventory",
                                                    where='id in (%s)' % ','.join(really_product_id_list))
                current_product_inventory_dict = {}
                for var in current_product_list:
                    current_product_inventory_dict[var['id']] = json2dict(var['inventory'])
                # 乐观锁
                try_flag = 0
                for var in product_data_list:
                    if var['inventory'] != current_product_inventory_dict[var['id']][var['index']]:
                        self.db.run_sql('ROLLBACK TO SAVEPOINT roll_point1', log=False)  # 回滚
                        try_flag = 1
                        break
                    else:
                        current_product_inventory_dict[var['id']][var['index']] = \
                            current_product_inventory_dict[var['id']][var['index']] - var['quantity']
                if try_flag: continue
                # 修改库存
                edit_inventory = 'UPDATE %sproduct SET inventory = CASE id ' % self.db.cfg["prefix"]
                for key in current_product_inventory_dict:
                    edit_inventory += 'WHEN %s THEN "%s" ' % (key, json2dict(current_product_inventory_dict[key]))

                self.db.run_sql(edit_inventory + 'END WHERE id IN (%s)' % ','.join(really_product_id_list),
                                log=False)  # 事务提交
                # 删除购物车记录
                carts = MySQL().list(table='cart', where='productid in (%s)' % ','.join(really_product_id_list))
                product_id_speci = {}
                data_pid = json2dict(data['pid'])
                data_attribute = json2dict(data['attribute'])
                for m in range(len(data_attribute)):
                    if data_pid[m] not in product_id_speci:
                        product_id_speci[data_pid[m]] = [data_attribute[m]]
                    else:
                        product_id_speci[data_pid[m]].append(data_attribute[m])
                carts_del_id = ['0']  # 删除的购物车ID
                for var in carts:
                    if json2dict(var['speci']) in product_id_speci[var['productid']]:
                        carts_del_id.append(str(var['id']))

                self.db.run_sql(
                    'DELETE FROM `%scart` WHERE id in (%s)' % (self.db.cfg["prefix"], ','.join(carts_del_id)),
                    log=True)  # 事务提交
                url = '/api/unlimited_process?action=pay&code=%s'
                return alert(act=url % cipher(json2dict({'order_number': data['oid']}, trans=False), 1, 1800))

        elif post_param.get('action', '') == 'order':
            # 登录判断
            if not self.kg['user'].get('id'): return alert(msg='请先登录', act='/user/login')
            # 购物车提交
            if post_param.get('cartid'):
                cartid = post_param.get('cartid')
                carts = self.db.list(
                    table='cart',
                    where='(uid=%s or accessid="%s") and id in (%s)' % (
                        self.kg['user']['id'], self.kg['cookie']['KGCMS_ACCESS_ID'], ','.join(cartid))
                )
                product_ids = []
                quantitys = []
                specis = []
                for cart in carts:
                    product_ids.append(str(cart['productid']))
                    quantitys.append(str(cart['quantity']))
                    specis.append(json2dict(cart['speci']))

            else:
                # 获取商品数据
                product_ids = post_param.get('product', [])
                quantitys = post_param.get('quantity', [])
                specis = post_param.get('speci', [])
                for i in range(len(specis)):
                    specis[i] = json2dict(specis[i])
                if not product_ids: return alert(msg="没有选择商品", act=3)
                if not quantitys: return alert(msg="数量出错", act=3)
                if not specis: return alert(msg="商品规格出错", act=3)

            # 获取商品数据
            products = self.db.list(
                table='product',
                where='id in (%s)' % ','.join(product_ids)
            )
            product_dict = {}
            for product in products:
                product['speci'] = json2dict(product['speci'])
                product['specipic'] = json2dict(product['specipic'])
                product['price'] = json2dict(product['price'])
                product['inventory'] = json2dict(product['inventory'])
                product_dict[product['id']] = product

            # 获取规格
            speci_list = json2dict(file="config/speci.json")
            speci_dict = {}
            for var in speci_list:
                speci_dict[var['id']] = var

            # 构建order数据
            order_data = {
                'oid': '暂无订单号',
                'pid': list(map(int, product_ids)),
                'number': list(map(int, quantitys)),
                'price': [],
                'amount': 0.00,
                'attribute': specis,
                'status': 0,
                'customer': 0,
                'vouch': 0,
                'payment': 1,
                'message': '',
                'reply': '',
                'addtime': '等待下单'
            }

            # 获取规格图,规格参数
            order_data['specipic'] = []
            order_data['title'] = []
            order_data['speci_param'] = []
            order_data['msg'] = []
            order_data['subtotal'] = []
            order_data['product_total'] = 0
            for i in range(len(order_data['pid'])):
                pid = order_data['pid'][i]
                attribute = order_data['attribute'][i]
                product_data = product_dict[pid]
                order_data['title'].append(product_data['title'])
                # 规格图
                index = product_data['speci'].index(attribute)
                order_data['specipic'].append(product_data['specipic'][index])
                # 规格参数
                params = []
                for var in attribute:
                    params.append([speci_dict[var[0]]['name'], speci_dict[var[0]]['param'][var[1]]])
                order_data['speci_param'].append(params)
                # 商品小计
                order_data['price'].append(product_data['price'][index])
                order_data['subtotal'].append(order_data['number'][i] * product_data['price'][index])
                order_data['product_total'] += order_data['number'][i] * product_data['price'][index]
                # 状态判断
                if product_data['published'] == 0 or product_data['audit'] == 0:
                    order_data['msg'].append("已失效")
                elif product_data['status'] == 0:
                    order_data['msg'].append("已下架")
                elif product_data['inventory'][index] < order_data['number'][i]:
                    order_data['msg'].append("库存不足(当前库存：%s)" % product_data['inventory'][index])
                else:
                    product_data['msg'] = ""
            order_data['status_msg'] = self.status[0]
            order_data['product_total'] = round(order_data['product_total'], 2)
            self.kg['order'] = order_data

            # 获取收货地址
            address = self.db.list(
                table='%saddress as a' % self.db.cfg["prefix"],
                where='del=0 && uid=%s' % self.kg['user']['id'],
                order='a.default=1 DESC, addtime DESC'
            )
            for var in address:
                var['select'] = 1 if var['default'] else 0
            self.kg['address'] = address

            # 获取快递
            shippings = self.db.list(table="shipping", where='enable=1 && webid=%s' % self.kg['web']['id'])
            for shipping in shippings:
                shipping['insure_price'] = '%.2f' % (float(shipping['insure']) * float(order_data['product_total']))
                shipping['select'] = 1 if shippings.index(shipping) == 0 else 0
            self.kg['shipping'] = shippings

        else:
            # 存在判断
            order_id = numeric(get_param.get('id', 0), 0)
            if not order_id: return notfound_404()
            order_data = self.db.list(table='order', where='uid=%s && id=%s' % (self.kg['user']['id'], order_id),
                                      shift=1)
            if not order_data: return alert(msg="订单不存在", act=3)
            self.kg['order_id'] = order_id

            self.kg['action'] = 'edit' if order_data['status'] == 0 else 'view'
            order_data['pid'] = json2dict(order_data['pid'])
            order_data['number'] = json2dict(order_data['number'])
            order_data['price'] = json2dict(order_data['price'])
            order_data['attribute'] = json2dict(order_data['attribute'])
            order_data['addtime'] = date(order_data['addtime'], '%Y-%m-%d %H:%M:%S')

            if order_data['oid'].startswith('ES'):
                # 获取商品数据
                products = self.db.list(
                    table='product',
                    where='id in (%s)' % ','.join('%s' % v for v in order_data['pid'])
                )
                product_dict = {}
                for product in products:
                    product['speci'] = json2dict(product['speci'])
                    product['specipic'] = json2dict(product['specipic'])
                    product['inventory'] = json2dict(product['inventory'])
                    product_dict[product['id']] = product

                # 获取规格
                speci_list = json2dict(file="config/speci.json")
                speci_dict = {}
                for var in speci_list:
                    speci_dict[var['id']] = var

                # 获取规格图,规格参数
                order_data['specipic'] = []
                order_data['title'] = []
                order_data['speci_param'] = []
                order_data['msg'] = []
                order_data['subtotal'] = []
                order_data['product_total'] = 0
                for i in range(len(order_data['pid'])):
                    pid = order_data['pid'][i]
                    attribute = order_data['attribute'][i]
                    try:
                        product_data = product_dict[pid]
                    except KeyError as e:
                        return alert("该商品已下架")
                    # product_data = product_dict[pid]
                    order_data['title'].append(product_data['title'])
                    # 规格图
                    index = product_data['speci'].index(attribute)
                    order_data['specipic'].append(product_data['specipic'][index])
                    # 规格参数
                    params = []
                    for var in attribute:
                        params.append([speci_dict[var[0]]['name'], speci_dict[var[0]]['param'][var[1]]])
                    order_data['speci_param'].append(params)
                    # 商品小计
                    order_data['subtotal'].append(order_data['number'][i] * order_data['price'][i])
                    order_data['product_total'] += order_data['number'][i] * order_data['price'][i]
                    # 状态判断
                    if product_data['published'] == 0 or product_data['audit'] == 0:
                        order_data['msg'].append("已失效")
                    elif product_data['status'] == 0:
                        order_data['msg'].append("已下架")
                    elif product_data['inventory'][index] < order_data['number'][i]:
                        order_data['msg'].append("库存不足(当前库存：%s)" % product_data['inventory'][index])
                    else:
                        product_data['msg'] = ""
                order_data['status_msg'] = self.status[order_data['status']]
            elif order_data['oid'].startswith('NR'):
                order_data['specipic'] = []
                order_data['title'] = ['在线充值']
                order_data['speci_param'] = []
                order_data['msg'] = ['']
                order_data['subtotal'] = [order_data['amount']]
                order_data['product_total'] = order_data['amount']
            self.kg['order'] = order_data

            # 获取收货地址
            address = self.db.list(
                table='%saddress as a' % self.db.cfg["prefix"],
                where='del=0 && uid=%s' % self.kg['user']['id'],
                order='a.default=1 DESC, addtime DESC'
            )
            for var in address:
                var['select'] = 1 if order_data['address'] == var['id'] else 0
            self.kg['address'] = address

            # 获取快递
            shippings = self.db.list(table="shipping", where='enable=1 && webid=%s' % self.kg['web']['id'])
            for shipping in shippings:
                shipping['insure_price'] = '%.2f' % (float(shipping['insure']) * float(order_data['product_total']))
                shipping['select'] = 1 if order_data['dispatching'] == shipping['id'] else 0
            self.kg['shipping'] = shippings

        return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
