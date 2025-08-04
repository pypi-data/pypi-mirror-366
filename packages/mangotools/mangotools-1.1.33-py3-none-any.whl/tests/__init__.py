# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 23:25
# @Author : 毛鹏
from urllib.parse import unquote

encoded_str = "%E9%99%88%E6%A2%A6-%E5%B0%8F%E9%9F%B3%E7%AC%A6%2B%E8%9D%B4%E8%9D%B6%E9%9F%B3%E7%AC%A6"
decoded_str = unquote(encoded_str)
print(decoded_str)  # 输出：陈梦-小音符+蝴蝶音符