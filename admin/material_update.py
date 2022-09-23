# -*- coding:utf-8 -*-
"""添加素材"""

from kyger.utility import *

class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 获取素材id
        material_id = numeric(get_param.get('id', 0), 0)
        act = 'edit' if material_id else 'add'

        # 是否为提交
        if post_param.get('action', '') == 'submit':
            material_data = {
                'name': html_escape(post_param.get('name', '')),
                'type': numeric(post_param.get('type', 0)),
                'pushtime': mk_time(post_param.get('period_time'), '%Y-%m-%d %H:%M'),
                'introduction': '',
                'title': json2dict([]),
                'picture': [],
                'key2url': json2dict([])
            }
            if not material_data['name']: return alert('素材名称必须填写')
            # 文本
            if material_data['type'] == 2:
                material_data['introduction'] = post_param.get('word_introduction', '')

            # 单图
            if material_data['type'] == 0:
                material_data['introduction'] = post_param.get('pic_introduction', '')
                if post_param.get('s_title', []): material_data['title'] = json2dict(post_param.get('s_title'))
                if post_param.get('s_picture', []): material_data['picture'] = post_param.get('s_picture')
                if post_param.get('s_key2url', []): material_data['key2url'] = json2dict(post_param.get('s_key2url'))

            # 多图
            if material_data['type'] == 1:
                if post_param.get('title', []): material_data['title'] = json2dict(post_param.get('title'))
                if post_param.get('picture', []): material_data['picture'] = post_param.get('picture')
                if post_param.get('key2url', []): material_data['key2url'] = json2dict(post_param.get('key2url'))

            # 数据添加与修改
            if act == 'edit':
                # 图片命名修改
                import os
                # 删除被用户删除的数据
                source_pic = json2dict(self.db.list(table='material', where=material_id, shift=1)['picture'])
                # 删除被删掉的图
                for var in source_pic:
                    if var not in material_data['picture']:
                        if exists(url_absolute(var), type='file'):
                            os.remove(url_absolute(var))  # 删除文件
                # 修改图名
                for i in range(len(material_data['picture'])):
                    cur_path = url_absolute(material_data['picture'][i])  # 当前路径(绝对)
                    path_list = material_data['picture'][i].split('/')
                    path_list[-1] = 'material_%s_%s%s' % (material_id, i, file_extension(material_data['picture'][i]))
                    re_path = '/'.join(path_list)  # 修改路径(相对)
                    # 修改文件命名
                    if exists(cur_path, type='file') and material_data['picture'][i] != re_path:
                        os.rename(cur_path, url_absolute(re_path))
                    # 替换文件路径
                    material_data['picture'][i] = re_path

                material_data['picture'] = json2dict(material_data['picture'])
                msg = self.db.edit('material', material_data, material_id)
                if not msg: return alert(msg='修改失败', act=3)
                else: return alert(act='material_manage')
            else:
                material_data['picture'] = json2dict(material_data['picture'])
                material_data['addtime'] = int(self.kg['run_start_time'][1])
                msg = self.db.add('material', material_data)
                if not msg: return alert(msg='添加失败', act=3)
                else: return alert(act='material_manage')

        else:
            if act == 'edit':
                data = self.db.list(table='material', where=material_id, shift=1)
            else:
                data = {}
            material = {
                'id': data.get('id', 0),
                'name': data.get('name', ''),
                'type': data.get('type', 2),
                'title': json2dict(data.get('title', '[]')),
                'picture': json2dict(data.get('picture', '[]')),
                'key2url': json2dict(data.get('key2url', '[]')),
                'introduction': data.get('introduction', ''),
                'addtime': date(data.get('addtime', int(self.kg['run_start_time'][1])), '%Y-%m-%d %H:%M')
            }
            return template(assign={
                'data': material
            })
