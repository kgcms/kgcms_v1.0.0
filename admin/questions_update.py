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
        post_param = self.kg['post']
        get_param = self.kg['get']
        role_id = numeric(get_param.get('id', ''), 0)
        act = 'edit' if role_id else 'add'

        # 提交数据
        if post_param.get("action", '') == "submit":
            type = numeric(post_param.get('type'), 0, 2)
            if type == 0:
                mid = numeric(post_param.get('local'))
            elif type == 1:
                wx_type = numeric(post_param.get('wx_type'), 1, 4)
                type_list = ['news', 'image', 'voice', 'video']
                mid = numeric(post_param.get(type_list[wx_type - 1]))
            else:
                mid = 0
            data = {
                'ask': json2dict(post_param.get('ask', [])),
                'mid': mid,
                'type': type,
                'answer': post_param.get('answer', '' ),
                'rule': numeric(post_param.get('rule', 0), 0, 1),
                'enable': numeric(post_param.get('enable', 0))
            }
            if act == 'edit':
                msg = self.db.edit('wx_questions', data, role_id)
                if msg: return alert(act='questions_manage')
                else: return alert(msg='修改失败', act=3)
            else:
                data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('wx_questions', data)
                if msg: return alert(act='questions_manage')
                else: return alert(msg='添加失败', act=3)

        # 获取页面
        else:
            # 获取该id数据
            if act == 'edit':
                role_data = self.db.list(
                    table='wx_questions',
                    where=role_id,
                    shift=1
                )
                role_data['ask'] = json2dict(role_data['ask'])
            else:
                role_data = {}

            # 组织数据
            data = {
                'id': role_data.get('id', ''),
                'ask': role_data.get('ask', []),
                'type': role_data.get('type', 0),
                'mid': role_data.get('mid', ''),
                'answer': role_data.get('answer', ''),
                'rule': role_data.get('rule', 0),
                'enable': role_data.get('enable', 1),
                'addtime': role_data.get('addtime', int(self.kg['run_start_time'][1]))
            }

            # 本地素材与微信素材数据
            news = self.db.list(table='wx_material', where='type="news"')
            image = self.db.list(table='wx_material', where='type="image"')
            voice = self.db.list(table='wx_material', where='type="voice"')
            video = self.db.list(table='wx_material', where='type="video"')
            local = self.db.list(table="material")

            # 微信素材类型
            wx_type = ''
            if data['type'] == 1:
                material_type = self.db.list(table='wx_material', where=data['mid'], shift=1)
                wx_type = material_type.get('type', '')

            return template(assign={
                "data": data,
                'news': news,
                'image': image,
                'voice': voice,
                'video': video,
                'local': local,
                "wx_type": wx_type
            })
