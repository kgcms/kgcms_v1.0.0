# -*- coding:utf-8 -*-
"""网站商品"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'model': [50, "商品型号长度不允许超过50个字符"],
            'units': [20, "计量单位长度不允许超过50个字符"],
            'brand': [50, "品牌长度不允许超过50个字符"],
            'coding': [50, "商品编码长度不允许超过50个字符"],
            'template': [50, "自定义模板长度不允许超过50个字符"],
            'publisher': [20, "发布者长度不允许超过20个字符"]
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, str_random, json2dict, alert, mk_time, html_escape, file_list, str_replace, \
            date, url_absolute, file_mime_type, exists, file_extension

        # 1.数据获取
        get_param = self.kg['get']  # get参数
        post_param = self.kg['post']  # post参数

        # 2.动作判断
        product_id = numeric(get_param.get('id', 0), 0)  # 获取编辑的商品id
        action = 'edit' if product_id else 'add'

        # 3.提交判断
        if post_param.get('action', '') == 'submit':
            # 栏目
            cid = numeric(post_param.get('category'))
            if not cid: return alert(msg="没有选择栏目", act=3)
            if not html_escape(post_param.get('title', '')): return alert(msg="标题不能为空", act=3)
            category_data = self.db.list(table='category', field='upper', where=cid, shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            category_data['upper'].append(cid)
            # 评论、推荐、出版、审核、状态、虚拟货物
            res_list = []
            for row in ['comment', 'recom', 'published', 'audit', 'status', 'virtual']:
                if row in post_param:
                    res_list.append(1)
                else:
                    res_list.append(0)
            # 时间
            pushtime = mk_time(post_param.get('period_time'), "%Y-%m-%d %H:%M")
            if pushtime == 0: pushtime = int(self.kg['run_start_time'][1])

            # 规格、价格、库存
            speci_type = json2dict(file="config/speci.json")
            speci_list = []
            for var in speci_type:
                key = 'speci_%s' % var['id']
                speci_list.append([var['id'], post_param.get(key, [])])
            price = post_param.get('price', [])
            inventory = post_param.get('inventory', [])
            speci_data = []
            for i in range(len(price)):
                price[i] = numeric(price[i])
                inventory[i] = numeric(inventory[i])
                res = []
                for row in speci_list:
                    if row[1][i] == 'null': return alert(msg='请选择规格', act=3)
                    res.append([row[0], numeric(row[1][i])])
                speci_data.append(res)
            # 权限
            authority = post_param.get('authority', [])
            for i in range(len(authority)):
                authority[i] = numeric(authority[i])

            data = {
                "category": json2dict(category_data['upper']),
                'title': html_escape(post_param.get('title', '')),
                'tag': html_escape(post_param.get('tag', '')),
                'sort': numeric(post_param.get('sort', 0), 0),
                "virtual": res_list[5],
                "authority": json2dict(authority),
                "specipic": json2dict(post_param.get('specipic', [])),
                "model": html_escape(post_param.get('model', '')),
                "market": html_escape(post_param.get('market', '')),
                "price": json2dict(price),
                "units": html_escape(post_param.get('units', '')),
                "inventory": json2dict(inventory),
                "keyword": html_escape(post_param.get('keyword', '')),
                "introduction": html_escape(post_param.get('introduction', '')),
                "sales": numeric(post_param.get('sales', 0), 0),
                "brand": html_escape(post_param.get('brand', '')),
                "coding": html_escape(post_param.get('coding', '')),
                "speci": json2dict(speci_data),
                "template": html_escape(post_param.get('template', '')),
                "comment": res_list[0],
                "agree": numeric(post_param.get('agree', 0), 0),
                "recom": res_list[1],
                "published": res_list[2],
                "audit": res_list[3],
                "status": res_list[4],
                'picture': post_param.get('picture', []),
                'thumbnail': html_escape(post_param.get('thumbnail', '')),
                "commenttotal": numeric(post_param.get('commenttotal', 0), 0),
                "favorite": numeric(post_param.get('favorite', 0), 0),
                "click": numeric(post_param.get('click', 0), 0),
                "publisher": html_escape(post_param.get('publisher', '')),
                "pushtime": pushtime,
                'content': post_param.get('KgcmsEditor', ''),
                "description": html_escape(post_param.get('description', '')),
                "filename": html_escape(post_param.get('filename', '')),
                'recycle': 0,
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            # 图片
            picture = post_param.get('picture', '')
            if picture:
                picture = [picture] if isinstance(picture, str) else picture
                while '' in picture:
                    picture.remove('')
                data['picture'] = picture

            if action == 'add':  # 添加商品
                data['picture'] = json2dict(data['picture'])
                data['webid'] = numeric(self.kg['web']['id'], 0)
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('product', data)
                if msg:
                    return alert(msg="添加成功", act='product_manage')
                else:
                    return alert(msg="添加失败", act=3)
            else:  # 编辑商品
                # 修改文件名
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='product', where=product_id, shift=1)['picture'])
                # 删除被删掉的图
                for var in source_pic:
                    if var not in data['picture']:
                        if exists(url_absolute(var), type='file'):
                            os.remove(url_absolute(var))  # 删除文件
                # 修改图名
                for i in range(len(data['picture'])):
                    cur_path = url_absolute(data['picture'][i])  # 当前路径(绝对)
                    path_list = data['picture'][i].split('/')
                    path_list[-1] = 'product_%s_%s%s' % (product_id, i, file_extension(data['picture'][i]))
                    re_path = '/'.join(path_list)  # 修改路径(相对)
                    # 修改文件命名
                    if exists(cur_path, type='file') and data['picture'][i] != re_path:
                        os.rename(cur_path, url_absolute(re_path))
                    # 替换文件路径
                    data['picture'][i] = re_path

                data['picture'] = json2dict(data['picture'])
                row = self.db.edit('product', data, where=product_id)
                if row:
                    return alert(msg="编辑成功", act='product_manage')
                else:
                    return alert(msg="编辑失败", act=3)
        # 非提交
        else:
            # 商品数据
            if action == "edit":
                from kyger.product import Product
                product_data = Product(self.db, self.kg).single(product_id, date='%Y-%m-%d %H:%M')
                if not product_data: return alert(msg="该商品不存在", act=3)
                product_data['content'] = html_escape(product_data['content'], False)
            else:
                product_data = {}

            # 商品数据整形
            data = {
                "id": product_data.get("id", 0),
                "category_title": product_data.get("category_title", ''),
                "title": product_data.get("title", ''),
                "tag": product_data.get("tag", ''),
                "sort": product_data.get("sort", ''),
                "virtual": product_data.get("virtual", 0),
                "model": product_data.get("model", ''),
                "market": product_data.get("market", '0.00'),
                "price": product_data.get("price", []),
                "units": product_data.get("units", ''),
                "inventory": product_data.get("inventory", []),
                "keyword": product_data.get("keyword", ''),
                "introduction": product_data.get("introduction", ''),
                "sales": product_data.get("sales", ''),
                "picture": product_data.get("picture", []),
                "brand": product_data.get("brand", ''),
                "coding": product_data.get("coding", ''),
                "speci": product_data.get("speci", []),
                "specipic": product_data.get("specipic", []),
                "template": product_data.get("template", ''),
                "comment": product_data.get("comment", 1),
                "agree": product_data.get("agree", ''),
                "recom": product_data.get("recom", 1),
                "published": product_data.get("published", 1),
                'authority': product_data.get('authority', []),
                "audit": product_data.get("audit", 1),
                "status": product_data.get("status", 1),
                "commenttotal": product_data.get("commenttotal", ''),
                "favorite": product_data.get("favorite", ''),
                "click": product_data.get("click", ''),
                "publisher": product_data.get("publisher", ''),
                "pushtime": product_data.get("pushtime", date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                "content": product_data.get("content", ''),
                "description": product_data.get("description", ''),
                "filename": product_data.get("filename", ''),
                "thumbnail": product_data.get("thumbnail", '')
            }
            # 获取栏目列表
            from kyger.category import Category
            category_list = Category(self.db, self.kg).rank(cid="product")
            category_list.insert(0, {"id": 0, "title": "请选择栏目", "level": 1})

            # 获取规格
            speci_list = json2dict(file='config/speci.json')
            # 获取用户等级
            rank = self.db.list(table='rank', where='webid=%s && enable=1' % self.kg['web']['id'])
            return template(assign={
                'data': data,
                'category': category_list,
                'action': action,
                'speci': speci_list,
                'rank': rank
            })

