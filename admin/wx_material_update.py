# -*- coding:utf-8 -*-
"""网站文章"""

from kyger.utility import *
import json
import os


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        weixin = Weixin(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = post_param.get("action")

        material_id = numeric(get_param.get('id', ''), 0)
        act = 'edit' if material_id else 'add'

        if action == "submit":
            if act == 'add':
                material_type = numeric(post_param.get('type', 0), 0, 3)
                # 图文素材
                if material_type == 0:
                    titles = post_param.get('title', [])

                    articles = []
                    for i in range(len(titles)):
                        digest = '' if len(titles) > 1 else post_param['digest'][i]
                        news = {
                            "title": titles[i],
                            "thumb_media_id": post_param['thumb_media_id'][i],
                            "author": post_param['author'][i],
                            "digest": digest,
                            "show_cover_pic": 1,
                            "content": self.text_deal(post_param['content'][i]),
                            "content_source_url": post_param['content_source_url'][i],
                            "need_open_comment": numeric(post_param['need_open_comment'][i], 0, 1),
                        }
                        # 必须数据检测
                        if not news['title']: return alert(msg='必须给每篇文章设置标题', act=3)
                        if not news['thumb_media_id']: return alert(msg='必须给每篇文章设置封面', act=3)
                        if not news['content']: return alert(msg='必须给每篇文章设置内容', act=3)

                        if news['need_open_comment']:
                            news['only_fans_can_comment'] = numeric(post_param['only_fans_can_comment'][i], 0, 1)
                        articles.append(news)

                    wx_res = weixin.wx_material_news_add(articles)
                    if wx_res.get('errcode', ''): return alert(msg=wx_res['errmsg'], act=3)
                    # 写数据
                    news_type = 1 if len(titles) > 1 else 0
                    current_time = int(self.kg['run_start_time'][1])
                    news_data = {
                        'media_id': wx_res['media_id'],
                        'name': '',
                        'type': 'news',
                        'news_type': news_type,
                        'url': '',
                        'localpath': '',
                        'update_time': current_time,
                        'addtime': current_time,
                        'description': ''
                    }
                    self.db.add('wx_material', news_data)
                    # 添加数据到缓存
                    media_data = json2dict(weixin.get_wx_material(wx_res['media_id']))
                    if media_data.get('errcode'):
                        os.remove(url_absolute('temp/wx_news_data.json'))
                        return alert(act='wx_material_manage')
                    news_data = json2dict(file='temp/wx_news_data.json')
                    if news_type:
                        news_data[wx_res['media_id']] = media_data['news_item']
                    else:
                        news_data[wx_res['media_id']] = media_data['news_item'][0]
                    dict2json_file(news_data, file='temp/wx_news_data.json')
                    return alert(act='wx_material_manage')

                elif material_type == 1:
                    pictures = post_param.get('picture', [])
                    if not pictures: return alert(msg="必须至少上传一张图", act=3)
                    sql = "INSERT INTO `kg_wx_material`(`media_id`, `name`, `type`, `news_type`, `url`, `localpath`, `update_time`, `addtime`, `description`) VALUES %s"
                    values = []
                    for row in pictures:
                        wx_data = weixin.wx_material_add('image', row)
                        if wx_data.get('errcode', ''): return alert(msg=wx_data['errmsg'], act=3)
                        local = '/upload/wx_material/image/%s' % wx_data['media_id'] + file_extension(row)
                        os.rename(url_absolute(row), url_absolute(local))
                        cur_time = int(self.kg['run_start_time'][1])
                        sql_val = (wx_data['media_id'], row.split('/')[-1], 'image', 0, wx_data['url'], local, cur_time, cur_time, '')
                        values.append("('%s','%s','%s',%s,'%s','%s',%s,%s,'%s')" % sql_val)
                    self.db.run_sql(sql % ','.join(values), 'add', log=False)
                    return alert(act='wx_material_manage?type=image')

                elif material_type == 2:
                    # 上传文件
                    file = post_param.get('voice', '')  # 获取文件数据
                    if not file: return alert(msg="没有选择文件", act=3)
                    from kyger.upload import Upload
                    up = Upload(file, self.db, self.kg)  # 创建实例
                    up.path = 0  # 不创建路径
                    up.exist_rename = False  # 文件名存在是否自动重命名。命名规则:*(1).*
                    msg = up.file('wx_material/voice')  # 上传到upload/wx_material/voice

                    # 上传到微信
                    if msg.get('state', '') != "SUCCESS": return alert(msg="上传失败%s" % msg, act=3)
                    re_wx = weixin.wx_material_add('voice', msg['url'])
                    if re_wx.get('errcode', ''): return alert(msg=re_wx.get('errmsg', '未知'), act=3)
                    local = '/upload/wx_material/voice/%s' % re_wx['media_id'] + file_extension(msg['url'])
                    os.rename(url_absolute(msg['url'][1:]), url_absolute(local[1:]))
                    current_time = int(self.kg['run_start_time'][1])
                    voice_data = {
                        'media_id': re_wx['media_id'],
                        'name': msg['filename'],
                        'type': 'voice',
                        'news_type': 0,
                        'url': '',
                        'localpath': local,
                        'update_time': current_time,
                        'addtime': current_time,
                        'description': ''
                    }
                    self.db.add('wx_material', voice_data)
                    return alert(act='wx_material_manage?type=voice')

                else:
                    # 参数
                    title = post_param.get('v_title', '')
                    description = post_param.get('v_description', '')
                    if not all([title, description]): return alert(msg='请填写标题和摘要', act=3)

                    # 上传文件
                    file = post_param.get('video', '')  # 获取文件数据
                    if not file: return alert(msg="没有选择文件", act=3)
                    from kyger.upload import Upload
                    up = Upload(file, self.db, self.kg)  # 创建实例
                    up.path = 0  # 不创建路径
                    up.exist_rename = False  # 文件名存在是否自动重命名。命名规则:*(1).*
                    msg = up.file('wx_material/video')  # 上传到upload/wx_material/video

                    # 上传到微信
                    if msg.get('state', '') != "SUCCESS": return alert(msg="上传失败", act=3)
                    re_wx = weixin.wx_material_add('video', msg['url'], title=title, introduction=description)
                    if re_wx.get('errcode', ''): return alert(msg=re_wx.get('errmsg', '未知'), act=3)
                    local = '/upload/wx_material/video/%s' % re_wx['media_id'] + file_extension(msg['url'])
                    os.rename(url_absolute(msg['url'][1:]), url_absolute(local[1:]))
                    current_time = int(self.kg['run_start_time'][1])
                    video_data = {
                        'media_id': re_wx['media_id'],
                        'name': title,
                        'type': 'video',
                        'news_type': 0,
                        'url': '',
                        'localpath': local,
                        'update_time': current_time,
                        'addtime': current_time,
                        'description': description
                    }
                    self.db.add('wx_material', video_data)
                    return alert(act='wx_material_manage?type=video')

            # 修改图文
            else:
                titles = post_param.get('title', [])
                edit_material = self.db.list(table='wx_material', where=material_id, shift=1)
                if not edit_material: return alert(msg='该素材不存在', act=2)
                for i in range(len(titles)):
                    digest = '' if len(titles) > 1 else post_param['digest'][i]
                    news = {
                        "media_id": edit_material['media_id'],
                        "index": i,
                        "articles": {
                            "title": titles[i],
                            "thumb_media_id": post_param['thumb_media_id'][i],
                            "author": post_param['author'][i],
                            "digest": digest,
                            "show_cover_pic": 1,
                            "content": self.text_deal(post_param['content'][i]),
                            "content_source_url": post_param['content_source_url'][i]
                        }
                    }
                    wx_res = weixin.wx_material_news_update(news)
                    if wx_res.get('errcode') != 0: return alert(msg='更新失败：%s' % wx_res['errmsg'], act=3)

                if len(titles) > 1:
                    url = 'wx_material_manage?type=news1'
                    news_type = 1
                else:
                    url = 'wx_material_manage?type=news'
                    news_type = 0
                update_data = {
                    "addtime": int(self.kg['run_start_time'][1]),
                    "news_type": news_type
                }
                self.db.edit('wx_material', update_data, material_id)
                return alert(act=url)

        elif action == "upload":
            dir = post_param.get('dir', 'other')
            file = post_param.get('file', {'data': ''})
            mater_type = post_param.get('type', '')
            from kyger.upload import Upload
            if file:
                up = Upload(file, self.db, self.kg)
                up.path = 0  # 不创建路径
                up.exist_rename = False  # 文件名存在是否自动重命名。
                up.filename = '{y}{mm}{dd}{hh}{ii}{ss}'  # 文件命名规则
                msg = up.file(dir, True)

                if mater_type == "image":
                    return json.dumps({
                        'status': 1,
                        "url": msg['url'],
                        "media_id": ''
                    })
                if not msg.get('url', ''): return json.dumps({'status': 0, 'msg': msg.get('msg', 'unknown')})

                wx_data = weixin.wx_material_add("thumb", msg['url'])

                if wx_data.get("errcode", ''):
                    return json.dumps({'status': 0, 'msg': wx_data['errmsg']})
                else:
                    os.rename(url_absolute(msg['url']), url_absolute('upload/wx_material/thumb/%s.jpg' % wx_data['media_id']))
                    return json.dumps({
                        'status': 1,
                        "url": '/upload/wx_material/thumb/%s.jpg' % wx_data['media_id'],
                        "media_id": wx_data['media_id']
                    })

        else:
            if act == 'edit':
                edit_material = self.db.list(
                    table='wx_material',
                    where=material_id,
                    shift=1
                )
                if not edit_material: return alert(msg='该条素材不存在', act=3)
                if edit_material['type'] != 'news': return alert(msg="非图文素材不允许修改", act=3)

                # 获取改素材的数据
                wx_res = json2dict(weixin.get_wx_material(edit_material['media_id']))
                if wx_res.get('errcode', ''): return alert(msg="获取素材出错：%s" % wx_res['errmsg'], act=3)
                data = wx_res['news_item']
            else:
                data = [{
                    "title": '',
                    "thumb_media_id": '',
                    "show_cover_pic": 1,
                    "author": '',
                    "digest": '',
                    "content": '',
                    "url": '',
                    "content_source_url": ''
                }]
            for var in data:
                var['content'] = str_replace(var['content'], ['data-src='], 'src=')

            return template(assign={
                'act': act,
                'data': data
            })

    def text_deal(self, content):
        """
        图文素材内容处理
        :param content: [str] 文章内容html代码
        :return:
        """
        import re, os
        from kyger.weixin import Weixin
        weixin = Weixin(self.db, self.kg)

        # 过滤标签
        content = strip_tags(content, 'img,span,em,strong,a')
        # 转义替换
        content = str_replace(content, ['\\"', '\\\\'], ['\"', '\\'])
        # 图片
        picture_list = re.findall('<img .*?src="(.*?)".*?>', content)
        replace_list = []
        for row in picture_list:
            # 微信的链接图
            if url_parse(row, ret='netloc') == 'mmbiz.qpic.cn':
                replace_list.append(row)
            # 非本站图片
            elif row.find('://') > 0:
                res = get_contents(row, mode='rb', charset="", method="GET")
                put_contents('temp/news_temp.png', res, mode='wb', charset="")
                wx_res = weixin.wx_material_news_uploadimg('temp/news_temp.png')
                os.remove(url_absolute('temp/news_temp.png'))
                if wx_res.get('errcode', ''): return alert(msg="文章图片上传失败：%s" % wx_res['errmsg'], act=3)
                replace_list.append(wx_res['url'])
            # 已上传至本站的图片
            else:
                wx_res = weixin.wx_material_news_uploadimg(row)
                if wx_res.get('errcode', ''): return alert(msg="文章图片上传失败：%s" % wx_res['errmsg'], act=3)
                replace_list.append(wx_res['url'])
        content = str_replace(content, picture_list, replace_list)
        return content




