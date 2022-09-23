# -*- coding:utf-8 -*-
"""网站文章"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None
    transaction_type = {
        1: "会员在线充值",
        2: "后台手动充值",
        3: "购买商品[消费支付]",
        4: "提交、删除或修改订单",
        5: "购买浏览权限",
        6: "操作日志"
    }

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import date, json2dict
        from kyger.product import Product

        post_param = self.kg['post']
        # 修改头像
        if post_param.get("action",'') == "change_user_image":
            userid = self.kg['user']['id']
            image = post_param.get('image', '')
            if userid and image:
                res = self.db.edit("user",{"image":image},self.kg['user']['id'])
                return json2dict({"errcode": 0, "errmsg": "修改成功!"}, trans=False)
            return json2dict({"errcode":1, "errmsg":"未查询到用户信息或头像url不正确!"}, trans=False)

        # 最近3次交易记录
        data = self.db.list(
            table='transaction',
            field="*, from_unixtime(`addtime`, '%Y-%m-%d %H:%i:%s') as `date`",
            where='uid=%s' % self.kg['user']['id'],
            limit='0,10',
            order='addtime DESC'
        )
        for row in data:
            row['type'] = self.transaction_type[row['type']]
        self.kg['transaction'] = data

        # 最近两次登录的ip和登录时间
        near_time = self.db.list(
            table='log',
            field='addtime',
            where='userid=%s' % self.kg['user']['id'],
            order='addtime DESC',
            limit='0,2'
        )
        # 最近两次登录
        login_list = self.db.list(
            table='log',
            field='ip',
            where='userid=%s group by ip,addtime' % self.kg['user']['id'],
            order='addtime DESC',
            limit='0,2'
        )
        if near_time:
            login_time = [0, 0]
            for i in range(len(near_time)):
                login_time[i] = date(near_time[i]['addtime'], '%Y-%m-%d %H:%M:%S')
            self.kg['user']['logintime'] = login_time
        if login_list:
            login_ip = ['', '']
            for i in range(len(login_list)):
                login_ip[i] = login_list[i]['ip']
            self.kg['user']['loginip'] = login_ip
        return template(function=[{"get_cart": Product(self.db, self.kg).get_cart}])
