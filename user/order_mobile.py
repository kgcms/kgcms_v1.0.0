# -*- coding:utf-8 -*-
"""订单管理"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
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
        get_param = self.kg['get']
        action = get_param.get('action')

        # 检查过期所有订单，取消并退还库存
        order_list = self.db.list(
            table='order',
            where='status=0 && addtime<%s' % (int(self.kg['run_start_time'][1]) - 7000)
        )
        for order in order_list:
            if order['oid'].startswith('ES'):
                # 数据
                order['pid'] = json2dict(order['pid'])
                order['number'] = json2dict(order['number'])
                order['attribute'] = json2dict(order['attribute'])
                skus = {}
                for i in range(len(order['attribute'])):
                    if order['pid'][i] not in skus:
                        skus[order['pid'][i]] = [
                            {"speci": order['attribute'][i], "number": order['number'][i]}]
                    else:
                        skus[order['pid'][i]].append(
                            {"speci": order['attribute'][i], "number": order['number'][i]})
                products = self.db.list(
                    table='product',
                    where='id in (%s)' % ','.join('%s' % v for v in order['pid'])
                )
                for product in products:
                    product['inventory'] = json2dict(product['inventory'])
                    product['speci'] = json2dict(product['speci'])
                    edit_datas = skus[product['id']]
                    for row in edit_datas:
                        index = product['speci'].index(row['speci'])
                        product['inventory'][index] += row['number']
                # 事务
                self.db.run_sql('UPDATE `%sorder` SET status=-4 WHERE id=%s' % (self.db.cfg["prefix"], order['id']),
                                log=False)
                # 退还库存
                sql = 'UPDATE %sproduct SET inventory = CASE id ' % self.db.cfg["prefix"]
                for product in products:
                    sql += 'WHEN %s THEN "%s" ' % (product['id'], json2dict(product['inventory']))
                sql += 'END WHERE id IN (%s)' % ','.join('%s' % v for v in order['pid'])
                self.db.run_sql(sql, log=True)
            elif order['oid'].startswith('NR'):
                self.db.edit('order', {'status': -4}, order['id'])
            else:
                pass

        if action in ('del', 'pay', 'cancel'):
            id = numeric(get_param.get('id'), 0)
            if not id: return alert(msg='参数错误', act=3)
            order_data = self.db.list(table='order', where=id, shift=1)
            if not order_data: return alert(msg='没有找到该订单记录', act=3)
            if action == 'del':
                if order_data['status'] not in (4, -4):
                    return alert(msg='订单未被取消或完成，不可删除', act=3)
                else:
                    self.db.dele('order', where=id)
                    return alert(act=2)
            elif action == 'pay':
                if order_data['status'] != 0: return alert(msg='只允许对未付款的订单进行支付', act=3)
                url = '/api/unlimited_process?action=pay&code=%s' % cipher(
                    json2dict({'order_number': order_data['oid']}, trans=False), 1)
                return alert(act=url)
            else:
                if order_data['status'] != 0:
                    return alert(msg='只允许取消未付款的订单', act=3)
                else:
                    if order_data['oid'].startswith('ES'):
                        # 数据
                        order_data['pid'] = json2dict(order_data['pid'])
                        order_data['number'] = json2dict(order_data['number'])
                        order_data['attribute'] = json2dict(order_data['attribute'])
                        skus = {}
                        for i in range(len(order_data['attribute'])):
                            if order_data['pid'][i] not in skus:
                                skus[order_data['pid'][i]] = [
                                    {"speci": order_data['attribute'][i], "number": order_data['number'][i]}]
                            else:
                                skus[order_data['pid'][i]].append(
                                    {"speci": order_data['attribute'][i], "number": order_data['number'][i]})
                        products = self.db.list(
                            table='product',
                            where='id in (%s)' % ','.join('%s' % v for v in order_data['pid'])
                        )
                        for product in products:
                            product['inventory'] = json2dict(product['inventory'])
                            product['speci'] = json2dict(product['speci'])
                            edit_datas = skus[product['id']]
                            for row in edit_datas:
                                index = product['speci'].index(row['speci'])
                                product['inventory'][index] += row['number']
                        # 事务
                        self.db.run_sql('UPDATE `%sorder` SET status=-4 WHERE id=%s' % (self.db.cfg["prefix"], id),
                                        log=False)
                        # 退还库存
                        sql = 'UPDATE %sproduct SET inventory = CASE id ' % self.db.cfg["prefix"]
                        for product in products:
                            sql += 'WHEN %s THEN "%s" ' % (product['id'], json2dict(product['inventory']))
                        sql += 'END WHERE id IN (%s)' % ','.join('%s' % v for v in order_data['pid'])
                        self.db.run_sql(sql, log=True)
                    elif order_data['oid'].startswith('NR'):
                        self.db.edit('order', {'status': -4}, id)
                    return alert(act='/user/order')

        elif self.kg['post'].get('action') == 'get_status':
            oid = self.kg['post'].get('oid')
            if not oid: return json2dict({'status': -1, 'msg': '订单号不能为空'}, trans=False)
            order_data = self.db.list(
                table='order',
                field='status',
                where='uid=%s && oid="%s"' % (self.kg['user']['id'], oid),
                shift=1
            )
            if not order_data: return json2dict({'status': -1, 'msg': '订单记录不存在'}, trans=False)
            if order_data['status'] in (1, 4):
                return json2dict({'status': 0, 'msg': '已支付'}, trans=False)
            else:
                return json2dict({'status': 1, 'msg': '暂未支付'}, trans=False)

        else:
            page = numeric(self.kg['get'].get('page', 1))
            order = self.db.list(
                table='order',
                field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                where='uid=%s' % self.kg['user']['id'],
                order='id DESC',
                page=page,
                limit=10
            )
            if page > self.db.total_page:
                page = self.db.total_page
                order = self.db.list(
                    table='order',
                    field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
                    where='uid=%s' % self.kg['user']['id'],
                    order='id DESC',
                    page=page,
                    limit=10
                )
            # 分页
            if self.db.total_page < 2:
                self.kg['page_html'] = ''
            else:
                from kyger.common import page_tpl
                page_html = page_tpl(page, self.db.total_page, 10, self.kg['server']['WEB_URL'], page_num=3)
                self.kg['page_html'] = page_html
            # 整形
            for row in order:
                row['status_title'] = self.status[row['status']]
            self.kg['order'] = order

            return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
