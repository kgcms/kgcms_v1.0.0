# -*- coding:utf-8 -*-
"""产品首页"""

from kyger.utility import *


class KgcmsApi(object):
    """产品模块首页处理类"""
 
    def __init__(self):
        """
        初始化数据
        """
        pass
    
    def __call__(self):
        from kyger.common import permission
        from kyger.kgcms import template
        from kyger.utility import numeric
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc

        self.kg["get"]["id"] = numeric(self.kg["get"].get("id", 0))
        self.kg["get"]["cid"] = numeric(self.kg["get"].get("cid", 0))

        misc = Misc(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 权限检测
        res = permission(self.db, self.kg)
        if res['status'] == 1:
            # 登录状态
            if self.kg['user']['id'] != 0:
                return alert(msg='没有相关权限', act=3)
            else:
                return alert(act="%s/user/login" % self.kg['server']['HTTP_HOST'])
            # return alert(msg='没有访问权限', act=3)
        elif res['status'] == 404:
            return notfound_404()
        else:
            data = res['data']
            

        # 评论开关
        from kyger.parser_ini import Config
        config = Config('config/settings.ini').get('user')
        self.kg['comment_enabled'] = 0
        if data.get('comment') == 1 and 'product' in json2dict(config['comment_enabled']): self.kg['comment_enabled'] = 1

        # 获取参数
        cid = numeric(get_param.get('cid', 0), 0)  # 频道ID
        id = numeric(get_param.get('id', 0), 0)  # 内容ID

        # 动作请求
        if post_param.get('action', '') == 'cart':  # 加入购物车
            # 获取参数
            product_id = numeric(post_param.get('productid', 0), 0)
            quantity = numeric(post_param.get('quantity', 0), 0)
            speci = json2dict(post_param.get('speci'))
            speci.sort()
            # 数据检查
            if not all((product_id, speci, quantity)):return json2dict({'status': 0, 'msg': '参数不全'}, trans=False)
            user_id = self.kg['session'].get('KGCMS_USER_ID', 0)
            product = self.db.list(table='product', where=product_id, shift=1)
            if not product: return json2dict({'status': 0, 'msg': '商品不存在'})
            available = 0
            inventory = 0
            product['speci'] = json2dict(product['speci'])
            product['inventory'] = json2dict(product['inventory'])
            for row in product['speci']:
                index = product['speci'].index(row)
                row.sort()
                if row == speci and product['inventory'][index] >= quantity:
                    inventory = product['inventory'][index]
                    available = 1
            if not available: return json2dict({'status': 0, 'msg': '该商品库存不足或者规格参数不存在'}, trans=False)
            # 是否已有该规格的商品
            res = self.db.list( table='cart', where='uid=%s && productid=%s' % (user_id, product_id))
            same = {}
            for row in res:
                row['speci'] = json2dict(row['speci'])
                row['speci'].sort()
                if speci == row['speci']:
                    same = row
            # 删除过期的购物车商品
            self.db.dele('cart', 'validtime < %s' % int(self.kg['run_start_time'][1]))
            # 插入或修改数据库
            cart = Product(self.db, self.kg)
            cart_quantity = cart.get_cart(1)
            cart_type = cart.get_cart()
            if same:
                if same['quantity'] + quantity > inventory:
                    if same['quantity'] > 0: r_data = {"status": 0, "msg": "库存不足,购物车已有该商品数量:%s" % same['quantity']}
                    else: r_data = {"status": 0, "msg": "库存不足"}
                    return json2dict(r_data, trans=False)
                msg = self.db.edit('cart', {'quantity': same['quantity'] + quantity}, same['id'])
                if msg:
                    return json2dict({"status": 1, "msg": "添加成功", "quantity": cart_quantity + quantity, "type": cart_type}, trans=False)
                else:
                    return json2dict({"status": 0, "msg": "添加失败"}, trans=False)
            else:
                # 数据插入
                data = {
                    "uid": user_id,
                    "accessid": self.kg['cookie']['KGCMS_ACCESS_ID'],
                    "productid": product_id,
                    "speci": json2dict(speci),
                    "quantity": quantity,
                    "validtime": int(self.kg['run_start_time'][1]) + 86400 * 30 * 3,
                    "addtime": int(self.kg['run_start_time'][1]),
                }
                res = self.db.add('cart', data)
                if res:
                    return json2dict({'status': 1, 'msg': '添加成功', "quantity": cart_quantity + quantity, "type": cart_type + 1}, trans=False)
                else:
                    return json2dict({'status': 0, 'msg': '添加失败'}, trans=False)

        # 商品内容页
        if id:
            # 浏览次数加一
            click = data['click'] + 1
            self.db.edit(table='product', data={'click': click}, where='id=%s' % id, log=False)

            # 数据
            self.kg['product'] = data
            category_data = self.db.list(table='category', where=data['category'][-1], shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            self.kg['category'] = category_data

            # 规格
            speci_list = json2dict(file="config/speci.json")
            speci_dict = {}
            for var in speci_list:
                speci_dict[var['id']] = var
            self.kg['speci'] = speci_dict
            tpl = "product_view.tpl"

        # 商品列表页
        else:
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

            # url参数合成
            self.kg['sort_url'] = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param), deld='sort') else ''
            sort = numeric(get_param.get('sort', 0), 0, 4)
            sort_list = [0, 10, 4, 6, 7]
            self.kg['sort'] = [sort, sort_list[sort]]
            # 自定义模板判断
            if data['template']:
                tpl = data['template']
            else:
               tpl = "product_list.tpl"
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
            ],
            tpl=tpl
        )

