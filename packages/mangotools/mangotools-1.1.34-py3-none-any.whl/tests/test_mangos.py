# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-24 10:01
# @Author : 毛鹏

from mangotools.mangos import Mango, get, test

Mango.v(1, '测试通过')
print(type(get))

test(1, data=1)