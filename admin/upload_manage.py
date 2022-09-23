# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        self.__filetype = {
            'application': 'xxx',  # 压缩文件
            'image': 'xxx',  # 图片文件


        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, exists, file_list, alert, file_mime_type, json2dict, date, url_absolute, str_replace, cipher
        from kyger.common import page_tpl
        import os

        get_param = self.kg['get']
        post_param = self.kg['post']

        if get_param.get('action', '') == 'del' and not post_param.get('dir', []) and get_param.get('dir', '') :  # 单项删除
            dir = str_replace(get_param.get('dir'), ['"', "'", "\\", "/", "..", " "], '').split('|')
            path = 'upload/%s' % '/'.join(dir)
            if not os.path.exists(url_absolute(path)): return alert(msg="该文件或目录不存在", act=3)
            if os.path.isfile(url_absolute(path)):  # 如果是文件直接删除
                os.remove(url_absolute(path))
            if os.path.isdir(url_absolute(path)):  # 如果是路径先判断文件夹下是否有文件
                if not file_list(path, 0, 0):
                    os.rmdir(url_absolute(path))
                else: return alert(msg="该文件夹下存在文件或文件夹无法删除", act=3)
            return alert(act=2)

        if post_param.get('action', '') == "del":  # 全选删除操作
            dirs = post_param.get('dir', [])
            if isinstance(dirs, str): dirs = [dirs]
            for var in dirs:  # 循环获取要删除的路径
                var = 'upload/' + str_replace(var, ['"', "'", "\\", "/", "..", " ", '|'], ['', '', '', '', '', '', '/'])
                var = url_absolute(var)
                if exists(var):  # 判断路径是否存在
                    if os.path.isdir(var):  # 判断是否为目录
                        if not len(file_list(var)):
                            os.removedirs(var)
                        else: return alert(msg="%s下存在目录或文件无法删除" % var, act=3)
                    else: os.remove(var)  # 文件直接删除
            return alert(act=2)
        else:
            action = get_param.get('action', '')
            path = get_param.get('dir', '')
            path = str_replace(path, ['"', "'", "\\", "/", ".", " "], '').split('|')
            if get_param.get('dir', ''):
                spell_path = 'upload/'
                for var in path:
                    if var in file_list(spell_path, 2, 0):spell_path += var + '/'
                    else: return alert(act="upload_manage")
            path = 'upload/' + '/'.join(path)
            if path:
                dirs = file_list(path, 0, 1)
                page = numeric(get_param.get('page', 1))
                # 分页处理
                rows = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 30))
                total_page = len(dirs) // rows + 1 if len(dirs) % rows else len(dirs) // rows
                if page > total_page: page = total_page
                pagehtml = page_tpl(page, total_page, rows, self.kg['server'].get('WEB_URL'))
                page_data = {'page': page, 'total_page': total_page, 'total_rows': len(dirs)}
            else:
                pagehtml = ''
                dirs = file_list('upload', 2, 1)  # 获取一级目录
                page_data = {'page': 1, 'total_page': 1, 'total_rows': 0}

            # 数据处理
            data = []
            name_list = json2dict(file="config/update_dir.json")
            for row in dirs:
                path_list = row.split('/')
                if get_param.get('dir', ''):name = path_list[len(path_list) - 1]
                else:name = name_list.get(path_list[len(path_list) - 1], path_list[len(path_list) - 1])
                var = {
                    "path": '|'.join(path_list[1::1]),
                    "name": name,
                    'addtime': date(os.path.getctime(url_absolute(row)), '%Y-%m-%d %H:%M:%S')
                }
                if os.path.isfile(url_absolute(row)):
                    size = numeric(os.path.getsize(url_absolute(row))) / 1024
                    size = ("%s KB" % round(size, 2)) if size < 1024 else ("%s MB" % round(size / 1024, 2))
                    # 文件logo
                    file_type = file_list('template/backend/' + self.kg['globals']['admin_template'] + '/images/filetype', 1, 0)
                    files = row.split('.')
                    if len(files) < 2: logo = 'unknown.png'
                    elif files[-1] + '.png' in file_type: logo = files[-1] + '.png'
                    else: logo = 'unknown.png'
                    # 文件类型
                    type = 'image' if file_mime_type(row) and file_mime_type(row).split('/')[0] == 'image' else 'file'
                    code = cipher(row, 1, 300),  # 下载链接有效期 300 秒,
                    var.update({
                        "type": type,  # 图片、文件、目录
                        "size": size,
                        'logo': 'images/filetype/' + logo,
                        "code": code[0]
                    })
                    data.append(var)  # 文件末尾追加
                else:
                    var.update({"type": "dir", "size": "--", 'logo': 'images/filetype/dir.png'})
                    data.insert(0, var)  # 路径插入
            sorted(data, key=lambda data: data['addtime'], reverse=True)
            if path: data = data[(page - 1) * rows: page * rows]
            if get_param.get('dir', ''): path_list = get_param.get('dir', '').split('|')
            else: path_list = []
            res = []
            for i in range(len(path_list)):
                res.append({'url': '|'.join(path_list[0:i + 1]), 'name': path_list[i]})
            return template(assign={'list': data, 'pagehtml': pagehtml, 'path': res, 'page_data': page_data})




