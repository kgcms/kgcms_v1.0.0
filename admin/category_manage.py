# -*- coding:utf-8 -*-
"""栏目管理页"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.utility import url_query2dict, numeric, json2dict, alert, url_update, str_cutting, log
        get_param = self.kg['get']  # 获取url参数
        post_param = self.kg['post']  # POST参数

        # 提交排序
        if post_param.get('action') == 'sort':
            sort = post_param.get('sort', [])
            if not sort: return alert(act=3)
            sql = 'UPDATE %scategory SET sort = CASE id ' % self.db.cfg["prefix"]
            id_list = []
            for row in sort:
                sort_data = row.split(',')
                id_list.append(str(numeric(sort_data[0], 0)))
                sql += 'WHEN %s THEN %s ' % (numeric(sort_data[0], 0), numeric(sort_data[1], 0))
            self.db.run_sql(sql + 'END WHERE id IN (%s)' % (','.join(id_list)), log=True)
            # log(self.db, self.kg, 3, {"state": "SUCCESS", "table": "category", "id": '[%s]' % (', '.join(id_list)),
            #                           "edit_count": len(id_list)})
            return alert(act=2)

        # 判断是否删除栏目
        action = get_param.get('action', '')
        if action == 'del':
            del_id = numeric(get_param['id'], 0)  # 获取要删除的栏目id

            # 判断是否可以删除
            del_data = self.db.list(table='category', field='module', where=del_id, shift=1)
            lower = self.lower_category(del_id)  # 获取子级栏目
            if del_data:
                tables = {'photo': 'picture'}
                if del_data['module'] in tables: del_data['module'] = tables[del_data['module']]
                content = self.db.list(
                    table='%s' % del_data['module'],
                    field='category',
                    where="`category` rlike '[\[|, ]%d[\]|,]'" % del_id
                )  # 该模块下的数据
            else:
                content = []

            # 如果该栏目既没有下级栏目也没有文章才删除
            url = url_update(url_query2dict(get_param), deld=['action', 'id'])
            url = '?' + url if url else ''
            if not lower and not content:
                self.db.dele(table='category', where=del_id, limit=1)
                return alert(act=2)
            return alert(msg='该栏目下有子级栏目或内容无法删除', act="./category_manage%s" % url)
        # 设置首页启用
        elif action == "enable" and numeric(get_param.get('id', 0), 0):
            enable_id = numeric(get_param.get('id', 0), 0)
            self.db.edit('category', {'enable': 1}, enable_id)
            return alert(act=2)
        # 取消首页启用
        elif action == "unenable" and numeric(get_param.get('id', 0), 0):
            unenable_id = numeric(get_param.get('id', 0), 0)
            self.db.edit('category', {'enable': 0}, unenable_id)
            return alert(act=2)
        # 设置首页展示
        elif action == "display" and numeric(get_param.get('id', 0), 0):
            display_id = numeric(get_param.get('id', 0), 0)
            self.db.edit('category', {'display': 1}, display_id)
            return alert(act=2)
        # 取消首页展示
        elif action == "undisplay" and numeric(get_param.get('id', 0), 0):
            undisplay_id = numeric(get_param.get('id', 0), 0)
            self.db.edit('category', {'display': 0}, undisplay_id)
            return alert(act=2)
        else:  # 非删除栏目操作
            from kyger.kgcms import template
            cid = numeric(self.kg['get'].get('cid', 0))  # 获取栏目id
            # 获取该栏目的子栏目
            data = self.lower_category(cid)
            # 获取cid的相同上级的同级栏目
            path = []
            if cid:
                cate = self.db.list(table='category', field='level, upper, title, id', where=cid, shift=1)
                where = 'webid=%s && `level` = %d && `upper` like "%s" ' % (self.kg['web']['id'], cate['level'], cate['upper'])  # 拥有相同上级的同级栏目
                category_list = self.db.list(table='category', field='title,id', order='`level` ASC')  # 全部栏目
                cate['upper'] = json2dict(cate['upper'])
                for var in category_list:  # 获取上级栏目用于导航条
                    if var['id'] in cate['upper']: path.append(var)
                path.append(cate)
            else: where = '`level` = 1 && webid = %s' % self.kg['web']['id']  # 为0获取1级栏目
            same_level = self.db.list(table='category', field='title, id, level', where=where)
            if not same_level: same_level = []
            if not (cid and cate['level'] > 1): same_level.insert(0, {"title": "所有栏目", "id": 0})

            # url参数合成
            button_url = url_query2dict(get_param) + '&' if url_query2dict(get_param) else ''
            url = {'button': button_url}
            for var in data:
                var['title'] = str_cutting(var['title'], 21)
            for var in path:
                var['title'] = str_cutting(var['title'], 21)
            for var in same_level:
                var['title'] = str_cutting(var['title'], 21)
            return template(assign={'data': data, 'category': same_level, 'cid': cid, 'url': url, 'path': path})

    def lower_category(self, cid):
        """
        获取该栏目id的下级栏目
        :param cid: [int] 栏目的id，为0时获取1级栏目
        :return: [list] 所有下级栏目的数据
        """
        where = "webid=%s && `upper` rlike '[\[|, ]%d\]'" % (self.kg['web']['id'], cid) if cid else "`level` = 1&& webid = %s" % self.kg['web']['id']
        data = self.db.list(
            table='category',
            field='id,title,level,picture,module,sort,enable, display',
            where=where,
            order='`level` ASC,sort ASC'
        )
        return data

