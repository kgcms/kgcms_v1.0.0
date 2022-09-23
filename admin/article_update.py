# -*- coding:utf-8 -*-
"""文章添加"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'author': [50, "文章作者长度不允许超过50个字符"],
            'source': [50, "来源长度不允许超过50个字符"],
            'sourceurl': [50, "来源网址长度不允许超过50个字符"],
            'template': [50, "自定义模板长度不允许超过50个字符"],
            'publisher': [20, "发布者长度不允许超过20个字符"]
        }
        # 必填检测
        self.must_input = {
            'category': '所属栏目',
            'title': '文章标题'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, json2dict, alert, mk_time, html_escape, file_list, date, url_absolute, file_extension, exists

        # 1.数据获取
        get_param = self.kg['get']  # get参数
        post_param = self.kg['post']  # post参数

        # 2.动作判断
        article_id = numeric(get_param.get('id', 0), 0)  # 获取编辑的文章id
        action = 'edit' if article_id else 'add'

        # 3.提交判断
        if post_param.get('action', '') == 'submit':
            # 栏目
            cid = numeric(post_param.get('category'))
            if not cid: return alert(msg="没有选择栏目", act=3)
            if not html_escape(post_param.get('title', '')): return alert(msg="标题不能为空", act=3)
            category_data = self.db.list(table='category', field='upper', where=cid, shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            category_data['upper'].append(cid)
            # 评论、推荐、出版、审核
            res_list = []
            for row in ['comment', 'recom', 'published', 'audit']:
                if row in post_param: res_list.append(1)
                else: res_list.append(0)
            # 时间
            pushtime = mk_time(post_param.get('period_time'), "%Y-%m-%d %H:%M")

            # 权限
            authority = post_param.get('authority', [])
            for i in range(len(authority)):
                authority[i] = numeric(authority[i])
            data = {
                'category': json2dict(category_data['upper']),
                'title': html_escape(post_param.get('title', '')),
                'tag': html_escape(post_param.get('tag', '')),
                'sort': numeric(post_param.get('sort', 0), 0),
                'author': html_escape(post_param.get('author', '')),
                'source': html_escape(post_param.get('source', '')),
                'sourceurl': html_escape(post_param.get('sourceurl', '')),
                'keyword': html_escape(post_param.get('keyword', '')),
                'introduction': html_escape(post_param.get('introduction', '')),
                'template': post_param.get('template', ''),
                'description': html_escape(post_param.get('description', '')),
                'comment': res_list[0],
                'recom': res_list[1],
                'published': res_list[2],
                'audit': res_list[3],
                "authority": json2dict(authority),
                'recycle': 0,
                'picture': post_param.get('picture', []),
                'thumbnail': html_escape(post_param.get('thumbnail', '')),
                'commenttotal': numeric(post_param.get('commenttotal', 0), 0),
                'like': numeric(post_param.get('like', 0), 0),
                'click': numeric(post_param.get('click', 0), 0),
                'publisher': html_escape(post_param.get('publisher', '')),
                'pushtime': pushtime,
                'content': post_param.get('KgcmsEditor', '')
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)

            # 图片
            picture = post_param.get('picture', '')
            if picture:
                picture = [picture] if isinstance(picture, str) else picture
                while '' in picture:
                    picture.remove('')
                data['picture'] = picture
            if action == 'add':  # 添加文章
                data['picture'] = json2dict(data['picture'])
                data['webid'] = numeric(self.kg['web']['id'], 0)
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('article', data)
                if msg: return alert(msg="添加成功", act='article_manage')
                else: return alert(msg="添加失败", act=3)
            else:  # 编辑文章
                # 修改文件名
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='article', where=article_id, shift=1)['picture'])
                # 删除被删掉的图
                for var in source_pic:
                    if var not in data['picture']:
                        if exists(url_absolute(var), type='file'):
                            os.remove(url_absolute(var))  # 删除文件
                # 修改图名
                for i in range(len(data['picture'])):
                    cur_path = url_absolute(data['picture'][i])  # 当前路径(绝对)
                    path_list = data['picture'][i].split('/')
                    path_list[-1] = 'product_%s_%s%s' % (article_id, i, file_extension(data['picture'][i]))
                    re_path = '/'.join(path_list)  # 修改路径(相对)
                    # 修改文件命名
                    if exists(cur_path, type='file') and data['picture'][i] != re_path:
                        os.rename(cur_path, url_absolute(re_path))
                    # 替换文件路径
                    data['picture'][i] = re_path

                data['picture'] = json2dict(data['picture'])
                row = self.db.edit('article', data, where=article_id)
                if row: return alert(msg="编辑成功", act='article_manage')
                else: return alert(msg="编辑失败", act=3)
        # 非提交
        else:
            # 文章数据
            if action == "edit":
                from kyger.article import Article
                article_data = Article(self.db, self.kg).single(article_id, date='%Y-%m-%d %H:%M')
                if not article_data: return alert(msg="该文章不存在", act=3)
                article_data['content'] = html_escape(article_data['content'], False)
            else: article_data = {}
            # 文章数据整形
            data = {
                "id": article_data.get("id", 0),
                "category_title": article_data.get("category_title", ''),
                "title": article_data.get("title", ''),
                "tag": article_data.get("tag", ''),
                "sort": article_data.get("sort", ''),
                "author": article_data.get("author", ''),
                "source": article_data.get("source", ''),
                "sourceurl": article_data.get("sourceurl", ''),
                "keyword": article_data.get("keyword", ''),
                "introduction": article_data.get("introduction", ''),
                "description": article_data.get("description", ''),
                "template": article_data.get("template", ''),
                "comment": article_data.get("comment", 1),
                "recom": article_data.get("recom", 1),
                "published": article_data.get("published", 1),
                "audit": article_data.get("audit", 1),
                "commenttotal": article_data.get("commenttotal", ''),
                "like": article_data.get("like", ''),
                "click": article_data.get("click", ''),
                "publisher": article_data.get("publisher", ''),
                "pushtime": article_data.get("pushtime", date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                "content": article_data.get("content", ''),
                'picture': article_data.get('picture', []),
                'authority': article_data.get('authority', [0]),
                'thumbnail': article_data.get('thumbnail', '')
            }
            # 获取栏目列表
            from kyger.category import Category
            category_list = Category(self.db, self.kg).rank(cid="article")
            category_list.insert(0, {"id": 0, "title": "请选择栏目", "level": 1})
            # 获取用户等级
            rank = self.db.list(table='rank', where='webid=%s && enable=1' % self.kg['web']['id'])
            return template(assign={'data': data, 'category': category_list, 'action': action, 'rank': rank})
