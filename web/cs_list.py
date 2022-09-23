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

        if post_param.get('action', '') == "transfer_customer_service":
            # openid
            openid = self.kg['session'].get('openid', '')
            if not openid: return json2dict({'msg': '请在微信浏览器中选择客服'}, trans=False)

            # 检查粉丝
            fans = self.db.list(table='wx_fans', where='openid = "%s"' % openid)
            if not fans: return json2dict({'msg': '请先关注公众号'}, trans=False)

            # 获取客服
            kf = numeric(post_param.get('id', 0), 0)
            if not kf: return json2dict({'msg': '获取客服id失败，请稍后重试'}, trans=False)
            kf_data = self.db.list(table="cs_account", where=kf, shift=1)
            if not kf_data: return json2dict({'msg': '拉取客服信息失败，请稍后重试'}, trans=False)

            # 会话判断
            current = numeric(int(self.kg['run_start_time'][1]))
            res = wechat.get_session(openid)
            if res.get('errcode', ''): return json2dict({'msg': res['errmsg']}, trans=False)
            cur_kf_account = res.get('kf_account', '')
            if cur_kf_account:
                last = self.db.list(
                    table='cs_transfer',
                    where="kf_account='%s' && openid='%s' && validtime >= %s" % (cur_kf_account, openid, current),
                    order='validtime DESC',
                    shift=1
                )
                if cur_kf_account != kf_data['account'] or not last:
                    # 关闭旧的会话
                    res = wechat.close_session(cur_kf_account, openid)
                    if res.get('errcode', ''): return json2dict({'msg': res['errmsg']}, trans=False)
                    # 建立新会话
                    res = wechat.create_session(kf_data['account'], openid)
                    if res.get('errcode', ''): return json2dict({'msg': res['errmsg']}, trans=False)

            else:
                res = wechat.create_session(kf_data['account'], openid)
                if res.get('errcode', ''): return json2dict({'msg': res['errmsg']}, trans=False)

            # 插入数据并回复欢迎信息
            transfer_data = {
                'openid': openid,
                'kf_account': kf_data['account'],
                'validtime': current + 300,
                'addtime': current
            }

            msg = self.db.add('cs_transfer', transfer_data)
            if not msg: return json2dict({'msg': '记录插入失败'}, trans=False)
            content = "已为您转接了客服 %s(工号：%s) ，请描述您的问题。\r\n\r\n消息转接持续5分钟，如5分钟内没有被接待，您的消息将不再转接到客服系统"
            res = wechat.push_text(openid, content % (kf_data['nickname'], kf_data['kf_id']))
            if res.get('errcode', ''): return json2dict({'msg': res['msg']}, trans=False)
            return json2dict({'status': True}, trans=False)

        else:
            # 获取openid第二步
            if self.kg['get'].get('state', '') == 'getopenid':
                code = self.kg['get'].get('code', '')
                if code:
                    res = wechat.get_openid(code)
                    if res.get('errcode', ''): return alert(msg='获取失败：%s' % res['errmsg'], act=3)
                    self.set_session = {"openid": res['openid'], 'code': code}
                else:
                    return alert(msg='参数错误', act=3)

            # 获取openid第一步
            openid = self.kg['session'].get('openid', '')
            if not openid:
                return alert(act=wechat.get_openid())

            group_id = numeric(self.kg['get'].get('id', 0))
            if not group_id: return alert(act='cs_group')

            group = self.db.list(table='cs_group', where=group_id)
            if not group: return alert(msg='访问无效', act=3)

            cs_list = self.db.list(table='cs_account', where='group_id=%s' % group_id)
            cs_list = wechat.wx_cs_online(cs_list)

            return template(assign={'data': cs_list})
