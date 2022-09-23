# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        import shutil
        from kyger.utility import file_list, json2dict, numeric, url_absolute, alert, get_contents, put_contents, \
            str_replace, exists
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = get_param.get('action', '')

        # 获取语言包路径
        if get_param.get('dir', ''):
            path = 'language/frontend/%s' % get_param.get('dir')
        else:
            path = 'language/frontend/%s' % self.kg['web']['language']

        # 修改数据
        if post_param.get('action', '') == "submit":
            data = str_replace(post_param.get('code', ''), ['\\"', "\\'", '\\\\'], ['"', "'", '\\'])
            put_contents(path + '/%s' % get_param.get('file', 'index.py'), data)
            return alert(act=2)

        # 动作判断
        if action == "copy" and get_param.get('dir', '') and get_param.get('name', ''):  # 复制并创建新语言包
            dir = get_param.get('dir', '')
            name = get_param.get('name', '')
            if not exists(url_absolute("language/frontend/%s" % dir)): return alert(msg="该语言包不存在", act=3)
            # 复制
            shutil.copytree(url_absolute("language/frontend/%s" % dir), url_absolute("language/frontend/%s" % name))
            return alert(act='template_language')
        if action == 'del' and get_param.get('dir', ''):
            dir = get_param.get('dir', '')
            if not exists(url_absolute("language/frontend/%s" % dir)): return alert(msg="该语言包不存在", act=3)
            # 删除
            data = self.db.list(table='web', field='`language`')
            boo = True
            for var in data:
                if var['language'] == dir:
                    boo = False
                    break
            if boo:
                shutil.rmtree(url_absolute('language/frontend/%s' % dir))
                return alert(act='template_language')
            else:
                return alert(msg="该语言包正在使用,无法删除", act=3)
        # 文件列表
        files = []
        file_name = json2dict(file=path + '/file_name.json')  # 文件名对应
        for row in file_list(path, 1, 0, False, '.py'):
            files.append({'name': file_name.get(row, ''), 'file': row})
        # 获取文件内容
        content = get_contents(path + '/%s' % get_param.get('file', 'index.py'), mode='rb')
        # 当前路径
        path_list = path.split('/')
        dir_name = {"file": path_list[len(path_list) - 1]}
        return template(
            assign={
                'list': files,
                'content': content,
                'name': [get_param.get('file', 'index.py'), file_name.get(get_param.get('file', 'index.py'), '')],
                'dir': dir_name,
                'path': path + '/%s' % get_param.get('file', 'index.py'),
                'dirs': file_list('language/frontend', 2, 0)
            }
        )

