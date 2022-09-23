# -*- coding:utf-8 -*-
"""栏目添加页"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {}
        # 必填检测
        self.must_input = {
            'module': '所属模块',
            'title': '栏目标题'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import alert, numeric, json2dict, html_escape
        from kyger.category import Category
        from kyger.upload import Upload

        # 1.获取数据
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 2.动作判断
        cid = numeric(get_param.get('cid', 0), 0)
        action = 'edit' if cid else 'add'

        # 3.提交判断
        if post_param.get("action") == "submit":
            cate_id = numeric(post_param.get('category', 0), 0)
            if cate_id:  # 作为cid的下级栏目
                up_cate = self.db.list(table='category', field='level,upper,id,module', where=cate_id, shift=1)
                if up_cate['module'] != post_param.get('module', ''): return alert(msg='模块选择错误', act=3)
                level = up_cate['level'] + 1  # 栏目等级在父级的基础上加1
                upper = json2dict(up_cate['upper'])  # 上级栏目在父级的基础上加上父级id
                upper.append(up_cate['id'])
            else:  # 作为一级栏目
                level = 1
                upper = []

            # 图片获取和保存
            cate_picture = post_param['image']
            image = ''
            if cate_picture[0]: image = cate_picture[0]
            if cate_picture[1]: image = cate_picture[1]

            # 数据组织
            enable = 1 if post_param.get('enable', '') else 0
            permission = post_param.get('permission', [])
            for i in range(len(permission)):
                permission[i] = numeric(permission[i])
            add_data = {
                'title': html_escape(post_param.get('title', '')),
                'module': post_param.get('module', ''),
                'level': level,
                'upper': json2dict(upper),
                'seotitle': html_escape(post_param.get('seotitle', '')),
                'seokey': html_escape(post_param.get('seokey', '')),
                'seodescr': html_escape(post_param.get('seodescr', '')),
                'introduction': html_escape(post_param.get('Introduction', '')),
                'sort': numeric(post_param.get('sort', 0)),
                'enable': enable,
                'template': html_escape(post_param.get('template', '')),
                'permission': json2dict(permission)
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(add_data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(add_data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)

            if image:  # 如果有值就存储
                up = Upload(image, self.db, self.kg, base64=True)
                up.path = 0  # 设置不创建路径
                up.filename = 'logo_{y}{mm}{dd}{hh}{ii}{ss}'  # 设置文件名形式
                msg = up.image('category')  # 保存文件
                add_data['picture'] = msg['url']

            url = 'category_manage?cid=%s' % cate_id if cate_id else 'category_manage'
            if action == 'add':
                add_data['webid'] = numeric(self.kg['web']['id'], 0)
                add_data['addtime'] = int(self.kg['run_start_time'][1])
                if not image: add_data['picture'] = ''
                msg = self.db.add('category', add_data)
                if msg: return alert(act=url)
                else: return alert(msg='添加失败', act=3)
            else:
                # 获取子栏目
                data = self.db.list(
                    table='category',
                    field='id,title,level,picture,module',
                    where="`upper` rlike '[\[|, ]%d\]'" % cid,
                    order='`level` ASC'
                )
                # 获取所属栏目的文章
                article = self.db.list(table='article', field='category',where="`category` rlike '[\[|, ]%d[\]|,]'" % cid)  # 获取文章表的数据
                # 获取自己的信息
                cate = self.db.list(table='category', field='upper', where=cid, shift=1)
                # 判断是否移动栏目
                if cate['upper'] == add_data['upper']:
                    msg = self.db.edit('category', add_data, numeric(get_param['cid']))
                    if msg: return alert(act=url)
                    else: return alert(msg='修改失败', act=3)
                else:
                    if not data and not article:
                        msg = self.db.edit('category', add_data, numeric(get_param['cid']))
                        if msg: return alert(act=url)
                        else: return alert(msg='修改失败', act=3)
                    else: return alert(msg="该栏目存在下级栏目或文章无法移动", act=3)
        # 非提交数据
        else:
            # 栏目列表
            article = Category(self.db, self.kg).rank('article')
            product = Category(self.db, self.kg).rank('product')
            photo = Category(self.db, self.kg).rank('photo')
            download = Category(self.db, self.kg).rank('download')
            research = Category(self.db, self.kg).rank('research')
            vote = Category(self.db, self.kg).rank('vote')
            for row in [article, product, photo, download, research, vote]:
                row.insert(0, {'title': '作为一级栏目', 'id': 0, 'level': 1})

            # cid的栏目数据
            if action == "edit":
                category_data = self.db.list(
                    table='category',
                    where=cid,
                    shift=1
                )
                if not category_data: return alert(msg="该栏目不存在", act=3)
                category_data['upper'] = json2dict(category_data['upper'])
                add_cate = {}
            else:
                category_data = {}
                add_id = numeric(get_param.get('add', 0), 0)
                if add_id:
                    add_cate = self.db.list(table='category', field='id, module', where=add_id, shift=1)
                else: add_cate = {}

            data = {
                'title': category_data.get('title', ''),
                'upper': category_data.get('upper', []),
                'level':  category_data.get('level', 0),
                'picture':  category_data.get('picture', self.kg['tpl_url'] + 'images/a8.png'),
                'seotitle': category_data.get('seotitle', ''),
                'seokey': category_data.get('seokey', ''),
                'seodescr': category_data.get('seodescr', ''),
                'introduction': category_data.get('introduction', ''),
                'sort': category_data.get('sort', 20),
                'module': category_data.get('module', ''),
                'enable': category_data.get('enable', 1),
                'template': category_data.get('template', ''),
                'permission': json2dict(category_data.get('permission', '[]')),
            }
            rank = self.db.list(table='rank', where='webid=%s && enable=1' % self.kg['web']['id'])
            return template(assign={
                'data': data,
                'category': {'article': article, 'product': product, 'photo': photo, 'download': download, 'research': research, 'vote': vote},
                'action': action,
                'add': add_cate,
                'rank': rank
            })
