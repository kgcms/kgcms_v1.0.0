# -*- coding:utf-8 -*-
"""网站导航"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, numeric, html_escape, alert, is_format
        from kyger.upload import Upload
        post_param = self.kg['post']
        get_param = self.kg['get']

        if get_param.get('action', '') == 'del'and get_param.get('id', 0):
            del_id = numeric(get_param.get('id'), 0)
            res = self.db.list(table='link', field='id', where='`nid` = %d' % del_id)
            if res: return alert(msg="改导航下存在菜单不可删除", act=3)
            else:
                res = self.db.dele('navigation', del_id, limit=1, log=True)
                if res: return alert(msg="删除成功", act='navig_manage')
                else: return alert(msg="删除失败", act=3)

        # 动作判断
        act = 'edit' if post_param.get('nav_id', '') else 'add'
        # 提交判断
        if post_param.get('action') == 'submit':
            if not post_param.get('title', ''): return alert(msg='标题不能为空', act=3)
            img = post_param.get('img')
            if act == 'add':
                next_id = self.db.run_sql('SHOW TABLE STATUS WHERE Name = "%snavigation"' % self.db.cfg["prefix"], log=False)[0]['Auto_increment']
                name = 'logo_%d' % next_id
            else: name = 'logo_%d' % numeric(post_param.get('nav_id', 0), 0)
            aid = html_escape(post_param.get('aid', ''))
            if len(aid) > 8 or (not aid[0].isalpha()): return alert(msg="识别码必须字母开头的0-8个字符，允许字母数字下划线", act=3)
            insert_data = {
                "title": html_escape(post_param.get('title', '')),
                "aid": aid,
            }
            if not insert_data['title']: return alert(msg="请输入标题", act=3)
            if img:
                img = img[2:-2:1]
                up = Upload(img, self.db, self.kg, base64=True)
                up.path = 0  # 设置不创建路径
                up.filename = name   # 设置文件名形式
                up.exist_rename = False
                msg = up.image('system/navigation')  # 保存文件
                insert_data['logo'] = msg['url']
            if act == 'edit':
                self.db.edit('navigation', insert_data, where=numeric(post_param.get('nav_id', 0), 0), limit=1)
                return alert(msg="修改成功", act='navig_manage')
            else:
                insert_data['sort'] = 100
                insert_data['webid'] = numeric(self.kg['web']['id'], 0)
                insert_data['addtime'] = int(self.kg['run_start_time'][1])
                row = self.db.add('navigation', insert_data)
                if row: return alert(msg="添加成功", act='navig_manage')
                else: return alert(msg="添加失败", act=3)

        elif post_param.get('action') == 'sort':
            sort_list = post_param.get('sort')
            sql = 'UPDATE %snavigation SET sort = CASE id ' % self.db.cfg["prefix"]
            id_list = []
            for row in sort_list:
                sort_data = row.split(',')
                id_list.append(str(numeric(sort_data[0], 0)))
                sql += 'WHEN %s THEN %s ' % (numeric(sort_data[0], 0), numeric(sort_data[1], 0))
            self.db.run_sql(sql + 'END WHERE id IN (%s)' % (','.join(id_list)), log=True)
            return alert(act=2)

        else:
            data = self.db.list(table='navigation', where="webid=%s" % self.kg['web']['id'], order='`sort` ASC')
            link_data = self.db.list(table='link', field='nid')
            link_list = []
            for row in link_data:
                link_list.append(row['nid'])
            for var in data:
                var['addtime'] = date(var['addtime'], '%Y-%m-%d %H:%M')
                var['menu'] = link_list.count(var['id'])
            return template(assign={'data': data})
