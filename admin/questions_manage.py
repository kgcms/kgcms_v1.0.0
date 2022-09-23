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
        get_param = self.kg['get']
        post_param = self.kg['post']
        get_act = get_param.get('action', '')
        post_act = post_param.get('action', '')

        act_list = ['del', 'enable', 'unenable', 'widely', 'accurate']
        if get_act in act_list or post_act in act_list:
            get_id = numeric(get_param.get('id', ''))
            post_id = post_param.get('id', [])
            if get_id: post_id.append(str(get_id))
            # 行为判断
            if post_id:
                if get_act == 'del' or post_act == 'del':
                    self.db.dele('wx_questions', 'id in (%s)' % ','.join(post_id))
                if get_act == 'enable' or post_act == 'enable':
                    self.db.edit('wx_questions', {'enable': 1}, 'id in (%s)' % ','.join(post_id))
                if get_act == 'unenable' or post_act == 'unenable':
                    self.db.edit('wx_questions', {'enable': 0}, 'id in (%s)' % ','.join(post_id))
                if get_act == 'widely' or post_act == 'widely':
                    self.db.edit('wx_questions', {'rule': 0}, 'id in (%s)' % ','.join(post_id))
                if get_act == 'accurate' or post_act == 'accurate':
                    self.db.edit('wx_questions', {'rule': 1}, 'id in (%s)' % ','.join(post_id))
            return alert(act='questions_manage')

        # 上传
        elif post_act == 'up_csv':
            from kyger.upload import Upload
            file = post_param.get('csv', {'data': ''})
            msg = Upload(file, self.db, self.kg).file('other')
            if msg.get('state', '') != 'SUCCESS': return alert(msg=msg['msg'], act=3)
            if file_extension(msg['url']) != '.csv': return alert(msg="文件格式要求为csv", act=2)

            # 读取csv文件 ask,type,mid,answer,rule,enable
            from kyger.common import csv_read
            csv_data = csv_read(msg['url'])
            sql = "INSERT INTO `kg_wx_questions`(`ask`, `type`, `mid`, `answer`, `rule`, `enable`, `addtime`) VALUES "
            values = []
            for row in csv_data['rows']:
                ask = json2dict(row[0].split('|'))
                type = numeric(row[1], 0, 2)
                rule = numeric(row[4], 0, 1)
                enable = numeric(row[5], 0, 1)
                addtime = int(self.kg['run_start_time'][1])
                values.append('("%s", %s, %s, "%s", %s, %s, %s)' % (ask, type, row[2], row[3], rule, enable, addtime))
            sql_msg = self.db.run_sql(sql + ','.join(values), act="add")
            # 删除文件
            import os
            os.remove(url_absolute(msg['url']))
            if sql_msg: return alert(msg="导入成功", act='questions_manage')
            else: return alert(msg="导入失败", act=3)

        # 下载
        elif get_act == 'down_csv':
            from kyger.common import csv_write
            data = self.db.list(table='wx_questions')
            headers = ["关键字多个用|隔开", "回复模式", "答案素材ID", "答案内容", "匹配规则", "是否启用"]
            rows = []
            for row in data:
                ask = '|'.join(json2dict(row['ask']))
                rows.append((ask, row['type'], row['mid'], row['answer'], row['rule'], row['enable']))
            csv_write("temp/questions.csv", headers, rows)
            code = cipher(url_absolute("temp/questions.csv"), 1, 3600)
            file_name = "questions_%s.csv" % date(int(self.kg['run_start_time'][1]), '%Y%m%d%H%M%S')
            return alert(act="../api/admin_process?action=download&name=%s&code=%s" % (file_name, code))

        # 获取数据
        else:
            # 参数
            rule = numeric(get_param.get('rule', 0), 0, 2)
            sort = numeric(get_param.get('sort', 0), 0, 1)
            word = get_param.get('word', '')
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
            page = numeric(get_param.get('page', 1), 1)

            # where
            if rule == 1: rule_sql = ' && rule = 0'
            elif rule == 2: rule_sql = ' && rule = 1'
            else: rule_sql = ''
            word_sql = ' && ask like "%%%s%%"' % word if word else ''
            where = "1%s%s" % (rule_sql, word_sql)

            # oder
            sort_list = ["addtime DESC", "addtime ASC"]

            # 查询数据库
            data = self.db.list(
                table="wx_questions",
                where=where,
                order=sort_list[sort],
                page=page,
                limit=row
            )
            if page > self.db.total_page:
                page = self.db.total_page
                data = self.db.list(
                    table="wx_questions",
                    where=where,
                    order=sort_list[sort],
                    page=page,
                    limit=row
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            # 分页
            from kyger.common import page_tpl
            page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'))

            # url参数合成
            rule_url = url_update(url_query2dict(get_param), deld='rule') + '&' if url_update(url_query2dict(get_param), deld='rule') else ''
            sort_url = url_update(url_query2dict(get_param), deld='sort') + '&' if url_update(url_query2dict(get_param), deld='sort') else ''
            url = {
                'rule': rule_url,
                'sort': sort_url
            }

            # 微信素材和本地素材id列表,

            mid_list = []
            for var in data:
                if var['mid'] and var['mid'] not in mid_list:
                    mid_list.append(var['mid'])
                var['ask'] = json2dict(var['ask'])
                var['addtime'] = date(var['addtime'], '%Y-%m-%d')
            if mid_list:
                # 微信
                wx_material_dict = {}
                wx_material = self.db.list(
                    table="wx_material",
                    field="id, name",
                    where="id in (%s)" % ','.join("%s" %v for v in mid_list),#str(tuple(mid_list))
                )
                for var in wx_material:
                    wx_material_dict[var['id']] = var['name']
                # 本地
                local_material_dict = {}
                local_material = self.db.list(
                    table="material",
                    field="id, name",
                     where="id in (%s)" % ','.join("%s" %v for v in mid_list),#str(tuple(mid_list))
                )
                for var in local_material:
                    local_material_dict[var['id']] = var['name']
                # 添加素材名
                for var in data:
                    if var['type'] == 0:
                        var['material'] = local_material_dict[var['mid']]
                    elif var['type'] == 1:
                        var['material'] = wx_material_dict[var['mid']]
                    else:
                        var['material'] = ''

            return template(assign={
                "data": data,
                "page_html": page_html,
                "word": word,
                "url": url,
                "rule": rule,
                "sort": sort,
                'page_data': page_data
            })
