# -*- coding:utf-8 -*-
"""网站文章"""
from kyger.utility import *
from tools import qrcode, six


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.weixin import Weixin
        wechat = Weixin(self.db, self.kg)
        get_param = self.kg['get']
        post_param = self.kg['post']

        # 删除
        if get_param.get('action', '') == "del":
            del_id = numeric(get_param.get('id', ''), 0)
            if del_id:
                del_row = self.db.list(table='cs_account', where=del_id, shift=1)
                self.db.dele('cs_account', del_id)
                res = wechat.wx_cs_del(del_row['account'])
                if res.get('errcode', ''): return alert(msg='删除失败:%s' % res['errmsg'], act=3)
                else: return alert(act=2)
            return alert(msg='参数错误', act=3)

        elif post_param.get('action', '') == "move":
            id = post_param.get('id', [])
            if not id: return alert(msg='没有选择客服', act=3)
            group = numeric(post_param.get('group', 0), 0)
            self.db.edit('cs_account', {'group_id': group}, where='id in (%s)' % ','.join(id))
            self.update_cs_count()
            return alert(act='wx_cs_manage')

        elif get_param.get('action', '') == 'syn':
            if not exists(url_absolute('temp/wx_cs.json'), 'file'):
                res = wechat.wx_cs_get()
                if res.get('errcode', ''): return alert(msg='同步失败：%s' % res['errmsg'], act=3)
                # 删除腾讯服务器没有的客服
                kf_id_list = []
                for row in res['kf_list']:
                    kf_id_list.append(str(row['kf_id']))
                self.db.dele(table='cs_account', where='kf_id not in (%s)' % ','.join(kf_id_list))
                dict2json_file(res, file='temp/wx_cs.json')
                return template(
                    assign={"count": len(kf_id_list), "index": 0, "cs_info": res['kf_list'][0], 'end': 0},
                    tpl='cs_syn.tpl'
                )
            else:
                cs_list = json2dict(file='temp/wx_cs.json')
                index = numeric(get_param.get('index', 0))
                cs_data = cs_list['kf_list'][index]
                kf_data = self.db.list(table='cs_account', where='kf_id = %s' % cs_data['kf_id'])

                # 下载图
                path = ''
                if cs_data['kf_headimgurl']:
                    path = '/upload/client_services/%s.jpg' % cs_data['kf_id']
                    put_contents(path, get_contents(cs_data['kf_headimgurl'], charset=""), 'wb')

                # 修改
                if kf_data:
                    data = {
                        'kf_id': cs_data.get('kf_id', 0),
                        'account': cs_data.get('kf_account', ''),
                        'nickname': cs_data.get('kf_nick', ''),
                        'headingurl': path,  # 图片需要下载
                        'kf_wx': cs_data.get('kf_wx', ''),
                        'invite_wx': cs_data.get('invite_wx', ''),
                        'invite_expire_time': cs_data.get('invite_expire_time', 0),
                        'invite_status': cs_data.get('invite_status', ''),
                    }
                    self.db.edit('cs_account', data, 'kf_id = %s' % cs_data['kf_id'])
                # 添加
                else:
                    data = {
                        'group_id': 0,
                        'kf_id': cs_data.get('kf_id', 0),
                        'account': cs_data.get('kf_account', ''),
                        'nickname': cs_data.get('kf_nick', ''),
                        'headingurl': path,  # 图片需要下载
                        'kf_wx': cs_data.get('kf_wx', ''),
                        'invite_wx': cs_data.get('invite_wx', ''),
                        'invite_expire_time': cs_data.get('invite_expire_time', 0),
                        'invite_status': cs_data.get('invite_status', ''),
                        'addtime': int(self.kg['run_start_time'][1])
                    }
                    self.db.add('cs_account', data)
                self.update_cs_count()
                if index == len(cs_list['kf_list']) - 1:
                    end = 1
                    import os
                    os.remove(url_absolute('temp/wx_cs.json'))
                    cs_info = {}
                else:
                    end = 0
                    cs_info = cs_list['kf_list'][index + 1]
                return template(
                    assign={"count": len(cs_list['kf_list']), "index": index + 1, "cs_info": cs_info, 'end': end},
                    tpl='cs_syn.tpl'
                )

        else:
            # 二维码
            if not exists(url_absolute('upload/client_services/frontend_cs.png'), type='file'):
                url = '%s/cs_group' % self.kg['server']['HTTP_HOST']
                img = qrcode.make(url)  # 创建支付二维码片
                img.save(url_absolute('upload/client_services/frontend_cs.png'))

            page = numeric(get_param.get('page', 1))
            row = numeric(self.kg['cookie'].get('KGCMS_PAGE_ROWS', 10))
            data = self.db.list(
                table='cs_account',
                page=page,
                limit=row
            )
            if page > self.db.total_page:
                page = self.db.total_page
                data = self.db.list(
                    table='cs_account',
                    page=page,
                    limit=row
                )
            page_data = {'page': self.db.page, 'total_page': self.db.total_page, 'total_rows': self.db.total_rows}
            data = wechat.wx_cs_online(data)
            from kyger.common import page_tpl
            page_html = page_tpl(page, self.db.total_page, row, self.kg['server'].get('WEB_URL'))
            group = self.db.list(table='cs_group')

            return template(assign={'data': data, 'group': group, 'page_html': page_html, 'page_data': page_data})

    def update_cs_count(self):
        group_list = self.db.list(
            table='cs_account',
            field="count(*), group_id",
            where='1 group by group_id'
        )
        sql = 'UPDATE %scs_group SET cs_count = CASE id ' % self.db.cfg["prefix"]
        group_id_list = []
        for var in group_list:
            sql += 'WHEN %s THEN %s ' % (var['group_id'], var['count(*)'])
            group_id_list.append(str(var['group_id']))
        self.db.edit('cs_group', {'cs_count': 0})
        self.db.run_sql(sql + 'END WHERE id in (%s)' % ','.join(group_id_list), 'edit')