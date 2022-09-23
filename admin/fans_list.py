# -*- coding:utf-8 -*-
"""网站订单"""

from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
       pass
    
    def __call__(self):
        from urllib.parse import quote, unquote
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 获取参数
        country = get_param.get('country', '')
        province = get_param.get("province", '')
        city = get_param.get("city", '')
        group = int(get_param.get("group", -1))
        source = numeric(get_param.get("source", 0))
        word = get_param.get('word', '')
        page = numeric(get_param.get('page', 1), 1)
        row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
        action = get_param.get('action', '')

        # 同步粉丝
        if action == 'syn':
            # 微信类实例化
            wechat = Weixin(self.db, self.kg)

            # 判断是否已经获取了粉丝列表
            if not exists(url_absolute('temp/fans_list.json'), 'file'):
                # 同步分组
                wechat.syn_groups()
                fans_list_data = wechat.get_fans_list()
                count = fans_list_data.get('count', 0)

                fans_list = {"fans_list": fans_list_data.get('data', {}).get('openid', []), "count": count}
                cycle = (count // 10000) + 1 if count % 10000 else count // 10000
                for i in range(cycle):
                    fans_list_data = wechat.get_fans_list(fans_list_data.get('next_openid', ''))
                    fans_list["fans_list"].extend(fans_list_data.get("data", {}).get('openid', []))
                dict2json_file(fans_list, file='temp/fans_list.json')
                # 清空粉丝表
                self.db.run_sql("TRUNCATE `%swx_fans`" % self.db.cfg["prefix"])

            # 读取文件开始同步粉丝
            data = json2dict(file='temp/fans_list.json')
            fans_index = numeric(get_param.get("index", 0))
            openid = data['fans_list'][fans_index]
            fans_info = wechat.get_fans_info(openid)

            # 保存数据到数据库
            fans_data = {
                "groupid": fans_info.get("groupid", ""),
                "openid": fans_info.get("openid", ""),
                "nickname": quote(fans_info.get("nickname", "")),
                "sex": numeric(fans_info.get("sex", 0)),
                "city": fans_info.get("city", ""),
                "country": fans_info.get("country", ""),
                "province": fans_info.get("province", ""),
                "language": fans_info.get("language", ""),
                "headimgurl": fans_info.get("headimgurl", ""),
                "qrscene": fans_info.get("qr_scene", ""),
                "scenestr": fans_info.get("qr_scene_str", ""),
                "subscribetime": fans_info.get("subscribe_time", "")
            }
            self.db.add('wx_fans', fans_data)

            # 索引值到达最后结束同步并删除文件
            if fans_index + 1 == len(data['fans_list']):
                import os
                os.remove(url_absolute('temp/fans_list.json'))
                end = 1
            else:
                end = 0

            return template(
                assign={"count": data.get('count', 0), "index": fans_index, "fans_info": fans_info, 'end': end},
                tpl='fans_syn.tpl'
            )

        # 移动用户分组
        elif post_param.get("action") == "move":
            wechat = Weixin(self.db, self.kg)
            openid_list = post_param.get('id', [])
            group_id = post_param.get('group_id', -1)
            if group_id == -1:
                return alert(msg="没有选择组", act=3)
            else:
                group_id = numeric(group_id)
            for row in openid_list:
                wechat.move_fans_group(row, group_id)
            self.update_fans_group()
            return alert(act=2)

        # 获取数据
        else:
            # where
            country_sql = " && country = '%s'" % country if country else ''
            province_sql = " && province = '%s'" % province if province else ''
            city_sql = " && city = '%s'" % city if city else ''
            group_sql = " && groupid = %s" % group  if group != -1 else ''
            source_sql = " && qrscene = %s" % source if source else ""
            word_sql = " && nickname like '%%%s%%'" % quote(word) if word else ""
            where = "a.`groupid` = b.`id`%s%s%s%s%s%s" % (group_sql, source_sql, word_sql, country_sql, province_sql, city_sql)

            # 查询数据
            data = self.db.list(
                table="`%swx_fans` a, `%swx_group` b" % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                field="a.*, b.`name` as group_name",
                where=where,
                order="id DESC",
                page=page,
                limit=row
            )
            if page > self.db.total_page:
                page = self.db.total_page
                data = self.db.list(
                    table="`%swx_fans` a, `%swx_group` b" % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                    field="a.*, b.`name` as group_name",
                    where=where,
                    order="id DESC",
                    page=page,
                    limit=row
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            # 分页
            from kyger.common import page_tpl
            page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'))

            # 数据整形
            for var in data:
                var['subscribetime'] = date(var['subscribetime'], '%Y-%m-%d')
                var['nickname'] = unquote(var['nickname'])

            # 关注时期信息
            today = mk_time(date(int(self.kg['run_start_time'][1]), "%Y%m%d"), "%Y%m%d")
            last7days = today - 86400 * 6
            last30days = today - 86400 * 29
            # 总数
            all_count = self.db.list(table="wx_fans", field="count(*)")
            # 今天
            today_count = self.db.list(table="wx_fans", field="count(*)", where="subscribetime > %s" % today)
            # 最近7天
            last7days_count = self.db.list(table="wx_fans", field="count(*)", where="subscribetime > %s" % last7days)
            # 最近30天
            last30days_count = self.db.list(table="wx_fans", field="count(*)", where="subscribetime > %s" % last30days)
            attention = {
                "count": all_count[0]["count(*)"],
                "today": today_count[0]["count(*)"],
                "last7days": last7days_count[0]["count(*)"],
                "last30days": last30days_count[0]["count(*)"]
            }

            # 分组与来源
            wx_group = self.db.list(table="wx_group")
            wx_qrcode = self.db.list(table="wx_qrcode")

            # url参数合成
            group_url = url_update(url_query2dict(get_param), deld='group') + '&' if url_update(url_query2dict(get_param), deld='group') else ''
            source_url = url_update(url_query2dict(get_param), deld='source') + '&' if url_update(url_query2dict(get_param), deld='source') else ''
            url = {
                'group': group_url,
                'source': source_url
            }

            return template(assign={
                "data": data,
                "attention": attention,
                "wx_group": wx_group,
                "wx_qrcode": wx_qrcode,
                "source": source,
                "group": group,
                "word": word,
                "url": url,
                "page_html": page_html,
                'page_data': page_data
            })

    def update_fans_group(self):
        group_list = self.db.list(
            table='wx_fans',
            field="count(*), groupid",
            where='1 group by groupid'
        )
        sql = 'UPDATE %swx_group SET count = CASE id ' % self.db.cfg["prefix"]
        group_id_list = []
        for var in group_list:
            sql += 'WHEN %s THEN %s ' % (var['groupid'], var['count(*)'])
            group_id_list.append(str(var['groupid']))
        self.db.edit('wx_group', {'count': 0})
        self.db.run_sql(sql + 'END WHERE id in (%s)' % ','.join(group_id_list), 'edit')
