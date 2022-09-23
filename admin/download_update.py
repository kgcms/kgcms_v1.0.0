# -*- coding:utf-8 -*-
"""下载添加"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'downname': [50, "自定义下载名长度不允许超过50个字符"],
            'color': [7, "标题颜色不合法"],
            'author': [50, "文章作者长度不允许超过50个字符"],
            'source': [50, "来源长度不允许超过50个字符"],
            'sourceurl': [50, "来源网址长度不允许超过50个字符"],
            'demourl': [50, "演示网址长度不允许超过50个字符"],
            'version': [50, "版本号长度不允许超过50个字符"],
            'softlang': [50, "软件语言长度不允许超过50个字符"],
            'authorization': [50, "授权方式长度不允许超过50个字符"],
            'size': [20, "软件大小不合法"],
            'template': [50, "自定义模板长度不允许超过50个字符"],
            'filename': [50, "自定义文件名长度不允许超过50个字符"],
            'publisher': [20, "发布者长度不允许超过20个字符"]
        }
        # 必填检测
        self.must_input = {
            'category': '所属栏目',
            'title': '下载标题'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, json2dict, alert, mk_time, html_escape, file_list, date, exists, url_absolute, file_extension


        # 1.数据获取
        get_param = self.kg['get']  # get参数
        post_param = self.kg['post']  # post参数

        # 2.动作判断
        download_id = numeric(get_param.get('id', 0), 0)  # 获取编辑的下载id
        action = 'edit' if download_id else 'add'
        # 3.提交判断
        if post_param.get('action', '') == 'submit':
            # 栏目
            cid = numeric(post_param.get('category'))
            if not cid: return alert(msg="没有选择栏目", act=3)
            if not html_escape(post_param.get('title', '')): return alert(msg="标题不能为空", act=3)
            category_data = self.db.list(table='category', field='upper', where=cid, shift=1)
            category_data['upper'] = json2dict(category_data['upper'])
            category_data['upper'].append(cid)
            # 评论、推荐、审核.标题加粗
            res_list = []
            for row in ['comment', 'recom', 'audit', 'bold']:
                if row in post_param:
                    res_list.append(1)
                else:
                    res_list.append(0)
            # 时间
            pushtime = mk_time(post_param.get('pushtime'), "%Y-%m-%d %H:%M")

            # 软件权限
            per_list = []
            for i in post_param.get('permission', []):
                per_list.append(int(i))
            # 下载镜像
            mirror_name = post_param.get('mirror_name')
            mirror_url = post_param.get('mirror_url')
            if isinstance(mirror_name, str): mirror_name = [mirror_name]
            if isinstance(mirror_url, str): mirror_url = [mirror_url]
            mirror = []
            for i in range(len(mirror_name)):
                mirror.append({"name": html_escape(mirror_name[i]), "url": html_escape(mirror_url[i])})
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
                'template': html_escape(post_param.get('template', '')),
                'buyuser': post_param.get('buyuser', []),
                'permission': per_list,
                'authority': authority,
                'comment': res_list[0],
                'recom': res_list[1],
                'authorization': html_escape(post_param.get('authorization', '')),
                'mode': numeric(post_param.get('mode', 0)),
                'color': html_escape(post_param.get('color', '')),
                'local': html_escape(post_param.get('file', '')),
                'mirror': json2dict(mirror),
                'audit': res_list[2],
                'bold': res_list[3],
                'recycle': 0,
                'picture': post_param.get('picture', []),
                'thumbnail': html_escape(post_param.get('thumbnail', '')),
                'agree': numeric(post_param.get('agree', 0)),
                'filename': html_escape(post_param.get('filename', '')),
                'count': numeric(post_param.get('count', 0)),
                'money': numeric(post_param.get('money', 0)),
                'integral': numeric(post_param.get('integral', 0)),
                'commenttotal': numeric(post_param.get('commenttotal', 0), 0),
                'click': numeric(post_param.get('click', 0), 0),
                'publisher': html_escape(post_param.get('publisher', '')),
                'pushtime': pushtime,
                'content': post_param.get('KgcmsEditor', ''),
                'size': html_escape(post_param.get('size', '0')),
                'softlang': html_escape(post_param.get('softlang', '')),
                'environment': html_escape(post_param.get('environment', '')),
                'demourl': html_escape(post_param.get('demourl', '')),
                'addtime': int(self.kg['run_start_time'][1]),
                "version": html_escape(post_param.get('version', '')),
                "description": html_escape(post_param.get('description', '')),
                'downname': html_escape(post_param.get('downname', '')),
                'defaultdown': numeric(post_param.get('defaultdown', 0), 0)
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)

            picture = post_param.get('picture', '')
            if picture:
                picture = [picture] if isinstance(picture, str) else picture
                while '' in picture:
                    picture.remove('')
                data['picture'] = picture

            if action == 'add':  # 添加下载
                data['picture'] = json2dict(data['picture'])
                data['webid'] = numeric(self.kg['web']['id'], 0)
                msg = self.db.add('download', data)
                if msg:
                    return alert(msg="添加成功", act='download_manage')
                else:
                    return alert(msg="添加失败", act=3)
            else:  # 编辑下载
                # 修改文件名
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='download', where=download_id, shift=1)['picture'])
                # 删除被删掉的图
                for var in source_pic:
                    if var not in data['picture']:
                        if exists(url_absolute(var), type='file'):
                            os.remove(url_absolute(var))  # 删除文件
                # 修改图名
                for i in range(len(data['picture'])):
                    cur_path = url_absolute(data['picture'][i])  # 当前路径(绝对)
                    path_list = data['picture'][i].split('/')
                    path_list[-1] = 'product_%s_%s%s' % (download_id, i, file_extension(data['picture'][i]))
                    re_path = '/'.join(path_list)  # 修改路径(相对)
                    # 修改文件命名
                    if exists(cur_path, type='file') and data['picture'][i] != re_path:
                        os.rename(cur_path, url_absolute(re_path))
                    # 替换文件路径
                    data['picture'][i] = re_path

                data['picture'] = json2dict(data['picture'])
                row = self.db.edit('download', data, where=download_id)
                if row:
                    return alert(msg="编辑成功", act='download_manage')
                else:
                    return alert(msg="编辑失败", act=3)
        # 上传文件
        elif post_param.get('action', '') == 'file':
            from kyger.upload import Upload
            import json
            file = self.kg['post'].get('file', {'data': ''})
            msg = Upload(file, self.db, self.kg).file('download/file', False)
            if msg.get('state', '') == "SUCCESS":
                return json.dumps({"status": 1, "path": msg['url']})
            elif msg.get('state', '') == "FAILURE":
                return json.dumps({"status": 0, "msg": msg['msg']})
            else:
                return json.dumps({"status": 0, "msg": "unknown erro"})
        # 非提交
        else:
            # 下载数据
            if action == "edit":
                from kyger.download import Download
                download_data = Download(self.db, self.kg).single(download_id, date='%Y-%m-%d %H:%M')
                if not download_data: return alert(msg="该下载不存在", act=3)
                download_data['content'] = html_escape(download_data['content'], False)
            else:
                download_data = {}

            # 下载权限
            get_pers = self.db.list(table='rank', field='id, rankname', where="webid=%s" % self.kg["web"]["id"])

            # 下载数据整形
            data = {
                "id": download_data.get("id", 0),
                "category_title": download_data.get("category_title", ''),
                "title": download_data.get("title", ''),
                "tag": download_data.get("tag", ''),
                "sort": download_data.get("sort", ''),
                "author": download_data.get("author", ''),
                "source": download_data.get("source", ''),
                "sourceurl": download_data.get("sourceurl", ''),
                # seo关键字
                "keyword": download_data.get("keyword", ''),
                # 下载权限
                "permission": download_data.get("permission", []),
                "template": download_data.get("template", ''),
                "comment": download_data.get("comment", 1),
                "recom": download_data.get("recom", 1),
                "bold": download_data.get("bold", 1),
                "color": download_data.get("color", ''),
                "local": download_data.get("local", ''),
                "mirror": download_data.get("mirror", ''),
                "audit": download_data.get("audit", 1),
                'authority': download_data.get('authority', []),
                "commenttotal": download_data.get("commenttotal", ''),
                # 浏览人数
                "click": download_data.get("click", ''),
                # 发布者
                "publisher": download_data.get("publisher", ''),
                "pushtime": download_data.get("pushtime", date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                "content": download_data.get("content", ''),
                'picture': download_data.get('picture', []),
                'thumbnail': download_data.get('thumbnail', ''),
                "size": download_data.get("size", '0'),
                "softlang": download_data.get("softlang", '简体中文'),
                "environment": download_data.get("environment", 'win7'),
                "demourl": download_data.get("demourl", 'www.com'),
                "version": download_data.get("version", ''),
                "description": download_data.get("description", ''),
                "count": download_data.get('count', 0),
                'downname': download_data.get('downname', ''),
                'defaultdown': download_data.get('defaultdown', 0)
            }
            # 获取栏目列表
            from kyger.category import Category
            category_list = Category(self.db, self.kg).rank(cid="download")
            category_list.insert(0, {"id": 0, "title": "请选择栏目", "level": 1})
            # 获取用户等级
            rank = self.db.list(table='rank', where='webid=%s && enable=1' % self.kg['web']['id'])
            return template(
                assign={
                    'data': data, 'category': category_list, 'action': action, 'per': get_pers, 'rank': rank
                },
            )
