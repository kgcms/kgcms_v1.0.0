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
        from kyger.weixin import Weixin
        from kyger.common import check_del_material
        wechat = Weixin(self.db, self.kg)

        get_param = self.kg['get']
        action = get_param.get('action', '')
        type = get_param.get('type', 'news')
        sort = numeric(get_param.get('sort', 0), 0, 3)
        word = get_param.get('word', '')
        page = numeric(get_param.get('page', 1), 1)
        if type in ['news', 'news1']:
            row = numeric(self.kg['cookie'].get('KGCMS_PICTURE_ROWS', 9))
        else:
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))

        # 获取图文素材列表做缓存
        if not exists(url_absolute('temp/wx_news_data.json'), 'file'):
            wx = Weixin(self.db, self.kg)
            res = wx.get_wx_material_list('news', 0, 1)
            if res.get('errcode'): return alert(msg="获取素材列表出错：%s" % res['errmsg'])
            cycle = (res['total_count'] // 20) + 1 if res['total_count'] % 20 else res['total_count'] // 20
            wx_news_data = {}
            for i in range(0, cycle):
                wx_datas = wx.get_wx_material_list('news', i * 20, 20)
                if wx_datas.get('errcode'): return alert(msg="获取素材列表出错：%s" % wx_datas['errmsg'])
                for wx_data in wx_datas['item']:
                    if len(wx_data['content']['news_item']) == 1:
                        wx_news_data[wx_data['media_id']] = wx_data['content']['news_item'][0]
                    else:
                        wx_news_data[wx_data['media_id']] = wx_data['content']['news_item']
            dict2json_file(wx_news_data, file='temp/wx_news_data.json')

        # 同步腾讯服务器数据
        if action == "syn":
            type_dict = {"news": "图文", "image": "图片", "video": "视频", "voice": "语音"}
            material_type = ['news', 'image', 'video', 'voice']
            cycle = numeric(get_param.get('cycle', 0), 0)
            type = get_param.get('type', 'news')

            if type not in material_type: return alert(msg="参数错误", alert=4)

            # 获取数据
            wx_data = wechat.get_wx_material_list(type, cycle * 20, 20)
            if wx_data.get('errcode', ''): return alert(msg='同步失败', act=4)  # 获取数据失败
            cycle_index = wx_data['total_count'] // 20  # 需要循环的次数

            # 获取media_id列表
            media_id_list = []
            for row in wx_data['item']:
                media_id_list.append(row['media_id'])

            #  查询腾讯素材数据库,获取addtime和description
            description_list = self.db.list(
                table='wx_material',
                field='id, media_id, type',
                where='media_id in ("%s")' % '","'.join(media_id_list)
            )
            id_list = [i['media_id'] for i in description_list]
            if type == 'news':
                dict2json_file({"wx_data['item']": wx_data['item'], "description_list": description_list}, file=("temp/news.json"))  # 删除调试
            if type == 'image':
                dict2json_file({"wx_data['item']": wx_data['item'], "description_list": description_list}, file=("temp/image.json"))  # 删除调试
            # 遍历腾讯接口返回的数据miedia_id列表
            for row in wx_data['item']:
                # 遍历本地数据库的关联数据
                if description_list:
                    for k in description_list:
                        if k['type'] == 'news':
                            # 图文素材
                            data = self.news(row)
                        else:
                            # 其他类型
                            data = self.other(row, k['type'], wechat)
                        # 存在则更新
                        if row['media_id'] in id_list:
                            self.db.edit("wx_material", data, where="media_id='%s'" % row['media_id'])
                        # 不存在则添加
                        else:
                            if k['type'] == 'news':
                                data.update({"addtime": int(self.kg['run_start_time'][1]), "description": "", "name":"","url":"","localpath":""})
                            else:
                                data.update({"addtime": int(self.kg['run_start_time'][1]), "description": ""})
                            res = self.db.add("wx_material",data)
                            if res == 0:return alert("插入错误")
                else:
                    if row.get('content', ''):
                        data = self.news(row)
                        data.update({"addtime": int(self.kg['run_start_time'][1]), "description": "", "name": "", "url": "",
                             "localpath": ""})
                        # news_type = 1 if len(row['content']['news_item']) > 1 else 0  # 单图多图
                        # data = {"media_id": row['media_id'], "type": "news", "news_type": news_type,
                        #         "update_time": row['update_time'], "addtime": int(self.kg['run_start_time'][1]), "description": "", "name": "", "url": "",
                        #      "localpath": ""}
                    else:
                        data = self.other(row, type, wechat)
                        data.update({"addtime": int(self.kg['run_start_time'][1]), "description": ""})
                        # extension = '.mp4' if type == "video" else file_extension(row['name'])  # 文件命名
                        # file_path = '/upload/wx_material/%s/%s' % (type, row['media_id'] + extension)
                        # data = {"media_id": row['media_id'], "name": row['name'], "type": type, "news_type": 0,
                        #         "url": row.get('url', ''), "localpath": file_path, "update_time": row['update_time'],"addtime": int(self.kg['run_start_time'][1]), "description": ""}
                    res2 = self.db.add("wx_material", data)
                    if res2 == 0:return alert("插入错误")

            # 循环请求逻辑
            end = 0
            if wx_data['total_count'] == 0 or cycle == cycle_index:
                cycle = 0
                # 同步完成
                if material_type.index(type) == 3:
                    next_type = ''
                    end = 1
                else:
                    next_type = material_type[material_type.index(type) + 1]
            else:
                cycle += 1
                next_type = type
            return template(
                assign={
                    'count': wx_data['total_count'],
                    'cycle': cycle,
                    'current_type': type_dict[type],
                    'next_type': next_type,
                    'end': end
                },
                tpl='wx_material_syn.tpl'
            )

        elif get_param.get('action', '') == 'del':
            media_id = get_param.get('mediaid', '')
            del_id = get_param.get("id", '')
            if not media_id:
                return alert(act=3, msg="素材不存在!")
            # 验证素材id是否被引用
            del_id, udel_list = check_del_material(self.db, [del_id])

            if del_id:
                wechat = Weixin(self.db, self.kg)
                wx_res = wechat.wx_material_news_del(media_id)
                if wx_res.get('errcode', '') != 0: return alert(msg='删除失败：%s' % wx_res['errmsg'], act=3)
                self.db.dele('wx_material', 'media_id = "%s"' % media_id)
                return alert(act=2, msg="删除成功")
            else:
                return alert(act=2, msg="被引用素材无法删除")

        # 获取数据
        else:
            # where
            word_sql = '&& name like "%%%s%%"' % word if word else ''
            if type == 'news':
                where = 'type = "news" && news_type = 0%s' % word_sql
            elif type == 'news1':
                where = 'type = "news" && news_type = 1%s' % word_sql
            else:
                where = 'type = "%s"%s' % (type, word_sql)

            # sort
            sort_param = {
                0: 'addtime DESC',
                1: 'addtime ASC',
                2: 'update_time DESC',
                3: 'update_time ASC'
            }

            # 查询数据
            data = self.db.list(
                table='wx_material',
                where=where,
                order=sort_param[sort],
                page=page,
                limit=row
            )
            if page > self.db.total_page:
                page = self.db.total_page
                data = self.db.list(
                    table='wx_material',
                    where=where,
                    order=sort_param[sort],
                    page=page,
                    limit=row
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            # 分页
            from kyger.common import page_tpl
            if type in ['news', 'news1']:
                page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'),
                                     action='set_picture', row_list=[3, 9, 36, 72, 144, 288, 576])
            else:
                page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'))

            # 数据整形
            news_data = json2dict(file='temp/wx_news_data.json')
            for row in data:
                row['update_time'] = date(row['update_time'], '%Y-%m-%d %H:%M:%S')
                row['name'] = row['name'].split('/')[-1]

                # 图文类型
                if type in ['news', 'news1']:
                    row['news'] = news_data[row['media_id']]

            # url拼接
            sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param),
                                                                                              deld='sort') else ''
            type_url = url_update(url_query2dict(get_param), deld='type') + '&' if url_update(url_query2dict(get_param),
                                                                                              deld='type') else ''
            url = {
                'type': type_url,
                'sort': sort_url,
            }

            return template(assign={
                'data': data,
                'type': type,
                'url': url,
                'sort': sort,
                'word': word,
                'page_html': page_html,
                'page_data': page_data
            })

    def news(self, row):
        news_type = 1 if len(row['content']['news_item']) > 1 else 0  # 单图多图
        data = {"media_id": row['media_id'], "type": "news", "news_type": news_type,
                "update_time": row['update_time']}
        # 下载资源
        # 获取图文素材的图片media_id并且下载图片
        # for var in row['news_item']:
        #     file_path = 'upload/wx_material/thumb/%s.jpg'
        #     if not exists(url_absolute(file_path), type='file'):
        #         put_contents(file_path % var['thumb_media_id'],
        #                      wechat.get_wx_material(var['thumb_media_id'], charset=''), 'wb')
        return data

    def other(self, row, type, wechat):
        extension = '.mp4' if type == "video" else file_extension(row['name'])  # 文件命名
        file_path = '/upload/wx_material/%s/%s' % (type, row['media_id'] + extension)
        # sql
        data = {"media_id": row['media_id'], "name": row['name'], "type": type, "news_type": 0,
                "url": row.get('url', ''), "localpath": file_path, "update_time": row['update_time']}

        # 下载资源
        if not exists(url_absolute(file_path), type='file'):
            import urllib.request

            # 视频返回的json数据包含下载地址
            if type == "video":
                video = json2dict(wechat.get_wx_material(row['media_id']))
                urllib.request.urlretrieve(video['down_url'], url_absolute(file_path))

            # 其他的直接返回二级制数据
            else:
                put_contents(file_path, wechat.get_wx_material(row['media_id'], charset=''), 'wb')
        return data












