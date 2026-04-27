# Keploy 使用说明

## 官方来源

- Keploy 官方文档：https://keploy.io/docs/
- Keploy API Testing Agent：https://keploy.io/docs/2.0.0/running-keploy/api-test-generator/
- Keploy GitHub 仓库：https://github.com/keploy/keploy

## 当前定位

Keploy 适合做 API、集成、E2E 测试生成，以及基于真实 API 使用数据生成测试和 mocks。

官方文档说明，Keploy 可以从 OpenAPI、Postman、cURL、endpoints 或真实 API 使用数据生成测试；也支持记录真实 API 交互并在本地或 CI 中进行可重复 replay。

## 推荐使用场景

- 基于真实调用生成 API 测试。
- 基于 OpenAPI / Postman / cURL 生成测试套件。
- 需要记录真实流量并生成 mocks。
- 需要在 CI 中回放 API 行为，检查回归问题。

## 使用边界

当前仓库没有声明 Keploy 已完成接入。

接入前必须确认：

1. 当前项目语言、框架、运行方式是否适合 Keploy。
2. 是否可以在测试环境安全记录流量。
3. 是否涉及支付、发券、扣库存、短信、外部通知等高风险副作用。
4. 生成的 mocks / test artifacts 是否需要进入 `.gitignore`。
5. 是否使用 Keploy Cloud、Keploy OSS，或两者结合。

## 待验证事项

- Windows 本地是否能稳定运行 Keploy 相关命令。
- 是否需要 Docker、WSL2、管理员权限或网络抓取能力。
- 是否适合当前个人测试助手项目的本地工作流。
- 与 Pytest / CI / Allure 的结合方式。