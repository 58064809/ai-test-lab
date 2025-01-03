# from flask import Flask, request, jsonify
# import gradio as gr
# from playwright.sync_api import sync_playwright
# from gevent import pywsgi
# import os
# import time
#
# app = Flask(__name__)
#
#
# # def login_to_website(loginurl, username, password, context_path):
# #     with sync_playwright() as p:
# #         # 使用 Chromium 浏览器
# #         browser = p.chromium.launch(headless=False)  # 设置为 False 可以看到浏览器操作
# #         iphone_11 = p.devices['iPhone 11 Pro']
# #         context = browser.new_context(
# #                 **iphone_11,
# #                 locale='zh-CN',
# #                 geolocation={ 'longitude': 12.492507, 'latitude': 41.889938 },
# #                 permissions=['geolocation']
# #             )
# #         page = context.new_page()
# #
# #         # 导航到登录页面
# #         page.goto(loginurl)
# #
# #         # 填写表单
# #         page.fill("input[class=uni-input-input]", username)
# #         page.fill("input[class=input-item-input]", password)
# #
# #         #点击协议
# #         # 定位 div 元素
# #         my_div = page.locator(".agree-image")
# #         # 点击 div 元素
# #         my_div.click()
# #         time.sleep(2)  # 等待 2 秒
# #
# #         # 提交表单
# #         page.click("uni-button[class=btn]")
# #
# #         # 等待页面加载完成
# #         page.wait_for_load_state("networkidle")
# #
# #         # 这将保存 cookies，以便后续请求保持登录状态
# #         context.storage_state(path=context_path)
# #
# #         # 关闭浏览器
# #         browser.close()
#
#
# ####大模型调用服务
# @app.route('/LLMRequest', methods=['POST'])
# def LLM_service():
#     # 获取输入信息
#     htmlurl = request.json['htmlurl']
#     output_path = r'./out.pdf'
#     if os.path.exists(output_path):
#         os.remove(output_path)
#     loginurl = 'https://cd-nt.lianlianlvyou.com/v2/index.html?i=wx16e21d1bfcacd281&v=337#/pagesLogin/login/passwordLogin'
#     username = '18511115458'
#     password = 'iawis1113'
#
#     with sync_playwright() as p:
#         # 使用 Chromium 浏览器
#         browser = p.chromium.launch(headless=True)  # 设置为 False 可以看到浏览器操作
#         iphone_13 = p.devices['iPhone 13 Pro']
#         context = browser.new_context(
#             **iphone_13,
#             locale='en-US',
#             geolocation={'longitude': 12.492507, 'latitude': 41.889938},
#             permissions=['geolocation']
#         )
#         page = context.new_page()
#
#         # 导航到登录页面
#         page.goto(loginurl)
#
#         # 填写表单
#         page.fill("input[class=uni-input-input]", username)
#         page.fill("input[class=input-item-input]", password)
#
#         # 点击协议
#         # 定位 div 元素
#         my_div = page.locator(".agree-image")
#         # 点击 div 元素
#         my_div.click()
#         time.sleep(2)  # 等待 2 秒
#
#         # 提交表单
#         page.click("uni-button[class=btn]")
#
#         # 等待页面加载完成
#         page.wait_for_load_state("networkidle")
#         time.sleep(2)  # 等待 2 秒
#
#         # 导航到指定的网页
#         page.goto(htmlurl)
#
#         # 等待页面加载完成
#         page.wait_for_load_state("networkidle")
#
#         time.sleep(5)  # 等待 2 秒
#
#         # 将页面转换为 PDF 文件
#         page.pdf(path=output_path, width="210mm", height="4297mm")
#         # 关闭浏览器
#         browser.close()
#         result = {'code': 200, 'data': request.json['htmlurl'], 'message': 'success'}
#         return jsonify(result)
#
#
# # ####定义页面信息
# # #定义聊天tab页面
# # llm_interface = gr.Interface(
# #     fn=LLM_service,
# #     inputs=gr.Textbox(label="输入网址", value='https://cd-nt.lianlianlvyou.com/v2/index.html?i=wx16e21d1bfcacd281&v=337#/pages/home/detail?id=1025844&from=home'),
# #     clear_btn="清除",
# #     submit_btn="提交",
# #     outputs=gr.Textbox(label="大模型输出"),
# #     allow_flagging="never"
# #     )
# # #定义模型信息tab页面
# # with gr.Blocks() as llminfo:
# #     gr.Markdown(
# #     """
# #      ## 信息说明
# #     ### 模型信息
# #     - 调用模型：QWenPlus
# #     - Prompt：无
# #     - 更新时间：2024年7月15日
# #
# #     ### 应用配置链接
# #     - [百炼APP链接](https://bailian.console.aliyun.com/?spm=5176.29228872.J_TC9GqcHi2edq9zUs9ZsDQ.1.3fe338b19oW8wg&accounttraceid=a970dc1f26674a6faa9746bf2fb9352bbgfu#/app-center/assistant/bc0d2328ebe6476686ed9002145f483d "阿里云官方网站")
# #     """
# #     )
# #
# # #定义主页面：tab组页面
# # iface = gr.TabbedInterface(
# #     [llm_interface, llminfo],
# #     ["模型调用", "模型信息"],
# #      title="网页内容转PDF测试-playwright",
# #     )
# # #主页面加载
# # iface.launch()
#
# if __name__ == '__main__':
#     # app.run(host='0.0.0.0', port=80)
#     server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
#     server.serve_forever()
import requests

print(requests.session().post("http://10.10.100.195/gen_pdf", json={
    "htmlUrl": "https://cd-nt.lianlianlvyou.com/v2/index.html?i=wx16e21d1bfcacd281&v=337#/pages/home/detail?id=1025844&from=home","uploadId": "123", "md5":"478b44ba930debf128d49079acd47844", "fileName": "test8.pdf"}).json())

