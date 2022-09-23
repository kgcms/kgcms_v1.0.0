# -*- coding:utf-8 -*-
"""网站图片"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'aid': [30, "识别码长度不允许超过30个字符"],
            'author': [50, "文章作者长度不允许超过50个字符"],
            'source': [50, "来源长度不允许超过50个字符"],
            'sourceurl': [50, "来源网址长度不允许超过50个字符"],
            'template': [50, "自定义模板长度不允许超过50个字符"],
            'publisher': [20, "发布者长度不允许超过20个字符"]
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.picture import Picture
        from kyger.category import Category
        from kyger.utility import numeric, date, alert, html_escape, json2dict, mk_time, url_absolute, file_extension, exists

        picture = Picture(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = post_param.get('action', '')
        act_id = numeric(get_param.get('id', 0), 0)

        act = 'edit' if act_id else 'add'

        if action == "submit":
            # 栏目
            cid = numeric(post_param.get('category'), 0)
            if not cid: return alert(msg="没有选择栏目", act=3)
            if not html_escape(post_param.get('title', '')): return alert(msg="标题不能为空", act=3)
            category_data = self.db.list(table='category', field='upper', where=cid, shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            category_data['upper'].append(cid)
            # 评论、推荐、出版、审核
            res_list = []
            for row in ['comment', 'recom', 'published', 'audit']:
                if row in post_param:
                    res_list.append(1)
                else:
                    res_list.append(0)
            # 时间
            pushtime = mk_time(post_param.get('pushtime'), "%Y-%m-%d %H:%M")

            # json类型
            json_data = {}
            for var in ['summary', 'picture', 'pictime', 'link']:
                json_data[var] = post_param.get(var, [])
            if json_data['pictime']:
                for i in range(len(json_data['pictime'])):
                    json_data['pictime'][i] = numeric(json_data['pictime'][i])
            # 权限
            authority = post_param.get('authority', [])
            for i in range(len(authority)):
                authority[i] = numeric(authority[i])
            data = {
                'webid': numeric(self.kg['web']['id'], 0),
                'category': json2dict(category_data['upper']),
                'title': html_escape(post_param.get('title', '')),
                'tag': html_escape(post_param.get('tag', '')),
                'sort': numeric(post_param.get('sort', 0), 0),
                'author': html_escape(post_param.get('author', '')),
                'source': html_escape(post_param.get('source', '')),
                'sourceurl': html_escape(post_param.get('sourceurl', '')),
                'keyword': html_escape(post_param.get('keyword', '')),
                'aid': html_escape(post_param.get('aid', '')),
                'template': post_param.get('template', ''),
                'summary': json2dict(json_data['summary']),
                'description': html_escape(post_param.get('description', '')),
                'comment': res_list[0],
                'recom': res_list[1],
                'published': res_list[2],
                'audit': res_list[3],
                'recycle': 0,
                "authority": json2dict(authority),
                'link': json2dict(json_data['link']),
                'pictime': json2dict(json_data['pictime']),
                'picture': json_data['picture'],
                'commenttotal': numeric(post_param.get('commenttotal', 0), 0),
                'agree': numeric(post_param.get('like', 0), 0),
                'click': numeric(post_param.get('click', 0), 0),
                'publisher': html_escape(post_param.get('publisher', '')),
                'pushtime': pushtime,
                'content': post_param.get('KgcmsEditor', ''),
                'thumbnail': html_escape(post_param.get('thumbnail', ''))
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)

            if act == 'add':  # 添加图集
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('picture', data)
                if msg:
                    return alert(act='picture_manage')
                else:
                    return alert(msg="添加失败", act=3)
            else:  # 编辑文章
                # 修改文件名
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='picture', where=act_id, shift=1)['picture'])
                # 删除被删掉的图
                for var in source_pic:
                    if var not in data['picture']:
                        if exists(url_absolute(var), type='file'):
                            os.remove(url_absolute(var))  # 删除文件
                # 修改图名
                for i in range(len(data['picture'])):
                    cur_path = url_absolute(data['picture'][i])  # 当前路径(绝对)
                    path_list = data['picture'][i].split('/')
                    path_list[-1] = 'product_%s_%s%s' % (act_id, i, file_extension(data['picture'][i]))
                    re_path = '/'.join(path_list)  # 修改路径(相对)
                    # 修改文件命名
                    if exists(cur_path, type='file') and data['picture'][i] != re_path:
                        os.rename(cur_path, url_absolute(re_path))
                    # 替换文件路径
                    data['picture'][i] = re_path

                data['picture'] = json2dict(data['picture'])
                row = self.db.edit('picture', data, where=act_id)
                if row:
                    return alert(act='picture_manage')
                else:
                    return alert(msg="编辑失败", act=3)
        else:
            pic_data = picture.single(act_id, '%Y-%m-%d %H:%M') if act == "edit" else {}
            data = {
                'id': pic_data.get('id', 0),
                'category': pic_data.get('category', []),
                'title': pic_data.get('title', ''),
                'aid': pic_data.get('aid', ''),
                'tag': pic_data.get('tag', ''),
                'author': pic_data.get('author', ''),
                'source': pic_data.get('source', ''),
                'sourceurl': pic_data.get('sourceurl', ''),
                'keyword': pic_data.get('keyword', ''),
                'content': pic_data.get('content', ''),
                'template': pic_data.get('template', ''),
                'comment': pic_data.get('comment', 1),
                'commenttotal': pic_data.get('commenttotal', 0),
                'agree': pic_data.get('agree', 0),
                'picture': pic_data.get('picture', []),
                'description': pic_data.get('description', ''),
                'summary': pic_data.get('summary', []),
                'pictime': pic_data.get('pictime', []),
                'link': pic_data.get('link', []),
                'recom': pic_data.get('recom', 0),
                'audit': pic_data.get('audit', 1),
                'published': pic_data.get('published', 1),
                'click': pic_data.get('click', 0),
                'sort': pic_data.get('sort', 0),
                'publisher': pic_data.get('publisher', self.kg['session']['KGCMS_ADMIN_LOGIN_ID']),
                'pushtime': pic_data.get('pushtime', date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                'category_title': pic_data.get('category_title', ''),
                'pic_date': pic_data.get('pic_date', []),
                'authority': pic_data.get('authority', []),
                'thumbnail': pic_data.get('thumbnail', '')
            }

            # 图集栏目
            category_data = Category(self.db, self.kg).rank('photo')
            # 获取用户等级
            rank = self.db.list(table='rank', where='webid=%s && enable=1' % self.kg['web']['id'])
            return template(assign={
                'data': data,
                'category': category_data,
                'rank': rank
            })
