# -*- coding:utf-8 -*-
"""流量概况"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        from kyger.kgcms import template, date, mk_time, json2dict
        # 最大日、周、月
        from kyger.access import Access
        Access(self.db, self.kg).upadte()
        access_max = json2dict(file="config/web_statistics.json")
        access_max['max_day']['time'] = date(access_max['max_day']['time'], '%Y年%m月%d日')
        access_max['max_week']['start'] = date(access_max['max_week']['time'], '%Y年%m月%d日')
        access_max['max_week']['end'] = date(access_max['max_week']['time'] + 518400, '%Y年%m月%d日')
        access_max['max_month']['time'] = date(access_max['max_month']['time'], '%Y年%m月')
        # 获取当前默认的站点
        web_data = self.db.list(table='web', field='name, domain', where='`default` = 1', shift=1)
        web_data['domain'] = json2dict(web_data['domain'])

        # 起始日期
        start = self.db.list(table='access', field='addtime', page=1, order='`addtime` ASC', limit=1, shift=1)

        # 总访问量
        all_access = [0, self.db.total_rows]
        all_ip = self.db.list(table='access', field='count(distinct ip)', shift=1)
        all_access[0] = all_ip['count(distinct ip)']

        # 访问量
        time_list = self.get_time()
        access_data = self.db.list(
            table='access',
            field='ip, addtime, aid',
            where='`addtime` > %d' % time_list['up_month'],
            order='`addtime` DESC',
        )
        echarts_day, echarts_week = ([], [])
        today_user, yesterday_user = ([], [])
        day, up_day, week, up_week, month, up_month = ([], [], [], [], [], [])
        for var in access_data:
            if var['addtime'] > time_list['this_day']:
                day.append(var['ip'])  # 今日
                echarts_day.append(var)  # 今日图表
                if var['aid'] not in today_user: today_user.append(var['aid'])  # 获取今日的用户aid
            elif var['addtime'] > time_list['up_day']:
                up_day.append(var['ip'])  # 昨日
                if var['aid'] not in yesterday_user: yesterday_user.append(var['aid'])  # 获取昨天的用户aid
            if var['addtime'] > time_list['this_week']:
                echarts_week.append(var)  # 本周图表
                week.append(var['ip'])  # 本周
            elif var['addtime'] > time_list['up_week']: up_week.append(var['ip'])  # 上周
            if var['addtime'] > time_list['this_month']: month.append(var['ip'])  # 本月
            elif var['addtime'] > time_list['up_month']: up_month.append(var['ip'])  # 上月
        ip = self.db.list(table='access', field='count(distinct ip)', where='`addtime` > %d' % time_list['this_year'], shift=1)
        pv = self.db.list(table='access', field='count(*)', where='`addtime` > %d' % time_list['this_year'],shift=1)
        year = [ip['count(distinct ip)'], pv['count(*)']]  # 今年

        # 今日新老客户量
        old = self.db.list(
            table='access',
            field='count(distinct aid)',
            where='aid in ("%s") && addtime < %d' % ('","'.join(today_user), time_list['this_day']),
            shift=1
        )['count(distinct aid)']
        new = len(today_user) - old

        # 同时在线
        online = self.db.list(table='access', field='addtime, aid', where='`addtime` > %d' % time_list['fifteen'],order='`addtime` DESC',)
        one_online, five_online, fifteen_online = ([], [], [])
        for var in online:
            if var['aid'] not in fifteen_online: fifteen_online.append(var['aid'])
            if var['addtime'] > (time_list['fifteen'] + 600) and var['aid'] not in five_online: five_online.append(var['aid'])
            if var['addtime'] > (time_list['fifteen'] + 840) and var['aid'] not in one_online: one_online.append(var['aid'])

        # 总天数
        time_diff = time_list['this_day'] + 86400 - start['addtime']
        count_day = (time_diff // 86400) + 1 if time_diff % 86400 else time_diff / 86400

        # 今日预测
        predict = list()
        predict.append(int(len(day) / (self.kg['run_start_time'][1] - time_list['this_day']) * 86400))
        predict.append(int(len(today_user) / (self.kg['run_start_time'][1] - time_list['this_day']) * 86400))
        predict.append(int(len(set(day)) / (self.kg['run_start_time'][1] - time_list['this_day']) * 86400))

        # 数据概况
        day_count = self.db.list(table='access', field='count(*)', where='addtime > %d' % time_list['this_day'], shift=1)['count(*)']
        week_count = self.db.list(table='access', field='count(*)', where='addtime > %d' % time_list['this_week'], shift=1)['count(*)']
        # 来源
        day_source = self.max_deal(day_count, 'domain', time_list['this_day'])
        week_source = self.max_deal(week_count, 'domain', time_list['this_week'])
        # 受访
        day_page = self.max_deal(day_count, 'page', time_list['this_day'], ['url'])
        week_page = self.max_deal(week_count, 'page', time_list['this_week'], ['url'])
        # 区域
        day_province = self.max_deal(day_count, 'province', time_list['this_day'])
        week_province = self.max_deal(week_count, 'province', time_list['this_week'])
        analysis = {
            "day": {"source": day_source, 'page': day_page, 'province': day_province},
            "week": {"source": week_source, 'page': week_page, 'province': week_province}
        }

        # 图表
        day_table = [0, 0, 0, 0, 0, 0, 0, 0]
        for var in echarts_day:
            dif_time = var['addtime'] - time_list['this_day']
            day_table[dif_time // 10800] += 1
        day_table.insert(0, 0)
        week_table = [0, 0, 0, 0, 0, 0, 0]
        for var in echarts_week:
            dif_time = var['addtime'] - time_list['this_week']
            week_table[dif_time // 86400] += 1
            print(dif_time // 86400)
        data = {
            "day": [len(set(day)), len(day)],
            "upday": [len(set(up_day)), len(up_day)],
            "week": [len(set(week)), len(week)],
            "upweek": [len(set(up_week)), len(up_week)],
            "month": [len(set(month)), len(month)],
            "upmonth": [len(set(up_month)), len(up_month)],
            "year": year,
            "all": all_access,
            "start": date(start['addtime'], "%Y年%m月%d日"),
            "count_day": count_day,
            'one': len(one_online),
            'five': len(five_online),
            'fifteen': len(fifteen_online),
            'new': new,
            'old': old,
            'yesterday': len(yesterday_user),
            'max': access_max,
            "predict": predict,
            'analysis': analysis,
            'echarts_week': week_table,
            'echarts_day': day_table
        }
        return template(assign={"data": data, "web": web_data, })

    def get_time(self):
        from kyger.kgcms import date, mk_time
        fifteen = int(self.kg['run_start_time'][1]) - 15 * 60
        this_day = mk_time(date(int(self.kg['run_start_time'][1]), '%Y%m%d'), '%Y%m%d')  # 今天
        up_day = mk_time(date(this_day - 86400, "%Y%m%d"), format="%Y%m%d")  # 昨天
        this_month = mk_time(date(this_day, '%Y%m'), format="%Y%m")  # 本月
        up_month = mk_time(date(this_month - 86400, "%Y%m"), format="%Y%m")  # 上月
        this_year = mk_time(date(this_day, "%Y"), format="%Y")  # 今年
        if int(date(this_day, '%w')) == 0:days = 6
        else: days = int(date(this_day, '%w')) - 1
        this_week = this_day - days * 86400  # 本周
        print(this_week)
        up_week = this_week - 7 * 86400  # 上周
        return {
            "this_day": this_day,
            "up_day": up_day,
            "this_month": this_month,
            "up_month": up_month,
            "this_year": this_year,
            "this_week": this_week,
            "up_week": up_week,
            "fifteen": fifteen
        }

    def max_deal(self, count, field, filter_time, extra_field=[]):
        # SELECT DISTINCT source as a, COUNT(*) as b FROM `kg_access` WHERE 1 GROUP by a ORDER by b DESC LIMIT 0,1
        from kyger.utility import url_parse
        extra_field = ',' + ','.join(extra_field) if extra_field else ''
        data = self.db.list(
            table='access',
            field='%s as a, COUNT(*) as b%s' % (field, extra_field),
            where='addtime > %d GROUP by a%s' % (filter_time, extra_field),
            order='b DESC',
        )
        if field == "page":
            is_null, is_index = (0, 0)
            url = ''
            del_index = []
            for row in data:
                if row['a'] == 'index':
                    is_index = row['b']
                    url = row['url']
                    del_index.append(data.index(row))
                if row['a'] == '':
                    is_null = row['b']
                    del_index.append(data.index(row))
            del_index.sort(reverse=True)
            for i in del_index:
                del data[i]
            data.append({'a': 'index', 'b': is_null + is_index, 'url': url})
            data.sort(key=lambda obj: obj.get('b'), reverse=True)
        if field == "province":
            is_null, is_ip = (0, 0)
            del_index = []
            for row in data:
                if row['a'] == '-':
                    is_ip = row['b']
                    del_index.append(data.index(row))
                if row['a'] == '':
                    is_null = row['b']
                    del_index.append(data.index(row))
            del_index.sort(reverse=True)
            for i in del_index:
                del data[i]
            data.append({'a': '未知', 'b': is_null + is_ip})
            data.sort(key=lambda obj: obj.get('b'), reverse=True)
        data = data[0:10]
        for var in data:
            var['rate'] = format(var['b'] / count * 100, '.2f')
            if 'url' in var:
                url_data = url_parse(var['url'], '__ALL__')
                var['url'] = "%s://%s%s" % (url_data['scheme'], url_data['netloc'], url_data['path'],)
        return data



