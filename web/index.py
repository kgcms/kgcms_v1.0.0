# -*- coding:utf-8 -*-
"""网站首页"""

from kyger.utility import *
from kyger.kgcms import template
from kyger.common import *


class KgcmsApi(object):
    """KGCMS框架接口"""
    db = kg = None

    def __init__(self):
        pass
    
    def __call__(self):
        from kyger.kgcms import template
        from kyger.category import Category
        from kyger.article import Article
        from kyger.product import Product
        from kyger.ad import Advertise
        from kyger.misc import Misc
        misc = Misc(self.db, self.kg)

        return template(
            assign={"path": str_replace(self.kg['server']['WEB_URL'], [self.kg['server']['HTTP_HOST'] + '/'], '')},
            function=[
                {"category": Category(self.db, self.kg).list},
                {"article_list": Article(self.db, self.kg).list},
                {"article_single": Article(self.db, self.kg).single},
                {"article_page": Article(self.db, self.kg).list_page},
                {"ad_list": Advertise(self.db, self.kg).list},
                {"navigate_list": misc.navigate},
                {"app": misc.app},
                {"get_cart": Product(self.db, self.kg).get_cart},
            ],
        )
    
    
    



        
        
        
        
        
        
        
        
        
        
        
        
        
        
       
    


    
        



