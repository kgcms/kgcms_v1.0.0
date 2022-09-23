# -*- coding:utf-8 -*-
"""
ueditor富文本编辑器, 安全问题,当前页必须做登录验证
文件上传处理对象
UEditor 1.4.3.3
"""


class KgcmsApi(object):
    """接口文件"""
    
    set_cookie = request = del_cookie = {}  # 注册全局变量

    db = kg = None  # 打开数据库

    py_config = {}  # 位于 tools/ueditor/python/config.json 下的配置文件转成 python dict
 
    def __init__(self):
        """
        初始化数据
        """
        # 登录及权限检测 ***
        pass

    def __call__(self, *args, **kwargs):
        """
        接口文件
        :return:
        """
        from kyger.utility import get_contents, json2dict, dict2json_file
        from kyger.upload import Upload

        import re
        dict2json_file({"json_config":self.kg['server']['ROOT_PATH']})
        json_config = get_contents(self.kg['server']['ROOT_PATH'] + 'tools/ueditor/python/config.json')  # 配置文件
        json_config = re.sub(r"\/\*([\S\s]*?)\*\/", "", json_config)  # 过滤注释 /*  */
        self.py_config = json2dict(json_config)  # 将json配置文件转成 python dict
        
        action = self.kg['get'].get('action', '')
        dir = self.kg['get'].get('dir', 'other')  # 上传文件保存目录

        # return self.py_config['imageActionName']
        if action == 'config':
            return re.sub(r"\s*\n", '', json_config).replace(' ', '')  # 删除所有空行和空格
        elif action in ('uploadimage', 'uploadscrawl', 'uploadvideo', 'uploadfile'):  # 上传文件
            
            data = self.kg['post'].get('upfile', {'data': ''})
            res = Upload(data, self.db, self.kg).image(dir)
            if res['state'] == 'SUCCESS':
                return '{"state": "SUCCESS", "url": "%s", "title": "%s", "original": "%s", "type": "%s"}' %\
                       (res['url'], res['filename'], res['filename'], res['type'])
            else:
                return '{"state": "%s"}' % res['msg']
            
        elif action == 'listimage':  # 列出图片
            # 请求参数 GET{"action": "listimage", "start": 0, "size": 20}
            return {"state": "SUCCESS",
                    "list": [
                        {"url": "upload/1.jpg"},
                        {"url": "https://www.kyger.com.cn/inc/templates/frontend/kyger/images/aaa.png"},
                        {"url": "upload/3.jpg"},
                        {"url": "upload/4.jpg"},
                        {"url": "upload/5.jpg"},
                        {"url": "upload/6.jpg"},
                        {"url": "upload/7.jpg"},
                        {"url": "upload/8.jpg"},
                        {"url": "upload/9.jpg"},
                        {"url": "upload/10.jpg"},
                        {"url": "upload/11.jpg"},
                        {"url": "upload/12.jpg"},
                        {"url": "upload/13.jpg"},
                        {"url": "upload/14.jpg"},
                        {"url": "upload/15.jpg"},
                        {"url": "upload/16.jpg"},
                        {"url": "upload/17.jpg"},
                        {"url": "upload/18.jpg"},
                        {"url": "upload/19.jpg"},
                        {"url": "upload/20.jpg"},

                    ], "start": 20, "total": 80  # 每滚动一屏的数据起始数, 总数量
}
            pass
        elif action == 'listfile':  # 列出文件
            return {'state': '这里调用文件列表数据 ...'}
        elif action == 'catchimage':  # 抓取远程文件
            return {'state': '这里处理远程文件数据 ...'}
        else:
            return {'state': '请求参数错误'}

    

        
        
        
        
        
    
    


 
        


    

