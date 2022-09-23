# -*- coding:utf-8 -*-
"""网站导航"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        self.__page_list = {
            "/article?cid=": "article_list",
            "/article?id=": "article_view",
            "/product?cid=": "product_list",
            "/product?id=": "product_view",
            "/photo?cid=": "photo_list",
            "/photo?id=": "photo_view",
            "customize": "customize",
            "index": "index"
        }

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, numeric, html_escape, alert, str_random, url_absolute, file_mime_type, exists
        from kyger.upload import Upload
        get_param = self.kg['get']
        post_param = self.kg['post']

        action = post_param.get('action', '')
        navid = numeric(get_param.get('navid', 0), 0)
        if action == "submit":
            value = []
            if post_param.get('title'):
                for i in range(len(post_param.get('title'))):
                    if not post_param['title'][i]:return alert(msg="标题不可为空", act=3)
                    if post_param['page'][i] == '0': return alert(msg="链接类型不可为空", act=3)
                    page = self.__page_list.get(post_param['page'][i], '')  # 页面
                    mid = 0 if page in ['customize', 'index'] else numeric(post_param['mid'][i], 0)  # mid
                    # logo
                    image = post_param['img'][i]
                    if image:
                        upload = Upload(image, self.db, self.kg, base64=True)
                        upload.path = 0  # 文件存放路径
                        upload.filename = '%s_%s' % (navid, i)  # 文件命名规则
                        upload.exist_rename = False
                        msg = upload.image('system/navigation')  # 上传到
                        logo = msg['url']
                    else: logo = ''
                    var = '(%s,"%s","%s",%s,"%s","%s",%s,%s,%s,%s,%s,"%s")' % (
                        self.kg['web']['id'],
                        post_param['title'][i],
                        page,
                        mid,
                        post_param['url'][i],
                        logo,
                        numeric(post_param['sort'][i], 0),
                        numeric(post_param['target'][i], 0, 1),
                        numeric(post_param['enable'][i], 0, 1),
                        navid,
                        int(self.kg['run_start_time'][1]),
                        post_param['description'][i]
                    )
                    value.append(var)
            if value:
                sql = 'INSERT INTO `%slink`(`webid`, `name`, `page`, `mid`, `url`, `logo`, `sort`, `target`, `enable`, `nid`, `addtime`, `description`) VALUES %s;' % (self.db.cfg["prefix"], ','.join(value))
                self.db.run_sql('DELETE FROM `%slink` WHERE nid = %s;' % (self.db.cfg["prefix"], navid), None, log=False)
                msg = self.db.run_sql(sql, 'add', log=True)
                if msg: return alert(act=2)
                else: return alert(msg="修改失败", act=3)
            else:
                msg = self.db.dele('link', 'nid = %s' % navid)
                if msg: return alert(act=2)
                else: return alert("删除失败", act=3)

        else:
            import base64
            if not self.db.list(table='navigation', where='id = %d' % navid):
                return alert(msg="该导航不存在", act=3)
            data = self.db.list(table='link', where='nid = %d' % navid, order='sort ASC')
            for row in data:
                path = url_absolute(row['logo'][1:])
                if exists(path, type='file'):
                    with open(r'%s' % path, "rb") as f:
                        base64_data = base64.b64encode(f.read())
                    mime = file_mime_type(row['logo'])
                    row['logo_data'] = "data:%s;base64,%s" % (mime, str(base64_data)[2: -1])
                else:row['logo_data'] = ''
            return template(
                assign={
                    'data': data,
                    'list': self.db.list(table='category', field='id,title', where='module = "article"'),
                    'view': self.db.list(table='article', field='id,title', limit='0, 10'),
                    'category': self.db.list(table='category', field='id,title', where='module = "product"'),
                    'detail': self.db.list(table='product', field='id,title'),
                    'slide': self.db.list(table='category', field='id,title', where='module = "picture"'),
                    'show': self.db.list(table='picture', field='id,title'),
                }
            )
