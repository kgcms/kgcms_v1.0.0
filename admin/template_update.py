# -*- coding:utf-8 -*-
"""编辑模板文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import file_list, json2dict, numeric, url_absolute, alert, get_contents, put_contents, str_replace
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 获取模板路径
        if get_param.get('dir', ''):
            path = 'template/frontend/%s' % get_param.get('dir')
        else:
            if self.kg['web']['template']:
                path = 'template/frontend/%s' % self.kg['web']['template']
            else:
                path = 'template/frontend/%s' % self.kg['web']['template_auto']['pc']

        if post_param.get('action', '') == "submit":
            data = str_replace(post_param.get('code', ''), ['\\"', "\\'", '\\\\'], ['"', "'", '\\'])
            put_contents(path + '/%s' % get_param.get('file', 'index.tpl'), data)
            return alert(act=2)

        # 文件列表
        files = []
        file_name = json2dict(file=path + '/file_name.json')  # 文件名对应
        for row in file_list(path, 1, 0, False, '.tpl'):
            files.append({'name': file_name.get(row, ''), 'file': row})
        # 获取文件内容
        content = get_contents(path + '/%s' % get_param.get('file', 'index.tpl'), mode='rb')
        # 当前路径
        path_list = path.split('/')
        dir_name = {"file": path_list[len(path_list) - 1]}
        # 获取模板
        dir_list = file_list('template/frontend', 2, 0)
        dirs = []
        for row in dir_list:
            config = json2dict(file='template/frontend/%s/config.json' % row)  # 读取配置文件
            dirs.append({"title": config['name'], "dir": row})
            if dir_name['file'] == row: dir_name['title'] = config['name']

        return template(
            assign={
                'list': files,
                'content': content,
                'name': [get_param.get('file', 'index.tpl'), file_name.get(get_param.get('file', 'index.tpl'), '')],
                'dir': dir_name,
                'path': path + '/%s' % get_param.get('file', 'index.tpl'),
                'dirs': dirs
            }
        )
