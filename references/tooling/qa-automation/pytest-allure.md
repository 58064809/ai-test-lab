# Pytest + Allure 使用说明

## 官方来源

- Pytest 官方文档：https://docs.pytest.org/
- Allure Pytest 官方文档：https://allurereport.org/docs/pytest/

## 当前定位

Pytest 是 Python 自动化测试的主执行框架。Allure Pytest 适合为 Pytest 测试生成结构化测试结果，并进一步生成可读测试报告。

本仓库后续如果沉淀自动化测试脚本，应优先围绕 Pytest 组织测试执行、fixture、断言、日志和报告产物。

## 推荐使用场景

- 接口自动化测试。
- 数据库校验脚本测试化。
- Redis 校验脚本测试化。
- 回归测试执行。
- 失败用例定位和测试报告输出。

## 常见命令

安装依赖的具体方式以项目实际依赖管理工具为准。以下命令仅作为官方能力验证方向，不表示当前项目已完成接入。

执行 Pytest：

```bash
pytest
```

生成 Allure 结果目录：

```bash
pytest --alluredir=allure-results
```

查看 Allure 报告：

```bash
allure serve allure-results
```

## 使用边界

当前仓库没有声明已经存在完整 Pytest 自动化框架。

接入前必须确认：

1. Python 版本。
2. 依赖管理方式。
3. 测试目录结构。
4. Allure 命令行工具是否安装。
5. CI 环境是否需要保存 `allure-results`、JUnit XML 或 HTML 报告。

## 待验证事项

- Windows 本地 Pytest 执行路径。
- Allure CLI 是否可用。
- 是否需要 Jenkins / GitHub Actions / 企业微信通知。
- 测试失败时日志、截图、请求响应、数据库校验结果如何挂到报告中。