# -*- coding:utf-8 -*-
"""这是一个允许 aJax 跨域请求的示例文件"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    def __init__(self):
        pass

    def __call__(self):
        # 设置 response 响应头
        self.response_headers = {'code': '200 OK', 'headers': [
            ('Accept', 'bytes'),  # 数据类型
            ('Content-type', 'text/html; charset=utf-8'),  # 文件类型及编码
            ('Access-Control-Allow-Credentials', 'true'),  # 设置是否允许发送 cookies
            ('Access-Control-Allow-Headers', 'Content-Type, Content-Length, Accept-Encoding, X-Requested-with, Origin'),  # 设置允许自定义请求头的字段
            ('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE'),  # 允许请求的类型
            ('Access-Control-Allow-Origin', '*'),  # *代表允许任何网址请求
        ]}

        return {}

