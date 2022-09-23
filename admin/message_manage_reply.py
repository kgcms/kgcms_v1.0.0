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
        from kyger.weixin import Weixin
        wechat = Weixin(self.db, self.kg)
        post_param = self.kg['post']
        get_param = self.kg['get']
        action = post_param.get('action')
        fans_id = numeric(get_param.get('fansid', 0), 0)

        if action == 'text':
            # 获取发送内容
            content = post_param.get('content', '')
            if not content:return alert(msg='请输入内容', act=3)
            # 获取发送的openid
            msgid = numeric(get_param.get('id', 0), 0)
            if not msgid:
                msg = self.db.list(table='wx_fans',field="`openid`", where='`id`=%d' % fans_id, shift=1)
            else:
                msg = self.db.list(table='message', where=msgid, shift=1)
            if not msg:return alert(msg='该用户不存在', act=3)
            # 开始推送

            res = wechat.push_text(msg['openid'], content)
            if res.get('errcode', ''):
                return alert(msg=res['errmsg'], act=3)
            return alert(msg='发送成功', act=2)
        elif action == 'material':
            # 获取素材id
            material = numeric(post_param.get('material', 0), 0)
            if not material:return alert(msg='请选择素材', act=3)
            # 获取发送的openid
            msgid = numeric(get_param.get('id', 0), 0)
            if not msgid:
                msg = self.db.list(table='wx_fans',field="`openid`", where='`id`=%d' % fans_id, shift=1)
            else:
                msg = self.db.list(table='message', where=msgid, shift=1)
            # 开始推送
            res = wechat.push_material(msg['openid'], material)
            if res.get('errcode', ''):

                return alert(msg=res['errmsg'], act=3)
            return alert(msg='发送成功', act=2)

        elif action == 'getcount':
            openid = post_param.get('openid', '')
            count = numeric(post_param.get('count', 0))

            # 判断是否为粉丝
            fans_data = self.db.list(table='wx_fans', where='openid="%s"' % openid)
            if not fans_data: return json2dict({'status': 1, 'msg': '该用户已取消关注'}, trans=False)

            if count != 0:
                last = self.db.list(
                    table='message',
                    where='openid="%s"' % openid,
                    order='addtime ASC',
                    limit='%s,1' % (count-1),
                    shift=1
                )
            else:
                last = {'addtime': 0}
            res = self.db.list(
                table='%smessage as a, %swx_fans as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                field="a.*, b.nickname, b.headimgurl",
                where='a.openid = b.openid && a.openid="%s" && addtime>%s' % (openid, last['addtime']),
                order='addtime DESC'
            )
            # 数据整形
            from urllib.parse import quote, unquote
            for var in res:
                var['nickname'] = unquote(var['nickname'])
                week = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
                var['day'] = week[numeric(date(var['addtime'], '%w'), 0, 6)]
                var['addtime'] = date(var['addtime'], '%Y-%m-%d %H:%M:%S')

            return json2dict({'status': 0, 'new': len(res), 'msg': res}, trans=False)

        else:
            id = numeric(get_param.get('id', 0), 0)
            fans_id = numeric(get_param.get('fansid', 0), 0)
            if id:
                message = self.db.list(table='message', where=id, shift=1)
                if not message: return alert(msg='此条记录不存在', act=3)
                fans = self.db.list(table='wx_fans', where='openid="%s"' % message['openid'], shift=1)
                if not fans: return alert(msg='这位粉丝不存在', act=3)
            elif fans_id:
                fans = self.db.list(table='wx_fans', where=fans_id, shift=1)
                if not fans: return alert(msg='这位粉丝不存在', act=3)
            else:
                return alert(act='message_manage')

            material = self.db.list(table='material', where='type !=1')
            msg_log = self.db.list(
                table='%smessage as a, %swx_fans as b' % (self.db.cfg["prefix"], self.db.cfg["prefix"]),
                field="a.*, b.nickname, b.headimgurl",
                where='a.openid = b.openid && a.openid="%s"' % fans['openid'],
                order='addtime DESC'
            )

            # 数据整形
            from urllib.parse import quote, unquote
            fans['nickname'] = unquote(fans['nickname'])
            for var in msg_log:
                var['nickname'] = unquote(var['nickname'])
                week = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
                var['day'] = week[numeric(date(var['addtime'], '%w'), 0, 6)]
                var['addtime'] = date(var['addtime'], '%Y-%m-%d %H:%M:%S')
            return template(assign={
                'material': material,
                'message': msg_log,
                'id': id,
                'count': len(msg_log),
                'fans': fans
            })
