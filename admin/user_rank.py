# -*- coding:utf-8 -*-
"""网站订单"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import numeric, alert
        get_param = self.kg['get']
        post_param = self.kg['post']
        action = get_param.get('action')
        act_id = numeric(get_param.get('id', 0), 0)

        # 按钮的点击操作
        if action in ['enable', 'unenable', 'auto', 'unauto', 'del'] and act_id:
            if action == "enable": self.db.edit('rank', {'enable': 1}, act_id)
            if action == "unenable": self.db.edit('rank', {'enable': 0}, act_id)
            if action == "auto": self.db.edit('rank', {'auto': 1}, act_id)
            if action == "unauto": self.db.edit('rank', {'auto': 0}, act_id)
            if action == "del":
                user = self.db.list(table='user', where="`level` rlike '[\[|, ]%d[\]|,]'" % act_id)
                if user: return alert(msg='该分组下有会员无法删除', act=3)
                self.db.dele('rank', act_id)
            return alert(act=2)

        # 数据的提交
        if post_param.get('action', '') == 'submit':
            #  UPDATE mytable SET myfield = CASE id WHEN 1 THEN 'value' WHEN 2 THEN 'value' WHEN 3 THEN 'value' END WHERE id IN (1,2,3)
            # rankid, name, discount, scores, money = ([], [], [], [], [])
            rankid = post_param.get('id', '')
            name = post_param.get('title', '')
            discount = post_param.get('discount', '')
            scores = post_param.get('scores', '')
            money = post_param.get('money', '')
            # 没有数据
            if not rankid: return alert(act=2)
            # 单个转列表
            for row in [rankid, name, discount, scores, money]:
                if len(row) == 1: row = [row]

            # 添加与修改
            sql = "UPDATE kg_rank SET rankname = CASE id %s END, discount = CASE id %s END, scores = CASE id %s END, money = CASE id %s END WHERE id IN (%s)"
            title_sql, discount_sql, scores_sql, money_sql = ('', '', '', '')
            add = []
            edit_id = []
            for i in range(len(rankid)):
                if rankid[i] == 'add':
                    add.append({'name': name[i], 'discount': discount[i], 'scores': scores[i], 'money': money[i]})
                else:
                    edit_id.append(rankid[i])
                    title_sql += "WHEN %s THEN '%s' " % (rankid[i], name[i])
                    discount_sql += "WHEN %s THEN %s " % (rankid[i], discount[i])
                    scores_sql += "WHEN %s THEN %s " % (rankid[i], scores[i])
                    money_sql += "WHEN %s THEN %s " % (rankid[i], money[i])
            # 编辑
            if edit_id:
                self.db.run_sql(sql % (title_sql, discount_sql, scores_sql, money_sql, ','.join(edit_id)), 'edit',
                                False)

            # 添加
            sql = 'INSERT INTO `kg_rank`(`webid`, `rankname`, `discount`, `scores`, `money`, `auto`, `enable`) VALUES %s'
            value = []
            for row in add:
                val = '(%s, "%s", %s, %s, %s, %s, %s)'
                val = val % (self.kg['web']['id'], row['name'], row['discount'], row['scores'], row['money'], 0, 1)
                value.append(val)
            if value:
                self.db.run_sql(sql % ','.join(value), 'add', False)
            return alert(act=3)
        # 获取数据
        else:
            data = self.db.list(table='rank', where='webid=%s' % self.kg['web']['id'], order='id ASC')
            return template(assign={'data': data})
