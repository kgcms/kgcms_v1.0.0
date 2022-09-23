# -*- coding:utf-8 -*-
"""网站订单"""
from kyger.utility import *


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        self.special = {
            "general": ['1', '98'],
            "administrator": ['98', '99'],
            "push": ['98', '99']
        }
        self.type = {
            0: '事件及日志',
            1: '文本消息',
            2: '图片消息',
            3: '语音消息',
            4: '视频消息',
            5: '位置信息',
            6: '链接消息',
            7: '签到成功',
            8: '签到失败',
            9: '现场抽奖',
            10: '对对碰',
            11: '摇一摇',
            12: '竞拍记录',
            98: '管理员',
            99: '管理员'
        }

    def __call__(self):
        from kyger.kgcms import template
        get_param = self.kg['get']
        post_param = self.kg['post']
        if post_param.get('action', ''):
            action = post_param.get('action', '')
        elif get_param.get('action', ''):
            action = get_param.get('action', '')
        else:
            action = ''

        if action in ['audit', 'recom', 'del', 'unaudit', 'unrecom']:
            get_id = get_param.get('id', '')
            post_id = post_param.get('id', '')
            if get_id: id_list = [get_id]
            else:id_list = post_id
            if not id_list: return alert(msg="没有选择消息", act=3)
            if action == 'audit':
                self.db.edit('message', {'audit': 1}, 'id in (%s)' % ','.join(id_list))
            elif action == 'unaudit':
                self.db.edit('message', {'audit': 0}, 'id in (%s)' % ','.join(id_list))
            elif action == 'recom':
                self.db.edit('message', {'recom': 1}, 'id in (%s)' % ','.join(id_list))
            elif action == 'recom':
                self.db.edit('message', {'recom': 0}, 'id in (%s)' % ','.join(id_list))
            elif action == 'del':
                self.db.dele('message', 'id in (%s)' % ','.join(id_list))
            else:
                return alert(msg='参数错误', act=3)
            return alert(act=2)

        elif self.kg['post'].get('action', '') == "getcount":
            count = numeric(self.kg['post'].get('count', 0))
            res = self.db.run_sql('select count(*) from %smessage' % self.db.cfg["prefix"], 'list', log=False)
            new = res[0]['count(*)'] - count
            return json2dict({'new': new}, trans=False)

        else:
            from urllib.parse import quote, unquote
            page = numeric(get_param.get('page', 1), 1)
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
            type = get_param.get('type', '')
            type = [type] if type.isdigit() else self.special.get(type, [])
            time = numeric(get_param.get('time', 0), 0, 4)
            activity = numeric(get_param.get('activity', 0))
            word = get_param.get('word', '')
            fans_id = numeric(get_param.get('fansid', 0), 0)
            message_id = numeric(get_param.get('message', 0), 0)
            message_data = self.db.list(table='message', where='id=%s' % message_id, shift=1)
            message_sql = '&& a.openid="%s"' % message_data['openid'] if message_data else ''


            # where
            current = int(self.kg['run_start_time'][1])
            today = mk_time(date(current, '%Y%m%d'), '%Y%m%d')
            time_list = [today, today - 86400 * 2, today - 86400 * 6, today - 86400 * 29]
            time_sql = '&& a.addtime > %s' % time_list[time - 1] if time else ''
            type_sql = '&& a.type in (%s)' % ','.join(type) if type else ''
            activity_sql = '&& a.actid=%s' % activity if activity else ''
            word_sql = '&& (b.nickname like "%%%s%%" or a.content like "%%%s%%")' % (quote(word), word) if word else ''
            if fans_id:
                res = self.db.list(table='wx_fans', where=fans_id, shift=1)
                fans_sql = '&& a.openid="%s"' % res['openid'] if res else ''
            else:
                fans_sql = ''

            where = ' %s%s%s%s%s%s' % (time_sql, type_sql, activity_sql, word_sql, fans_sql, message_sql)

            msg = self.db.list(
                table='%smessage as a, %swx_fans as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                field="a.*, b.nickname, b.headimgurl",
                where='a.openid = b.openid' + where,
                page=page,
                limit=row,
                order='addtime DESC'
            )
            if page > self.db.total_page:
                page = self.db.total_page
                msg = self.db.list(
                    table='%smessage as a, %swx_fans as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                    field="a.*, b.nickname, b.headimgurl",
                    where='a.openid = b.openid' + where,
                    page=page,
                    limit=row,
                    order='addtime DESC'
                )
            count = self.db.run_sql('select count(*) from %smessage' % self.db.cfg["prefix"], 'list', log=False)[0]['count(*)']

            # 分页
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            from kyger.common import page_tpl
            page_html = page_tpl(page, self.db.total_page, row, self.kg['server']['WEB_URL'])

            # 数据整形
            from urllib.parse import quote, unquote
            for var in msg:
                var['nickname'] = unquote(var['nickname'])
                var['addtime'] = date(var['addtime'], '%Y-%m-%d %H:%M:%S')
                var['type_msg'] = self.type[var['type']]

            # url参数合成
            type_url = url_update(url_query2dict(get_param), deld='type') + '&' if url_update(url_query2dict(get_param), deld='type') else ''
            time_url = url_update(url_query2dict(get_param), deld='time') + '&' if url_update(url_query2dict(get_param), deld='time') else ''
            activity_url = url_update(url_query2dict(get_param), deld='activity') + '&' if url_update(url_query2dict(get_param), deld='activity') else ''
            url = {
                'type': type_url,
                'time': time_url,
                'activity': activity_url
            }

            # 活动
            activity_list = self.db.list(table='activity')
            return template(assign={
                'data': msg,
                'url': url,
                'page_html': page_html,
                'word': word,
                'type': get_param.get('type', ''),
                'time': time,
                'activity_list': activity_list,
                'activity': activity,
                'count': count,
                'page_data': page_data
            })
