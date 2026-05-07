# 038｜Codex 任务：真实任务验证包

## 任务目标

在 `ai-test-lab` 项目中新增 `examples/real_tasks/` 目录，用 8 个 Markdown 文件沉淀真实测试任务样例，用于验证当前个人 AI 测试助手是否真的有用。

当前任务只做任务样例沉淀，不写业务代码，不新增 runtime 能力，不接入新工具。

## 背景

当前主链路已完成：

```text
pytest --alluredir=allure-results
→ allure generate allure-results -o allure-report --clean
→ 读取 allure-report/widgets/summary.json
→ 输出测试报告摘要
```

本地已验证结果：

```text
total=204
passed=204
failed=0
broken=0
skipped=0
duration_ms=3936
```

当前不要继续拆 Allure，Allure 已收口。

## 需要创建的文件

请确保以下文件存在；如果不存在则创建，如果已存在则检查内容是否完整，必要时补齐：

```text
examples/real_tasks/README.md
examples/real_tasks/001_requirement_analysis.md
examples/real_tasks/002_test_case_generation.md
examples/real_tasks/003_log_analysis.md
examples/real_tasks/004_pytest_allure_summary.md
examples/real_tasks/005_codex_change_review.md
examples/real_tasks/006_api_test_design.md
examples/real_tasks/007_failed_test_to_bug_report.md
examples/real_tasks/008_tool_integration_evaluation.md
```

## 文件内容要求

### README.md

说明本目录是 `038｜真实任务验证包`，用于验证 AI 测试助手是否具备真实测试工作能力。

必须包含：

1. 目录用途；
2. 验证范围；
3. 文件说明；
4. 使用方式；
5. 评价标准；
6. 当前边界。

验证范围至少包含：

```text
需求分析
测试用例生成
日志分析
pytest + Allure 报告总结
Codex 修改结果审查
接口测试设计
失败测试结果生成缺陷报告
成熟工具接入评估
```

### 001_requirement_analysis.md

主题：需求分析任务验证。

需求内容：

```text
用户登录支持手机号验证码登录、账号密码登录、第三方授权登录。
登录成功后返回 token、用户信息、是否新用户标识。
如果是新用户，需要引导完善资料。
连续输错密码 5 次后锁定账号 30 分钟。
验证码 5 分钟内有效，同一手机号 60 秒内只能发送一次验证码。
```

输出要求包含：核心业务规则、异常场景、测试范围、风险点、测试优先级建议，不要直接写自动化代码。

### 002_test_case_generation.md

主题：测试用例生成任务验证。

基于登录需求生成测试用例。

输出格式必须是 Markdown 表格，列固定为：

```text
标题｜优先级｜前置条件｜测试步骤｜预期结果
```

要求：

1. 优先级使用 P0、P1、P2、P3；
2. 不需要“用例类型”列；
3. 不需要一个步骤对应一个预期，支持多对多；
4. 覆盖正常、异常、边界、安全、兼容性场景；
5. 输出中文。

### 003_log_analysis.md

主题：日志分析任务验证。

使用以下日志：

```text
2026-05-07 10:12:01 INFO  request_id=abc123 api=/api/order/create user_id=10001 start
2026-05-07 10:12:01 INFO  request_id=abc123 check stock sku_id=SKU001 available=0
2026-05-07 10:12:01 ERROR request_id=abc123 order create failed error=StockNotEnoughException message="stock not enough"
2026-05-07 10:12:01 INFO  request_id=abc123 rollback coupon coupon_id=C001 success=true
2026-05-07 10:12:01 INFO  request_id=abc123 rollback points points=100 success=true
2026-05-07 10:12:01 WARN  request_id=abc123 payment prepay skipped reason=order_create_failed
```

输出要求包含：失败环节、关键字段提取、数据一致性风险、补偿/回滚是否完整、下一步排查建议、信息不足时需要补充的日志或字段。

