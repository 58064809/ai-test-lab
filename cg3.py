# coding=utf-8
# 2024/11/18 14:00
# import json
#
# json_str = '''
# {
#     "name": "John",
#     "age": 30,
#     "cars": [
#         {"name": "Ford", "models": ["Fiesta", "Focus", "Mustang"]},
#         {"name": "BMW", "models": ["320", "X3", "X5"]},
#         {"name": "Fiat", "models": ["500", "Panda"]}
#     ]
# }
# '''
#
# # 解析 JSON 字符串为 Python 对象
# data = json.loads(json_str)
#
#
# def traverse_json(obj, level=0):
#     """
#     递归遍历 JSON 数据
#     :param obj: JSON 对象（可能是字典或列表）
#     :param level: 缩进级别（用于美观输出）
#     """
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             print(f"{'  ' * level}Key: {key}, Value:")
#             traverse_json(value, level + 1)
#     elif isinstance(obj, list):
#         for i, item in enumerate(obj):
#             print(f"{'  ' * level}Item {i}:")
#             traverse_json(item, level + 1)
#     else:
#         print(f"{'  ' * level}Value: {obj}")
#
# # 调用递归函数遍历数据
# traverse_json(data)

#
# import pytest
# import requests
# import re
# from jsonpath_ng.ext import parse  # 使用 jsonpath-ng.ext 提供的扩展
# from bs4 import BeautifulSoup
# from typing import Union
# from mashumaro import DataClass
#
#
# # 通过 mashumaro 定义一个示例数据类，用于将 JSON 自动转化为对象
# class Post(DataClass):
#     id: int
#     title: str
#     body: str
#
#
# def get_response(url: str, session: requests.Session = None) -> requests.Response:
#     """获取 API 响应，默认使用 session，提高性能"""
#     session = session or requests.Session()
#     try:
#         response = session.get(url)
#         response.raise_for_status()  # 检查是否请求成功
#         return response
#     except requests.RequestException as e:
#         # 捕获网络请求错误并抛出异常
#         print(f"Error fetching {url}: {e}")
#         return None
#
#
# def extract_json_data(response: requests.Response) -> Union[Post, None]:
#     """
#     从 JSON 响应中提取数据，使用 jsonpath 提取数据。
#     返回一个 Post 对象，或者 None（如果未找到）
#     """
#     data = response.json()
#     jsonpath_expr = parse('$.id')
#     matches = jsonpath_expr.find(data)
#     if matches:
#         return Post.from_dict(data)  # 将 JSON 转换为 Post 对象
#     return None
#
#
# def extract_text_data(response: requests.Response) -> Union[str, None]:
#     """
#     从文本响应（HTML）中提取数据，使用 BeautifulSoup 提取 <title> 标签内容
#     """
#     html_content = response.text
#     soup = BeautifulSoup(html_content, 'html.parser')
#     return soup.title.string if soup.title else None
#
#
# def extract_data_from_response(response: requests.Response) -> Union[str, Post, None]:
#     """
#     根据响应的 Content-Type 动态判断并提取数据。
#     如果是 JSON 响应，使用 jsonpath 提取数据；如果是文本响应，使用 BeautifulSoup 提取数据。
#     """
#     if not response:
#         return None
#
#     content_type = response.headers.get("Content-Type", "").lower()
#
#     if "application/json" in content_type:
#         return extract_json_data(response)
#
#     elif "text" in content_type:
#         return extract_text_data(response)
#
#     return None
#
#
# # 测试 JSON 响应数据的提取
# def test_extract_json_data():
#     """测试 JSON 响应数据的提取"""
#     url = "https://jsonplaceholder.typicode.com/posts/1"
#     response = get_response(url)
#
#     extracted_data = extract_data_from_response(response)
#
#     # 期待返回一个 Post 对象，并且 id 应该是 1
#     assert isinstance(extracted_data, Post)
#     assert extracted_data.id == 1
#     assert extracted_data.title is not None
#
#
# # 测试 HTML 响应数据的提取
# def test_extract_html_data():
#     """测试 HTML 响应数据的提取"""
#     url = "https://example.com"
#     response = get_response(url)
#
#     extracted_data = extract_data_from_response(response)
#
#     # 期待返回 <title> 标签内容
#     assert extracted_data is not None
#     assert isinstance(extracted_data, str)  # extracted_data 应该是字符串（title 内容）
#     assert len(extracted_data) > 0  # title 内容不为空
#
#
# # 测试异常处理，模拟请求失败
# def test_invalid_url():
#     """测试无效 URL 请求"""
#     url = "https://invalid-url.com"
#     response = get_response(url)
#     assert response is None  # 无效 URL 应该返回 None


# import requests
# url = 'https://apid.lianlianlvyou.com/v1/movie/order/fulu/notify'
# data = {
#     "code":200,
#     "sign":"uayudkdashfdqfdkjfldaskjadads8129daiw12312312", # 写死
#     "data":{
#     "status":"6", # 4 出票成功 5 订单核销 6 //订单退款,
#     "orderNo":"T244601112510165673" # 订单号
#     }
# }
#
# print(requests.session().post(url, json=data).text)


# s = "`id`, `vision`, `parent`, `product`, `branch`, `module`, `plan`, `source`, `sourceNote`, `fromBug`, `feedback`, `title`, `keywords`, `type`, `category`, `pri`, `estimate`, `status`, `subStatus`, `color`, `stage`, `stagedBy`, `mailto`, `lib`, `fromStory`, `fromVersion`, `openedBy`, `openedDate`, `assignedTo`, `assignedDate`, `approvedDate`, `lastEditedBy`, `lastEditedDate`, `changedBy`, `changedDate`, `reviewedBy`, `reviewedDate`, `closedBy`, `closedDate`, `closedReason`, `activatedDate`, `toBug`, `childStories`, `linkStories`, `linkRequirements`, `twins`, `duplicateStory`, `version`, `storyChanged`, `feedbackBy`, `notifyEmail`, `URChanged`, `deleted`".replace(
#         '`', '').replace(' ', '').strip().split(',')
#
# print(','.join(s))

# print((10, 7, 1,'【探客系统】插入BUG-01', 1, 2, 'codeerror', '这是步骤<br />\n这是结果<br />\n这是期望', 'closed',1,'路昭凡', '2023-02-15 14:33:33', 'trunk', 'closed', 1, '0000-00-00', '胡强', 'fixed', 'trunk', '2023-02-18 11:33:33', '谭斌', 1,0, '谭斌', 1)[-2])

a = [1,2,3,4]
for i,item in enumerate(a[1:]):
    print(i,item)