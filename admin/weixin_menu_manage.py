# -*- coding:utf-8 -*-
"""微信自定义菜单"""

from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        wx = Weixin(self.db, self.kg)

        get_param = self.kg['get']
        post_param = self.kg['post']
        # dict2json_file({"post":post_param, "get":get_param},file=("temp/json2222.json"))
        # 修改菜单
        if post_param.get('action', '') == 'submit':
            import json
            data = self.data_format()
            # dict2json_file(data, file=("temp/tempss.json"))
            msg = wx.update_menu(json.dumps(data, ensure_ascii=False))
            # 出错判断
            if msg.get('errcode', ''):
                # dict2json_file({"msg": msg}, file=("temp/test/errmsg.json"))
                return alert(msg=msg['errmsg'], act=3)
            return alert(act=2)

        # 获取菜单数据
        else:
            data = wx.get_menu()
            # dict2json_file(data, file=("temp/getdata.json"))
            local_material = self.db.list(table='material')
            wx_material = self.db.list(table='wx_material', where='type="news"')
            # 数据整形
            news_data = json2dict(file="temp/wx_news_data.json")
            if isinstance(news_data, dict):
                for row in wx_material:
                    row['update_time'] = date(row['update_time'], '%Y-%m-%d %H:%M:%S')
                    row['name'] = row['name'].split('/')[-1]
                    row['news'] = news_data[row['media_id']]
            return template(assign={
                'data': [],
                'local': local_material,
                'wx': wx_material
            })

    def data_format(self):
        """
        数据整形函数
        """
        btn_type = [
            {'type': ['miniprogram'], 'param': ['type', 'name', 'url', 'appid', 'pagepath']},
            {'type': ['view'], 'param': ['type', 'name', 'url']},
            {'type': ['media_id', 'view_limited'], 'param': ['type', 'name', 'media_id', 'key']},
            {'type': ['location', 'click'], 'param': ['type', 'name', 'key']},
            {
                'type': ['scancode_waitmsg', 'scancode_push', 'pic_sysphoto', 'pic_photo_or_album', 'pic_weinxin'],
                'param': ['type', 'name', 'key', 'sub_button']
            }
        ]

        post_param = self.kg['post']
        # dict2json_file({"post":post_param},file=("temp/test/post.json"))
        data = []
        for i in range(len(post_param.get('menu_name', []))):
            menu = {}

            # 没有子菜单
            if post_param['menu_type'][i]:
                for row in btn_type:
                    if post_param['menu_type'][i] in row['type']:
                        for var in row['param']:
                            menu[var] = post_param['menu_%s' % var][i]
                        break
                data.append(menu)

            # 有子菜单
            else:
                menu = {'name': post_param['menu_name'][i], 'sub_button': []}
                for n in range(len(post_param['button_name[%s]' % i])):
                    btn = {}
                    for row in btn_type:
                        if post_param['button_type[%s]' % i][n] in row['type']:
                            for var in row['param']:
                                btn[var] = [] if var == 'sub_button' else post_param['button_%s[%s]' % (var, i)][n]
                            menu['sub_button'].append(btn)
                            break
                data.append(menu)
        # dict2json_file({"resdata":data},file=("temp/test/resdata.json"))

        return {'button': data}

