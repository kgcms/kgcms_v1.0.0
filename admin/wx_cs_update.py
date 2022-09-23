# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *



class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        # 长度检测字段和返回提示
        self.long_check = {
            'nickname': [32, "客服昵称长度不允许超过32个字符"],
            'invite_wx': [32, "邀请微信客服长度不允许超过32个字符"]
        }
        # 必填检测
        self.must_input = {
            'nickname': '客服昵称'
        }
    
    def __call__(self):
        from kyger.kgcms import template
        post_param = self.kg['post']
        get_param = self.kg['get']
        cs_id = numeric(get_param.get('id', 0), 0)
        act = 'edit' if cs_id else 'add'

        if post_param.get('action', '') == 'submit':
            from kyger.weixin import Weixin
            wechat = Weixin(self.db, self.kg)
            kf_account = post_param.get('wxname', '')
            nickname = post_param.get('nickname', '')
            headingurl = post_param.get('picture', '')
            if not all((nickname, headingurl)):
                return alert(msg="昵称和头像必须填写", act=3)

            if act == 'edit':
                account = self.db.list(table='cs_account', where=cs_id, shift=1)
                if kf_account and not account['kf_wx']:
                    # 邀请
                    res = wechat.wx_cs_invite(account['account'], kf_account)
                    if res.get('errcode', ''):
                        # dict2json_file({"res": res}, file=("temp/test/errmsg.json"))
                        return alert(msg='邀请失败：%s' % res['errmsg'], act=3)
                    self.db.edit('cs_account', {'kf_wx': kf_account}, cs_id)
                if account['headingurl'] != headingurl:
                    # 修改头像
                    res = wechat.wx_cs_headimg(account['account'], headingurl)
                    if res.get('errcode', ''): return alert(msg='修改头像失败: %s' % res['errmsg'], act=3)
                    self.db.edit('cs_account', {'headingurl': headingurl}, cs_id)
                if nickname != account['nickname']:
                    # 修改昵称
                    res = wechat.wx_cs_update(account['account'], nickname)
                    if res.get('errcode', ''): return alert(msg='修改昵称失败:%s' % res['errmsg'], act=3)
                    self.db.edit('cs_account', {'nickname': nickname}, cs_id)
                self.db.edit('cs_account', {'group_id': numeric(post_param.get('group', 0), 0)}, cs_id)
                return alert(act='wx_cs_manage')

            else:
                # 获取配置文件拼接账号
                from kyger.parser_ini import Config
                weixin_ini = Config('/config/settings.ini').get('weixin')  # 读取配置文件
                sql = "SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA. TABLES WHERE TABLE_NAME = '%scs_account'"
                auto_id = self.db.run_sql(sql % self.db.cfg["prefix"], 'list', log=False)[0]['AUTO_INCREMENT']
                wx_accoount = 'kgcms%s@%s' % (auto_id, weixin_ini['number'])

                # 添加
                res = wechat.wx_cs_add(wx_accoount, nickname)
                if res.get('errcode', ''): return alert(msg='添加失败：%s' % res['errmsg'], act=3)
                # 修改头像
                res = wechat.wx_cs_headimg(wx_accoount, headingurl)
                if res.get('errcode', ''): return alert(msg='修改头像失败：%s' % res['errmsg'], act=3)
                if kf_account:
                    # 邀请
                    res = wechat.wx_cs_invite(wx_accoount, kf_account)
                    if res.get('errcode', ''): return alert(msg='邀请失败：%s' % res['errmsg'], act=3)

                data = {
                    'group_id': numeric(post_param.get('group', 0), 0),
                    'kf_id': 0,
                    'account': wx_accoount,
                    'nickname': nickname,
                    'headingurl': headingurl,
                    'kf_wx': '',
                    'invite_wx': kf_account,
                    'invite_expire_time': int(self.kg['run_start_time'][1]) + 86400,
                    'invite_status': 'waiting',
                    'addtime': int(self.kg['run_start_time'][1])
                }
                # 数据库字段长度检测
                for field in self.long_check:
                    if len(data[field]) > self.long_check[field][0]: return alert(msg=self.long_check[field][1], act=3)
                for field in self.must_input:
                    if len(data[field]) == 0: return alert(msg="%s必须填写" % self.must_input[field], act=3)
                self.db.add('cs_account', data)
                return alert(act='wx_cs_update')

        else:
            # 获取分组
            cs_group = self.db.list(table='cs_group')

            # 获取数据
            if act == 'edit':
                cs_account = self.db.list(table='cs_account', where=cs_id, shift=1)
            else:
                cs_account = {}
            data = {
                'id': cs_account.get('id', ''),
                'group_id': cs_account.get('group_id', 0),
                'kf_id': cs_account.get('kf_id', 0),
                'account': cs_account.get('account', ''),
                'nickname': cs_account.get('nickname', ''),
                'headingurl': cs_account.get('headingurl', ''),
                'kf_wx': cs_account.get('kf_wx', ''),
                'invite_wx': cs_account.get('invite_wx', ''),
                'invite_expire_time': cs_account.get('invite_expire_time', 0),
                'invite_status': cs_account.get('invite_status', ''),
                'addtime': cs_account.get('addtime', '')
            }

            return template(assign={
                'cs_group': cs_group,
                'data': data
            })
