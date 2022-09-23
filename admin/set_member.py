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
        from kyger.parser_ini import Config
        post_param = self.kg['post']

        if post_param.get('action', '') == 'submit':
            set_user = {
                "allow_reg": (numeric(post_param.get('allow_reg', 0), 0, 1), '允许新用户注册'),
                "register_audit": (numeric(post_param.get('register_audit', 0)), '会员注册验证,0无需验证，1邮件验证，2手工验证'),
                "username_strictly": (numeric(post_param.get('username_strictly', 0), 0, 1), '严格限制注册账号,0不限制，1限制'),
                'disable': (str_replace(html_escape(post_param.get('disable', '')), ['，', '　', ' '], [',', '', '']), '禁止使用的账号'),
                "search_open": (numeric(post_param.get('search_open', 0)), '站内搜索0完全开放，1只允许会员搜索，2禁用搜索功能'),
                "search_fulltext": (numeric(post_param.get('search_fulltext', 0)), '全文搜索0完全开放，1只允许会员搜索，2禁用搜索功能'),
                "search_interval": (numeric(post_param.get('search_interval', 0)), '搜索请求间隔时间，单位：秒'),
                "comment_enabled": (json2dict(post_param.get('comment_enabled', []), trans=False), '评论功能开启'),
                "comment_audit": (numeric(post_param.get('comment_audit', 0), 0, 1), '评论显示模式,0需要管理员审核，1直接显示'),
                "comment_traveler": (numeric(post_param.get('comment_traveler', 0), 0, 1), '游客发表评论,0允许未登录评论，1必须会员登录发表'),
                "comment_interval": (numeric(post_param.get('comment_interval', 0)), '评论时间间隔单位：分钟'),
                "message": (numeric(post_param.get('message', 0)), '在线留言，0完全开放，1只允许会员留言，2关闭留言'),
                "message_interval": (numeric(post_param.get('message_interval', 0)), '留言时间间隔单位：分钟'),
                "feedback": (numeric(post_param.get('feedback', 0)), '在线反馈，0完全开放，1只允许会员留言，2关闭留言'),
                "feedback_interval": (numeric(post_param.get('feedback_interval', 0)), '反馈时间间隔单位：分钟'),
                "allow_exchange": (numeric(post_param.get('allow_exchange', 0), 0, 1), '金钱段欢积分，0关闭，1开启'),
                "register_scores": (numeric(post_param.get('register_scores', 0)), '会员注册默认积分'),
                "ratio_scores": (numeric(post_param.get('ratio_scores', 0)), '金钱与积分兑换比例'),
                "login_scores": (numeric(post_param.get('login_scores', 0)), '登录增加积分'),
                "comment_scores": (numeric(post_param.get('comment_scores', 0)), '评论增加积分')
            }
            Config('config/settings.ini').set('user', set_user)
            return alert(act=2)
        else:
            data = Config('config/settings.ini').get('user')
            data['comment_enabled'] = json2dict(data['comment_enabled'])
            return template(assign={'data': data})