### 004_pytest_allure_summary.md

主题：pytest + Allure 报告总结任务验证。

使用以下结果：

```text
total=204
passed=204
failed=0
broken=0
skipped=0
duration_ms=3936
```

输出要求包含：执行结论、通过率、耗时、是否可以进入下一阶段、不夸大结论、说明 summary 信息局限。

### 005_codex_change_review.md

主题：Codex 修改结果审查任务验证。

模拟 Codex 完成如下改动：

1. 新增 `pytest_runner`；
2. 新增 `allure_report_reader`；
3. 新增 runtime CLI 参数 `--run-test-report`；
4. 支持执行 pytest 后自动生成 Allure 报告摘要。

审查重点：

1. 是否违反只读边界；
2. 是否引入 `shell` / `filesystem_write` / `github_write`；
3. 是否存在路径写死；
4. 是否有异常处理；
5. 是否有日志输出；
6. 是否有最小可验证链路；
7. 是否过度设计；
8. 是否破坏现有功能。

输出要求按“通过项 / 风险项 / 建议修改 / 是否可合并”输出，不要直接重写代码。

### 006_api_test_design.md

主题：接口测试设计任务验证。

接口：

```http
POST /api/coupon/receive
```

请求参数：

```json
{
  "user_id": 10001,
  "coupon_id": "C001"
}
```

业务规则：

1. 每个用户同一张优惠券只能领取一次；
2. 优惠券有库存；
3. 优惠券有领取时间范围；
4. 新人券仅新用户可领取；
5. 已过期、已下架、库存不足不可领取；
6. 领取成功后生成用户券记录并扣减库存；
7. 需要避免并发重复领取和库存超扣。

输出要求包含：测试点、核心测试用例、参数校验、并发测试、数据库校验、幂等性和一致性校验、成熟工具建议。

### 007_failed_test_to_bug_report.md

主题：失败测试结果生成缺陷报告任务验证。

失败信息：

```text
测试用例：领取新人券成功
接口：POST /api/coupon/receive
用户：10001
coupon_id：NEW_USER_001
预期结果：新人用户首次领取成功，返回 success=true，并生成用户券记录
实际结果：接口返回 success=false，message="coupon not available"
数据库检查：
- coupon.status = 1
- coupon.stock = 100
- coupon.start_time < 当前时间
- coupon.end_time > 当前时间
- user.is_new = true
- user_coupon 未生成记录
```

输出要求包含：缺陷标题、严重级别、优先级、前置条件、复现步骤、预期结果、实际结果、初步定位、建议补充排查信息。

### 008_tool_integration_evaluation.md

主题：成熟工具接入评估任务验证。

评估 Schemathesis 是否适合作为当前个人 AI 测试助手的接口测试生成工具。

当前项目约束：

1. 项目是个人专用 AI 测试助手；
2. 不做团队平台；
3. 不造轮子；
4. 代码实现交给 Codex；
5. 当前已有 Pytest + Allure；
6. 不能写死具体业务；
7. 优先成熟工具、官方生态、工业级方案。

输出要求包含：工具用途、适配位置、接入优先级、最小接入方式、不适合解决的问题、与 Pytest + Allure 的关系、是否建议现在接入、下一步 Codex 任务清单。

## 项目边界

必须遵守：

1. 不写业务代码；
2. 不继续拆 Allure；
3. 不做测试平台；
4. 不做团队平台；
5. 不写死当前公司业务；
6. 不引入新的复杂架构；
7. 不开放 `shell` / `filesystem_write` / `github_write`；
8. 只做任务样例沉淀；
9. 保持格式清晰、专业、可直接使用。

## 验收标准

完成后请输出：

1. 新增或确认存在的文件列表；
2. 每个文件的用途；
3. 是否符合“不造轮子、只做 Codex 任务清单、个人 AI 测试助手”的原则；
4. 是否有需要人工检查的地方。
