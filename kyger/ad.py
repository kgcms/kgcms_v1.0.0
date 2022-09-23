# -*- coding:utf-8 -*-
"""广告及焦点图"""


class Advertise(object):
    """广告及焦点图"""
    limit_time = 86400  # 限制一个ip多久再计算一次点击次数（秒）

    # 构造函数
    def __init__(self, db=None, kg=None):
        # 数据库
        from kyger.db import MySQL
        self.db = db if db else MySQL()  # 数据库操作对象
        self.kg = kg  # 全局变量

    def list(self, aid, row=0):
        """
        调用一个或多个广告
        :param aid: [str] 要调用的广告识别码
        :param row: [int] 是否要只调用单个，0调用全部，其他为调用个数
        :return:
        """
        from kyger.utility import json2dict, str_replace
        data = self.db.list(table='ad', where="aid='%s'" % aid)
        for var in data:
            var['picture'] = json2dict(var['picture'])
            var['picurl'] = json2dict(var['picurl'])
            var['summary'] = json2dict(var['summary'])
            var['code_orig'] = var['code']  # 不统计的广告代码
            # 找出链接
            link_list = self.ad_link(var['code'])
            for i in range(len(link_list['list'])):
                if link_list['list'][i].strip():
                    var['code'] = str_replace(var['code'], link_list['list'][i], 'api/unlimited_process?action=ad&id=%s&index=%s' % (var['id'], i))
        data = self.weight_rand(data, row)
        if len(data) == 1: data = data[0]
        return data

    def weight_rand(self, data, row):
        """
        权重处理
        :param data: [str] 要处理的数据
        :param row: [int] 是否要只调用单个，0调用全部，其他为调用个数
        """
        temp_data = []
        weight = 0
        for var in data:
            current_time = int(self.kg['run_start_time'][1])

            # 广告过期
            if var['expir'] == 1 and (var['start'] > current_time or var['end'] < current_time):
                var['code'] = var['expired'] if var['expired'] else 'This Posting Has Expired.'

            weight += var['weight']
            for i in range(var['weight']):
                temp_data.append(var)

        import random
        res = [] if row else data
        for i in range(row):
            rand_num = random.randint(0, weight - 1)
            res.append(temp_data[rand_num])
            tag = temp_data[rand_num]
            weight = weight - tag['weight']
            while tag in temp_data:
                temp_data.remove(tag)

        return res

    @staticmethod
    def ad_link(code):
        from kyger.utility import json2dict, str_replace
        import re
        pattern = re.compile(r'href=[\'"]([\s\S]*?)[\'"]')  # 查找链接
        link_list = pattern.findall(code)
        links = []
        for row in link_list:
            links.append(str_replace(row, ['\n', '\r', '\t', ' '], ''))
        return {
            "list": link_list,  # 正则匹配到的链接
            'link': links  # 过滤掉换行，回车，制表符，空格后的链接
        }


