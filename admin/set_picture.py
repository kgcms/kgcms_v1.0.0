# -*- coding:utf-8 -*-
"""图片裁切及水印"""


class KgcmsApi(object):
    """KGCMS框架接口"""

    kg = db = None

    def __init__(self):
        from kyger.cropper import Cropper
        Cropper('static/image/watermark_preview_bg.jpg').watermark('upload/other/watermark_preview.jpg')

    def __call__(self):
        from kyger.kgcms import template
        from kyger.utility import file_list, json2dict, alert, numeric, html_escape, str_replace, dict2json_file, file_list, exists, url_absolute

        # 1.获取数据
        post = self.kg['post']

        if post.get('action', '') == 'submit':
            data = {
                "cut":{
                    "condition": [numeric(post['condition'][0]), numeric(post['condition'][1])],
                    "quality": numeric(post['quality']),
                    "article_thumbnail": [numeric(post['article_thumbnail'][0]), numeric(post['article_thumbnail'][1]), numeric(post['article_thumbnail'][2]), numeric(post['article_thumbnail'][3])],
                    "article": [numeric(post['article'][0]), numeric(post['article'][1]), numeric(post['article'][2]), numeric(post['article'][3])],
                    "product_thumbnail": [numeric(post['product_thumbnail'][0]), numeric(post['product_thumbnail'][1]), numeric(post['product_thumbnail'][2]), numeric(post['product_thumbnail'][3])],
                    "product": [numeric(post['product'][0]), numeric(post['product'][1]), numeric(post['product'][2]), numeric(post['product'][3])],
                    "picture_thumbnail": [numeric(post['picture_thumbnail'][0]), numeric(post['picture_thumbnail'][1]), numeric(post['picture_thumbnail'][2]), numeric(post['picture_thumbnail'][3])],
                    "picture": [numeric(post['picture'][0]), numeric(post['picture'][1]), numeric(post['picture'][2]), numeric(post['picture'][3])],
                    "download_thumbnail": [numeric(post['download_thumbnail'][0]), numeric(post['download_thumbnail'][1]), numeric(post['download_thumbnail'][2]), numeric(post['download_thumbnail'][3])],
                    "download": [numeric(post['download'][0]), numeric(post['download'][1]), numeric(post['download'][2]), numeric(post['download'][3])]
                },
                "watermark": {
                    "condition": [numeric(post['mark'][0]), numeric(post['mark'][1])],
                    "type": post['type'],
                    "path": "/upload/other/watermark.png",
                    "position": numeric(post['position'], 0, 8),
                    "offset": [int(post['offset'][0]), int(post['offset'][1])],
                    "font": "fonts/%s" % post['font'],
                    "color": post['color'],
                    "word": post['word'],
                    "size": numeric(post['size']),
                    "angle": numeric(post['angle'])
                }
            }
            dict2json_file(data, file='config/set_picture.json')

        tab = 1 if numeric(post.get('tab')) == 1 else 0
        # 配置文件
        config = json2dict(file='config/set_picture.json')
        config['watermark']['font'] = config['watermark']['font'].split('/')[-1]
        config['watermark']['image'] = 1 if exists(url_absolute(config['watermark']['path']), type='file') else 0

        # 字体
        fonts = file_list('fonts/', 1, 0)

        # PIL模块
        import sys
        PIL_module = 0
        for path in sys.path:
            if exists(path + '/' + 'PIL'):
                PIL_module = 1

        return template(assign={
            'data': config,
            'fonts': fonts,
            'PIL': PIL_module,
            'tab': tab
        })
