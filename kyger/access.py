# -*- coding:utf-8 -*-
"""流量统计"""

from kyger.utility import numeric, mk_time, date, dict2json_file, json2dict


class Access(object):
    """流量统计调用"""
    __page = 0  # 当前页
    __total_page = 0  # 总页数
    __total_rows = 0  # 总记录数
    __group_rows = 0  # 分组情况下的总记录数

    # 构造函数
    def __init__(self, db=None, kg=None):
        # 数据库
        from kyger.db import MySQL
        self.db = db if db else MySQL()  # 数据库操作对象
        self.kg = kg  # 全局变量
        self.__limit = ''

    def list_page(self, *args, **kwargs):
        """
        分页获取流量信息，参数同list。
        :return:{
            'list':          # 分页的当前页流量数据
            'page_html':     # 分页的html模板
            'page_data':     # 分页的数据：当前页、总页数、总记录数
        }
        """
        self.__page = numeric(self.kg['get'].get('page', 1), 1)  # 当前页
        if 'row' in kwargs: row = kwargs['row']  # 在kwargs里
        elif len(args) > 0: row = args[0]  # 在args里
        else: row = 10  # 默认10

        # 获取数据
        data = self.list(*args, **kwargs)
        # 分页模板合成
        web_url = self.kg['server'].get('WEB_URL')
        from kyger.common import page_tpl
        page_html = page_tpl(self.__page, self.__total_page, row, web_url)  # 获取分页模板
        self.__total_rows = self.db.total_rows  # 总记录数
        self.__total_page = self.db.total_page  # 总页数
        return {
            'list': data,
            'page_html': page_html,
            'page_data': {'page': self.__page, 'total_page': self.__total_page, 'total_rows': self.__total_rows, 'group_rows': self.__group_rows}
        }

    def list(self, row=10, start=0, webid=0, ip='', domain='', stime='', etime='', user='', access_page='', url='', source='', field='*', order='`id` DESC', group='', date='%Y-%m-%d'):
        """
        实时统计数据获取
        :param row: [int] 分页时为每页要显示的数量，不分页时为调用的总记录数。缺省值为 10
        :param start: [int] 不分页时，从第几条数据开始调用，分页时无效。缺省值0
        :param webid: [int] 所属的应用id，0调用全部，其他为调用webid。缺省值0
        :param ip: [str] 要筛选的ip地址。缺省值''
        :param domain: [str] 要筛选的域名。缺省值''
        :param stime: [str] 开始时间，格式：'201910151340'。缺省值''
        :param etime: [str] 结束时间，格式：'201910151340'。缺省值''
        :param user: [str] 筛选的用户。缺省值''
        :param access_page: [str] 筛选的访问页面，格式'admin/index'。缺省值''
        :param url: [str] 筛选的访问地址。缺省值''
        :param source: [str] 来源的地址。缺省值''
        :param field: [str] 查询的字段。缺省值''
        :param order: [str] 排序方式。缺省值'`id` DESC'
        :param group: [str] sql分组。缺省值''
        :param date: [str] 返回的日期格式，格式：'%Y-%m-%d %H:%M:%S'。缺省值'%Y-%m-%d'
        :return: 数据库查到并整形过后的列表数据
        """
        # sql语句
        ip_sql = ' && ip like"%%%s%%"' % ip if ip else ''  # ip地址
        domain_sql = ' && domain like "%%%s%%"' % domain if domain else ''  # 域名
        start_sql = ' && addtime > %d' % mk_time(stime, "%Y%m%d%H%M") if mk_time(stime, "%Y%m%d%H%M") else ''  # 开始时间
        end_sql = ' && addtime < %d' % mk_time(etime, "%Y%m%d%H%M") if mk_time(etime, "%Y%m%d%H%M") else ''  # 结束时间
        webid_sql = ' && webid = %d' % webid if webid else ''  # 系统应用
        if source == 0: source_sql = ' && source = ""'
        else:source_sql = ' && source = "%s"' % source if source else ''  # 来源地址
        url_sql = ' && url = "%s"' % url if url else ''  # 来源地址
        # 访问页面
        if access_page:
            access_page = access_page.split('/')
            if access_page[1] == "index": access_page[1] = 'index", "'
            access_page_sql = ' && model = "%s" && page in ("%s")' % (access_page[0], access_page[1])
        else:
            access_page_sql = ''
        # 用户
        if user:
            user_data = self.db.list(table='admin', field='id', where='username like "%%%s%%"' % user)  # 查管理员表
            id_list = []
            for var in user_data:
                id_list.append(str(var['id']))
            if id_list: user_sql = '&& (adminid in (%s) or aid like "%%%s%%")' % (','.join(id_list), user)
            else: user_sql = '&& aid like "%%%s%%"' % user
        else: user_sql = ''

        # where
        if group:
            where = '1 %s%s%s%s%s%s%s%s%s' % (start_sql, end_sql, ip_sql, domain_sql, webid_sql, access_page_sql, user_sql, source_sql, url_sql)
            self.__group_rows = self.db.list(table='access', field='count(*)', where=where, shift=1)['count(*)']
        where = '1 %s%s%s%s%s%s%s%s%s %s' % (start_sql, end_sql, ip_sql, domain_sql, webid_sql, access_page_sql, user_sql, source_sql, url_sql, group)

        # limit
        limit = row if self.__page else '%d, %d' % (start, row)
        data = self.db.list(table='access', field=field, where=where, page=self.__page, order=order, limit=limit)
        if self.__page > self.db.total_page:
            self.__page = self.db.total_page
            data = self.db.list(table='access', field=field, where=where, page=self.__page, order=order, limit=limit)
        if field == '*':
            data = self.data_format(data, date) if data else []
        self.__total_page, self.__total_rows, self.__page = (self.db.total_page, self.db.total_rows, self.db.page)
        return data

    def data_format(self, data, date_format):
        """
        将数据进行整形
        :param data: [list{}] 从数据库查出的数据
        :param date_format: [str] 日期格式化：
                                %y 两位数的年份表示（00-99）  %Y 四位数的年份表示（000-9999）  %m 月份（01-12）  %d 日，月内中的一天（0-31）
                                %H 24小时制小时数（0-23）  %I 12小时制小时数（01-12）  %M 分钟数（00=59）  %S 秒（00-59）
                                %a 本地简化星期名称  %A 本地完整星期名称 %b 本地简化的月份名称, 英文  %B 本地完整的月份名称, 英文
                                %c 本地相应的日期表示和时间表示  %j 年内的一天（001-366）  %p 本地A.M.或P.M.的等价符  %U 一年中的星期数（00-53）星期天为星期的开始（第n周）
                                %w 星期（0-6），星期天为星期的开始  %W 一年中的星期数（00-53）星期一为星期的开始（第n周）   %x 本地相应的日期表示
                                %X 本地相应的时间表示  %Z 当前时区的名称  %% %号本身
        :return: [list{}] 将整形过后的数据返回
        """
        from kyger.utility import date
        # 获取应用标题
        web_title = self.db.list(table='web', field='id, name')
        web = {}
        for row in web_title:
            web[row['id']] = row

        adminid_list = []
        for i in data:
            i['web_name'] = web.get(i['webid'])['name'] if web.get(i['webid']) else 'None'  # 应用名
            # 时间格式显示
            if 'addtime' in i:
                i['addtime'] = date(i['addtime'], format=date_format)
            i['ident'] = i['aid'][0:3:1] + '***' + i['aid'][-3::1]
            if i['adminid'] not in adminid_list:
                adminid_list.append(str(i['adminid']))
        # 获取管理员用户名
        admin_username = self.db.list(
            table='admin',
            field='id, username',
            where='`id` in (%s)' % ','.join(adminid_list),
            limit=numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
        )
        username = {}
        for row in admin_username:
            username[row['id']] = row
        for i in data:
            i['admin'] = username.get(i['adminid'])['username'] if username.get(i['adminid']) else ''  # 管理员
        return data

    def upadte(self):

        web_statistics = json2dict(file="config/web_statistics.json")
        # 每日
        if date(web_statistics['addtime'], '%Y%m%d') != date(int(self.kg['run_start_time'][1]), '%Y%m%d'):
            day = self.max_data(0)
            web_statistics['max_day']['pv'] = day['pv']
            web_statistics['max_day']['ip'] = day['ip']
            web_statistics['max_day']['time'] = day['time']
        # 每周
        if date(web_statistics['addtime'], '%Y%W') != date(int(self.kg['run_start_time'][1]), '%Y%W'):
            week = self.max_data(1)
            web_statistics['max_week']['pv'] = week['pv']
            web_statistics['max_week']['ip'] = week['ip']
            web_statistics['max_week']['time'] = week['time']
        # 每月
        if date(web_statistics['addtime'], '%Y%m') != date(int(self.kg['run_start_time'][1]), '%Y%m'):
            month = self.max_data(2)
            web_statistics['max_month']['pv'] = month['pv']
            web_statistics['max_month']['ip'] = month['ip']
            web_statistics['max_month']['time'] = month['time']
            dict2json_file(web_statistics, file='config/web_statistics.json')

    def max_data(self, type):
        arg_list = ['%Y%m%d', '%x,%v', '%Y%m']
        data = self.db.list(
            table='access',
            field="max(addtime) as addtime,COUNT(distinct ip) as ip,COUNT(*) as pv, DATE_FORMAT(FROM_UNIXTIME(addtime), '%s') as a" % arg_list[type],
            where="1 group by a",
            order="pv DESC",
            limit="0,1",
            shift=1
        )
        if type == 1:
            week = date(data['addtime'], '%Y,%W')
            week_list = week.split(',')
            week_day = numeric(date(mk_time(week_list[0], '%Y'), '%w')) - 1
            time = mk_time(week_list[0], '%Y') + numeric(week_list[1], 0) * 604800 - week_day * 86400
        else:
            time = mk_time(data['a'], arg_list[type])
        return {'pv': data['pv'], 'ip': data['ip'], 'time': time}






