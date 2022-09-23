# -*- coding:utf-8 -*-
"""广告及焦点图"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'aid': [30, "广告识别码长度不允许超过30个字符"],
            'title': [50, "广告名称长度不允许超过50个字符"],
            'size': [50, "文字大小不合法"],
            'color': [32, "链接颜色不合法"]
        }
        # 必填检测
        self.must_input = {
            'aid': '广告识别码',
            'title': '广告名称'
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert, mk_time, html_escape, str_replace, date, json2dict, exists, file_extension, url_absolute

        # 1.数据获取
        get_param = self.kg['get']  # get参数
        post_param = self.kg['post']  # post参数

        # 2.动作判断
        ad_id = numeric(get_param.get('ad_id', 0), 0)  # 获取编辑的广告id
        action = 'edit' if ad_id else 'add'

        # 3.提交判断
        audit = 1 if 'audit' in post_param else 0
        enable = 1 if 'enable' in post_param else 0
        if post_param.get('action', '') == 'submit':
            code = post_param.get('code', '')
            width = post_param.get('width', [])
            height = post_param.get('height', [])
            pic_size = []
            for i in range(len(width)):
                pic_size.append([width[i], height[i]])
            data = {
                'aid': html_escape(post_param.get('aid', '')),
                'title': html_escape(post_param.get('name', '')),
                'url': html_escape(post_param.get('url', '')),
                'color': html_escape(post_param.get('color', '')),
                'description': html_escape(post_param.get('info', '')),
                'sort': numeric(post_param.get('sort', 0), 0),
                'click': numeric(post_param.get('click', 0), 0),
                'weight': numeric(post_param.get('weight', 1), 1, 20),
                'code': code,
                'expired': html_escape(post_param.get('expired', '')),
                'audit': audit,
                'enable': enable,
                'size': html_escape(post_param.get('size', '')),
                'picture': post_param.get('picture', []),
                'summary': json2dict(post_param.get('summary', [])),
                'picurl': json2dict(post_param.get('picurl', [])),
                'content': html_escape(post_param.get('content', '')),
                'type': numeric(post_param.get('type', 1), 1, 3),
                'expir': numeric(post_param.get('expir', 1), 0, 1),
                'start': mk_time(post_param.get('start', ''), format="%Y-%m-%d %H:%M"),
                'end': mk_time(post_param.get('end', ''), format="%Y-%m-%d %H:%M"),
                'picsize': json2dict(pic_size)
            }
            # 数据库字段长度检测
            for field in self.long_check:
                if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
            for field in self.must_input:
                if len(data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)

            if action == 'add':
                data['picture'] = json2dict(data['picture'])
                data['webid'] = self.kg['web']['id']
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('ad', data)
                if not msg: return alert(msg='添加失败', act=3)
                else: return alert(act='ad_manage')
            else:
                # 修改文件名
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='ad', where=ad_id, shift=1)['picture'])
                count = max(len(source_pic), len(data['picture']))
                for i in range(count):
                    if i > len(source_pic) - 1:  # 超过了源图列表的索引
                        pass
                    elif i > len(data['picture']) - 1:  # 超过了当前图列表的索引
                        if exists(url_absolute(source_pic[i]), type='file'):
                            os.remove(url_absolute(source_pic[i]))  # 删除文件
                    else:
                        if source_pic[i] not in data['picture'] and exists(url_absolute(data['picture'][i]), type='file'):
                            if exists(url_absolute(source_pic[i]), type='file'):
                                os.remove(url_absolute(source_pic[i]))  # 删除文件

                # 重命名文件
                res_pic = []
                for i in range(len(data['picture'])):
                    path = data['picture'][i]
                    re_path = path.split('/')
                    re_path[-1] = 'ad_%s_%s%s' % (ad_id, i, file_extension(path))
                    if exists(url_absolute(path), type='file'):
                        os.rename(url_absolute(path), url_absolute('/'.join(re_path)))
                    res_pic.append('/'.join(re_path))
                data['picture'] = json2dict(res_pic)
                msg = self.db.edit('ad', data, ad_id)
                if not msg: return alert(msg='修改失败', act=3)
                else: return alert(act='ad_manage')
        else:
            # 广告数据
            if action == "edit":
                ad_data = self.db.list(table='ad', where=ad_id, shift=1)
                if not ad_data: return alert(msg="该广告不存在", act=3)
                ad_data['start'] = date(ad_data['start'], '%Y-%m-%d %H:%M')
                ad_data['end'] = date(ad_data['end'], '%Y-%m-%d %H:%M')
            else:
                ad_data = {}
            # 广告数据整形
            data = {
                "id": ad_data.get("id", 0),
                "aid": ad_data.get("aid", ''),
                "title": ad_data.get("title", ''),
                "url": ad_data.get("url", ''),
                "sort": ad_data.get("sort", 0),
                "code": ad_data.get("code", ''),
                "weight": ad_data.get("weight", ''),
                "click": ad_data.get("click", ''),
                "expir": ad_data.get("expir", 0),
                "start": ad_data.get("start", date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                "end": ad_data.get("end", date(int(self.kg['run_start_time'][1]), '%Y-%m-%d %H:%M')),
                "color": ad_data.get("color", '#fff'),
                "description": ad_data.get("description", ''),
                "expired": ad_data.get("expired", ''),
                "enable": ad_data.get("enable", 1),
                "audit": ad_data.get("audit", 1),
                'size': ad_data.get('size', ''),
                "picture": json2dict(ad_data.get('picture', '[]')),
                "summary": json2dict(ad_data.get('summary', '[]')),
                "picurl": json2dict(ad_data.get('picurl', '[]')),
                "content": ad_data.get('content', ''),
                "type": ad_data.get('type', 1),
                "picsize": json2dict(ad_data.get('picsize', '[]'))
            }
            # 获取栏目列表
        return template(assign={'data': data})
