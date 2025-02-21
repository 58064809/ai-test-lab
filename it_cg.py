# coding=utf-8
# 2025/1/17 11:57
from datetime import datetime

a = "2024/11/27 09:46:23"
a = a.replace('/', '-')
print(datetime.strptime(a, '%Y-%m-%d %H:%M:%S'))