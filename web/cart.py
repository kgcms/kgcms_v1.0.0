# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *



class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.common import permission
        from kyger.kgcms import template
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc
        misc = Misc(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']

        if post_param.get('action', '') == 'cart_edit':  # 购车修改
            id = numeric(self.kg['post'].get('id', 0), 0)
            quantity = numeric(self.kg['post'].get('quantity', 1), 1)
            if not all((id, quantity)): return json2dict({'status': 0, 'msg': "参数不全"}, trans=False)
            # 判断库存
            cart_data = self.db.list(
                table='cart',
                where='id=%s && (uid=%s or accessid="%s")' % (
                id, self.kg['user']['id'], self.kg['cookie']['KGCMS_ACCESS_ID']),
                shift=1
            )
            if not cart_data: return json2dict({'status': 0, 'msg': '该购物车记录不存在'})
            cart_data['speci'] = json2dict(cart_data['speci'])
            cart_data['speci'].sort()
            product_data = self.db.list(table='product', where=cart_data['productid'], shift=1)
            flag = 0
            inventory = 0
            for row in json2dict(product_data['speci']):
                index = json2dict(product_data['speci']).index(row)
                row.sort()
                inventory = json2dict(product_data['inventory'])[index]
                if row == cart_data['speci'] and json2dict(product_data['inventory'])[index] >= quantity:
                    flag = 1
                    break
            if flag == 0: return json2dict({'status': 0, 'msg': '存储不足', 'inventory': inventory}, trans=False)
            # 修改数据
            res = self.db.edit('cart', {'quantity': quantity}, 'id=%s' % id)
            if res in (0, 1):
                return json2dict({'status': 1}, trans=False)
            else:
                return json2dict({'status': 0, 'msg': "修改失败: %s" % res}, trans=False)

        elif post_param.get('action', '') == 'cart_del':  # 购车修改
            id = numeric(post_param.get('id', 0))
            res = self.db.dele('cart', 'id=%s && uid=%s' % (id, self.kg['session']['KGCMS_USER_ID']))
            if res:
                return json2dict({'status': 0}, trans=False)
            else:
                return json2dict({'status': 1, 'msg': '未找这条购物记录'}, trans=False)

        else:
            page = numeric(get_param.get('page', 1), 1)
            if self.kg['user'].get('id'):
                where = '(accessid="%s" or uid=%s)' % (self.kg['cookie']['KGCMS_ACCESS_ID'], self.kg['user']['id'])
            else:
                where = 'accessid="%s"' % self.kg['cookie']['KGCMS_ACCESS_ID']
            carts = self.db.list(
                table='%scart as a, %sproduct as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                field='a.*, b.title, b.inventory, b.price, b.specipic, b.speci as specis',
                where=where + '&& a.productid = b.id',
                page=page,
                limit=10
            )
            if page > self.db.total_page:
                page = self.db.total_page
                carts = self.db.list(
                    table='%scart as a, %sproduct as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                    field='a.*, b.title, b.inventory, b.price, b.specipic, b.speci as specis',
                    where=where + '&& a.productid = b.id',
                    page=page,
                    limit=10
                )
            # 分页
            if self.db.total_page < 2:
                self.kg['page_html'] = ''
            else:
                from kyger.common import page_tpl
                page_html = page_tpl(page, self.db.total_page, 10, self.kg['server']['WEB_URL'])
                self.kg['page_html'] = page_html
            # 获取规格
            speci_list = json2dict(file="config/speci.json")
            speci_dict = {}
            for var in speci_list:
                speci_dict[var['id']] = var
            # 数据整形
            for cart in carts:
                cart['speci'] = json2dict(cart['speci'])
                cart['inventory'] = json2dict(cart['inventory'])
                cart['price'] = json2dict(cart['price'])
                cart['specipic'] = json2dict(cart['specipic'])
                cart['specis'] = json2dict(cart['specis'])
                # 规格整形
                cart['speci_param'] = []
                for var in cart['speci']:
                    cart['speci_param'].append([speci_dict[var[0]]['name'], speci_dict[var[0]]['param'][var[1]]])

                # 库存、规格图、单价
                index = cart['specis'].index(cart['speci'])
                cart['inventory'] = cart['inventory'][index]
                cart['price'] = cart['price'][index]
                cart['specipic'] = cart['specipic'][index]

                # 小计
                cart['subtotal'] = cart['quantity'] * float(cart['price'])
            self.kg['carts'] = carts

            # 栏目数据
            data = self.db.list(
                table='category',
                where='module="%s" && level=1' % 'product',
                shift=1,
                order='id ASC'
            )
            data['upper'] = json2dict(data['upper'])
            # 获取上级频道id和名称
            if data['upper']:
                up_cate = self.db.list(
                    table='category',
                    field='id,title',
                    where=data['upper'][-1],
                    shift=1
                )
                up_data = (up_cate['title'], up_cate['id']) if up_cate else ('', 0)
                data['up_name'], data['up_id'] = up_data
            else:
                data['up_name'], data['up_id'] = ('', 0)
            self.kg['category'] = data

            return template(
                function=[
                    {"category": Category(self.db, self.kg).list},
                    {"article_list": Article(self.db, self.kg).list},
                    {"article_single": Article(self.db, self.kg).single},
                    {"article_page": Article(self.db, self.kg).list_page},
                    {"product_page": Product(self.db, self.kg).list_page},
                    {"product_single": Product(self.db, self.kg).single},
                    {"ad_list": Advertise(self.db, self.kg).list},
                    {"navigate_list": misc.navigate},
                    {"app": misc.app},
                    {"get_cart": Product(self.db, self.kg).get_cart},
                ]
            )
