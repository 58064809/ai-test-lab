# Schemathesis 使用说明

## 官方来源

- Schemathesis Quick Start：https://schemathesis.github.io/schemathesis/quick-start/
- Schemathesis ReadTheDocs Quick Start：https://schemathesis.readthedocs.io/en/stable/quick-start/

## 当前定位

Schemathesis 适合在存在 OpenAPI 或 GraphQL schema 的情况下，自动生成大量测试用例来检查 API 契约、边界输入、服务端错误和响应校验。

官方 quick start 说明中，Schemathesis 会基于 schema 生成 property-based 输入，并执行状态码符合性、响应验证、服务端错误检测等检查。

## 推荐使用场景

- 项目已有 OpenAPI 文档。
- 需要快速发现接口边界问题。
- 需要验证实现和接口文档是否一致。
- 需要将接口契约测试接入 CI。

## 官方示例命令

测试官方示例 API：

```bash
uvx schemathesis run https://example.schemathesis.io/openapi.json
```

测试自己的远程 OpenAPI：

```bash
uvx schemathesis run https://your-api.com/openapi.json \
  --header 'Authorization: Bearer your-token'
```

测试本地 OpenAPI：

```bash
uvx schemathesis run ./openapi.yaml --url http://localhost:8000
```

## 使用边界

当前仓库没有声明 Schemathesis 已完成接入。

接入前必须确认：

1. 是否有 OpenAPI / GraphQL schema。
2. schema 是否能访问。
3. 是否需要鉴权 header。
4. 测试环境是否允许自动生成大量请求。
5. 是否存在写操作、扣库存、支付、发券等高风险接口，需要先隔离或限制。

## 待验证事项

- Windows 环境是否已安装 uv 或 Schemathesis。
- 当前项目是否有可用 OpenAPI 文档。
- 是否需要对高风险接口进行排除。
- 是否需要输出 JUnit XML / HAR / VCR cassette 等 CI 产物。