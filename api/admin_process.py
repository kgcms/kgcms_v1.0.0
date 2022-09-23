# -*- coding:utf-8 -*-
"""原PHP版APP文件，各种功能逻辑处理、aJax处理"""

from kyger.utility import *
from os import remove, rename
import json


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        pass

    def __call__(self):
        action = self.kg['get'].get('action', '')  # 事件
        value = self.kg['get'].get('value', '')  # 参数
        post_param = self.kg['post']
        # dict2json_file({"data":str(post_param)})
        # ajax上传图片
        if post_param.get('action') == 'upload':
            file_name = post_param.get('filename', '')
            if not file_name: file_name = '{y}{mm}{dd}{hh}{ii}{ss}'
            dir = post_param.get('dir', 'other')
            file = post_param.get('file', {'data': ''})
            from kyger.upload import Upload
            if file:
                up = Upload(file, self.db, self.kg)
                up.path = 0  # 不创建路径
                up.exist_rename = False  # 文件名存在是否自动重命名。
                up.filename = file_name  # 文件命名规则
                msg = up.file(dir, True)
                if msg.get('url', ''):
                    # 水印与裁切
                    if dir in ['article', 'product', 'picture', 'download']:
                        # 获取配置文件，实例化裁切水印类
                        from kyger.cropper import Cropper
                        crop = Cropper(msg['url'])
                        conifg = json2dict(file='config/set_picture.json')
                        module = '%s_thumbnail' % dir if post_param.get('type', '') == 'thumbnail' else dir

                        # 裁切
                        if conifg['cut'][module][1]:
                            crop.cut(conifg['cut'][module][2], conifg['cut'][module][3])
                        # 水印
                        if conifg['cut'][module][0]:
                            crop.watermark()
                return json2dict(msg, trans=False)
            return json2dict({'state': 'FAILURE', 'msg': '没有选择文件'}, trans=False)

        # 设置每页要显示的记录数
        if action == 'set_page':
            self.set_cookie = {'KGCMS_PAGE_ROWS': numeric(value, 5, 1000)}  # 设置cookie，全局显示条数
            return alert(act=2)  # 返回上一页并刷新

        # 设置每页要显示的记录数(3的倍数)
        if action == 'set_picture':
            self.set_cookie = {'KGCMS_PICTURE_ROWS': numeric(value, 3, 1000)}  # 设置cookie，全局显示条数
            return alert(act=2)  # 返回上一页并刷新

        # 重启当前应用
        # 使用方法：<!--script type="text/javascript" src="/api/admin_process?action=app_restart&value=start"></script-->
        elif action == 'app_restart':  # Python 重启
            if value == 'start':  # 重启
                # 操作日志
                log(self.db, self.kg, 8, {'state': 'SUCCESS'})

                # import subprocess
                # subprocess.run(["pm2", "restart", "all"], shell=True)
                # return "重启完成"

                import sys, os
                python = sys.executable
                os.execl(python, python, *sys.argv)

            else:

                html = """
                <!doctype html><html><head><meta charset="utf-8"><title>重启 KGCMS</title></head><body><style type="text/css">
                *{font-size:16px; font-family:"微软雅黑; NSimSun"; white-space:nowrap; color:#A9B7C6; background:#2B2B2B; line-height:20px;}
                div{color:#CC7832; text-align:center; height:35px; line-height:35px; padding:16% 0 0 0;}
                a{display:block; margin:10px auto; width:80px; height:30px; text-align:center; line-height:30px; background:#444; text-decoration:none;}
                a:hover{ background:#666; }</style><div id="cutover">KGCMS 正在重启中，请稍候 ... <br /><img src="../static/image/progress.gif" /><br /><span id="time">正在准备重启</span></div>
                <script type="text/javascript" src="/api/admin_process?action=app_restart&value=start"></script>
                <script type="text/javascript">var jgt = 5; var stime = function(){
                document.getElementById('time').innerHTML = jgt; jgt = jgt - 1; if(jgt == 0){clearInterval(timing);
                document.getElementById('cutover').innerHTML = '重启完成，请关闭当前窗口<br /><a href="/" onclick="javascript:window.close(); return false;">关 闭</a>'}}
                var timing = setInterval("stime();",1000);
                </script></body></html>
                """
                return html

        # 清空 temp 缓存文件
        elif action == 'clear_temp':
            list = file_list(self.kg['server']['ROOT_PATH'] + 'temp', 1, 2)
            for temp_file in list: remove(temp_file)
            return alert(msg="操作成功，已清除 %s 个临时文件" % len(list), act=2)

        # 后台文件下载
        # admin_process?action=download&name=aacb.sql&code=[使用cipher加密后的完整路径]
        elif action == "download":
            from os.path import basename, getsize
            save_name = self.kg['get'].get('name', '')  # 保存时默认新的文件名，为空时将采用旧文件名
            file = self.kg['get'].get('code', '')  # 下载路径，经过加密的路径

            file = cipher(file)  # 要下载的文件完整路径解密
            if not save_name: save_name = basename(file)
            self.response_headers = {
                'code': '200 OK',
                'headers': [
                    ('Accept', 'bytes'),
                    ("Cache-Control", "must-revalidate, post-check=0, pre-check=0"),
                    ("Content-Description", "File Transfer"),
                    ("Content-Type", "application/octet-stream"),
                    ("Content-Length", str(getsize(file))),
                    ("Content-Disposition", "attachment; filename=" + save_name),
                ]
            }
            r = open(file, 'rb').read()
            return r

        elif action == 'set_view':  # 设置视图类型
            if value == "list": self.set_cookie = {'KGCMS_PAGE_VIEW': 'list'}  # 设置cookie
            if value == "simple": self.set_cookie = {'KGCMS_PAGE_VIEW': 'simple'}  # 设置cookie
            return alert(act=2)
        elif action == "install_template":  # 安装模板
            import urllib.request
            import os
            from kyger.common import un_pack
            file = cipher(self.kg['get'].get('code', ''))  # 要下载的文件完整路径解密
            if not file: return 'Parameter Error'
            path = 'temp/%s_%s' % (date(int(self.kg['run_start_time'][1]), "%Y%m%d%H%M%S"), file.split('/')[-1])
            urllib.request.urlretrieve(file, url_absolute(path))  # 下载文件到temp文件夹下
            un_pack(path, 'template/frontend')  # 解压
            os.remove(url_absolute(path))  # 删除
            return alert(act=2)
        elif action == 'test':
            return value
        else:
            return 'Parameter Error'


