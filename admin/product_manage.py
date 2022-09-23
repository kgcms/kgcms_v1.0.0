# -*- coding:utf-8 -*-
"""网站商品"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.product import Product
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, url_query2dict, url_update, str_replace
        product = Product(self.db, self.kg)
        post_param = self.kg['post']
        get_param = self.kg['get']

        # 判断是否执行动作
        if get_param.get('action', ''):
            action = get_param.get('action', '')
            if 'id' not in get_param: return alert(act=3)
            id_list = get_param['id'] if isinstance(get_param['id'], list) else [get_param['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
            # 移除action和id参数
            del get_param['action']
            del get_param['id']
        elif post_param.get('action', ''):
            action = post_param.get('action', '')
            if 'id' not in post_param: return alert(act=3)
            id_list = post_param['id'] if isinstance(post_param['id'], list) else [post_param['id']]  # 将单条转列表
            id_sql = ','.join(id_list)
        else: action = ''
        if action in ['recom', 'unrecom', 'published', 'unpublished', 'audit', 'unaudit', 'del', 'del_true',
                      'recovery', 'sale', 'unsale'] and id_sql:
            if action == 'recom': self.db.edit('product', {'recom': 1}, where='id in (%s)' % id_sql)  # 推荐
            if action == 'unrecom': self.db.edit('product', {'recom': 0}, where='id in (%s)' % id_sql)  # 不推荐
            if action == 'published': self.db.edit('product', {'published': 1}, where='id in (%s)' % id_sql)  # 出版
            if action == 'unpublished': self.db.edit('product', {'published': 0}, where='id in (%s)' % id_sql)  # 草稿
            if action == 'audit': self.db.edit('product', {'audit': 1}, where='id in (%s)' % id_sql)  # 审核
            if action == 'unaudit': self.db.edit('product', {'audit': 0}, where='id in (%s)' % id_sql)  # 未审核
            if action == 'sale': self.db.edit('product', {'status': 1}, where='id in (%s)' % id_sql)  # 上架销售
            if action == 'unsale': self.db.edit('product', {'status': 0}, where='id in (%s)' % id_sql)  # 下架
            if action == 'del': self.db.edit('product', {'recycle': 1}, where='id in (%s)' % id_sql)  # 删除
            if action == 'recovery': self.db.edit('product', {'recycle': 0}, where='id in (%s)' % id_sql)  # 还原
            if action == 'del_true': self.db.dele('product', where='id in (%s)' % id_sql)  # 彻底删除
            url = '?' + url_query2dict(get_param) if url_query2dict(get_param) else ''
            if action == 'del':
                return alert(act='product_manage')
            else:
                return alert(act='product_manage%s' % url)

        # 不符合上面条件则调用数据
        filter_id = numeric(get_param.get('filter', 0), 0, 8)  # 数据筛选的序号
        recycle = numeric(get_param.get('trash', 0), 0, 1)  # 回收站
        # 数据筛选参数
        filter_list = [0, 0, 0, 0, 0, 0]  # 推荐 发布 审核 评论 销售 虚拟
        if filter_id:
            filter_id = filter_id - 1 if filter_id > 0 else 0
            filter_list[filter_id // 2] = (filter_id % 2) + 1
        # 调用商品数据
        data = product.list_page(
            sort=numeric(get_param.get('sort', 0)),  # 排序
            row=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10)),  # 调用条数
            recom=filter_list[0],  # 推荐
            category=numeric(get_param.get('cid', 0)),  # 栏目
            start=0,  # 分页不设置开始
            sale=filter_list[4],
            virtual=filter_list[5],
            webid=numeric(get_param.get('webid', 0)),  # webid
            picture=0,  # 是否调用图片记录
            word=get_param.get('word', ''),  # 搜索关键字
            published=filter_list[1],  # 出版
            audit=filter_list[2],  # 审核
            recycle=recycle + 1,  # 回收
            comment=filter_list[3],  # 评论
            date='%Y-%m-%d'  # 日期格式
        )
        # 栏目数据
        from kyger.category import Category
        column = Category(self.db, self.kg)
        category_data = column.rank(cid="product")  # 获取栏目结构
        category_data.insert(0, {"title": "所有栏目", "id": 0, "level": 0})

        # url参数合成
        button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
        sort_url = url_update(url_query2dict(get_param), deld=['sort', 'page'])
        sort_url = sort_url + '&' if sort_url else ''
        filter_url = url_update(url_query2dict(get_param), deld=['filter', 'page'])
        filter_url = filter_url + '&' if filter_url else ''
        category_url = url_update(url_query2dict(get_param), deld=['cid', 'page'])
        category_url = category_url + '&' if category_url else ''
        url = {
            'button': button_url,
            'sort': sort_url,
            'filter': filter_url,
            'category': category_url
        }
        return template(
            assign={
                'data': data['list'],
                'branch': data['page_html'],
                'sort': numeric(get_param.get('sort', 0)),
                'filter': numeric(get_param.get('filter', 0), 0, 14),
                'category': category_data,
                'cid': numeric(get_param.get('cid', 0)),
                'word': str_replace(get_param.get('word', ''), ['"'], ['&quot;']),
                'url': url,
                'trash': recycle,
                'page_data': data['page_data']
            }
        )
