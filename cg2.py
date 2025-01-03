# coding=utf-8
# 2024/10/26 16:23


from locust import HttpUser, task, between

token = N

class MyUser(HttpUser):
    wait_time = between(1, 5)

    # 类级别的变量，用于存储共享的 token
    def on_start(cls):
        """在所有用户开始之前执行一次登录操作"""
        if cls.token is None:  # 只有在第一次运行时才进行登录
            response = cls.client.post("/login", json={
                "username": "testuser",
                "password": "password123"
            })
            if response.status_code == 200:
                cls.token = response.json().get('token')
                print(f"Token obtained: {cls.token}")
            else:
                print("Login failed")
                raise Exception("Login failed")

    @task
    def view_dashboard(self):
        """使用共享的 token 访问受保护的资源"""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/dashboard", headers=headers)

    @task
    def view_profile(self):
        """使用共享的 token 访问用户资料"""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/profile", headers=headers)

    @task
    def view_search_results(self):
        """使用共享的 token 执行搜索任务"""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/search?q=test", headers=headers)
