# Agentic QA 调研指南

---

## 1. 文档定位

本文用于整理 Agentic QA 相关产品、框架、工具和质量分析平台的调研入口，并为 `docs/architecture/agentic-qa-blueprint.md` 提供外部资料依据。

它解决的问题不是“列一堆链接”，而是帮助测试工程师按合理顺序理解：

- Agentic QA 的商业产品形态是什么
- 底层 Agent 框架如何支撑工作流编排
- AI 如何接入浏览器、测试工具和研发工具链
- 哪些能力值得借鉴，哪些能力需要谨慎落地
- 当前仓库后续可以沉淀哪些 Agent、Skill、Template 和 Standard

后续只要涉及 Agentic QA 的方案设计、Agent 定义、Skill 编写、Template 设计或工程实现，都应先读取本文，再进入实现。

本文不替代 `AGENTS.md`、`standards/` 或 `skills/`：

- `AGENTS.md` 定义身份、协作原则和加载优先级
- `standards/` 定义输出、用例、缺陷、风险等质量标准
- `skills/` 定义具体测试能力怎么做
- 本文只提供外部调研入口、阅读路径和能力映射建议

---

## 2. 推荐阅读顺序

建议按以下顺序阅读，避免一开始陷入框架细节。

1. 先看商业平台  
   目标是理解 Agentic QA 在真实产品中被包装成什么能力。

2. 再看 Agent 框架  
   目标是理解多 Agent、工具调用、工作流编排、Guardrails 和可观测性如何实现。

3. 再看 MCP 与浏览器 Agent  
   目标是理解 AI 如何控制浏览器、读取页面结构、生成或维护测试。

4. 最后看测试报告与质量分析平台  
   目标是理解测试结果、失败归因、质量门禁和报告如何进入闭环。

资料维护要求：

- 外部产品和框架更新较快，正式引用前应重新打开官方链接确认
- 不把商业宣传语直接写成仓库事实，应转化为可验证的能力、输入、输出和边界
- 如果链接失效，应优先查找官方文档、官方 GitHub 或产品文档入口

---

## 3. 优先阅读清单

如果时间有限，优先看以下 6 个：

| 优先级 | 资料 | 重点关注 |
| --- | --- | --- |
| P0 | [Katalon Agentic QA Guide](https://katalon.com/resources-center/blog/what-is-agentic-qa-the-complete-guide-for-2026) | Agentic QA 的完整概念、自治程度、QA 角色变化 |
| P0 | [BrowserStack AI Agents](https://www.browserstack.com/docs/test-management/browserstack-ai) | 测试用例生成、测试数据生成、失败分析、测试选择、用例去重 |
| P0 | [LangGraph GitHub](https://github.com/langchain-ai/langgraph) | Agent 工作流编排、状态管理、长任务和多 Agent 结构 |
| P0 | [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) | Agent、Tools、Handoffs、Guardrails、Tracing |
| P0 | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | LLM 如何通过 MCP 操作浏览器并读取页面结构 |
| P1 | [Stagehand](https://github.com/browserbase/stagehand) | 自然语言 + 代码混合控制浏览器、浏览器 Agent 工程化形态 |

最低要求：

- 做 Agentic QA 总体方案前，至少阅读 Katalon、BrowserStack、LangGraph、OpenAI Agents SDK
- 做 UI 自动化、浏览器 Agent 或自愈测试前，至少阅读 Playwright MCP 和 Stagehand
- 做失败归因、报告和质量门禁前，至少阅读 ReportPortal

看完这 6 个，基本可以建立三层认知：

- 产品层：Agentic QA 能卖成什么样
- 架构层：Agent 工作流怎么组织
- 工具层：AI 如何接浏览器和测试执行工具

阅读时不要只摘录产品卖点，应记录每个资料对当前仓库的可落地点：它应该进入 `agents/`、`skills/`、`templates/`、`standards/`、`docs/` 还是仅作为 `references/` 背景资料。

---

## 4. 商业平台调研

商业平台适合用来观察产品形态、能力包装和企业落地方向。

| 名称 | 链接 | 建议看什么 | 可借鉴点 |
| --- | --- | --- | --- |
| Katalon Agentic QA | [What Is Agentic QA?](https://katalon.com/resources-center/blog/what-is-agentic-qa-the-complete-guide-for-2026) | Agentic QA 概念、自治测试工作流、QA 角色变化 | 可作为 `docs/` 中 Agentic QA 总体说明的参考 |
| Katalon True Platform | [Katalon True Platform](https://katalon.com/) | 商业平台如何包装 AI QA、Web/Mobile/API/Desktop 覆盖 | 可参考其端到端质量平台叙事 |
| BrowserStack AI Agents | [BrowserStack AI Docs](https://www.browserstack.com/docs/) | Test Case Generator、Self-Healing、Test Selection、Failure Analysis | 可拆成多个 Agent 能力模块 |
| BrowserStack Test Management AI | [Generate test artifacts](https://www.browserstack.com/docs/test-management/browserstack-ai) | 从需求、Jira、Confluence、Figma 生成测试资产 | 可参考测试资产生成与治理思路 |
| mabl Agentic Testing | [mabl Agentic Testing](https://www.mabl.com/agentic-testing-for-software-development-mabl) | 测试创建、执行、失败分析、维护、报告 | 可参考 Agentic Testing 的生命周期划分 |
| QA Wolf Automation AI | [QA Wolf](https://www.qawolf.com/) | Agentic SDLC、E2E 测试自动生成与并行执行 | 可关注 E2E 自动化服务化思路 |
| Applitools Visual AI | [Applitools Visual AI](https://applitools.com/platform/validate/visual-ai/) | 视觉回归、UI 变化检测、视觉断言 | 可用于 UI 回归和视觉质量评估场景 |

调研重点：

- 商业平台通常不会只强调“生成测试用例”，而是强调测试生命周期闭环
- 高价值能力集中在测试生成、测试选择、自愈、失败分析、测试报告和质量门禁
- 商业产品都会强调 Human-in-the-loop，只是包装程度不同

---

## 5. 开源 Agent 框架调研

Agent 框架适合用来理解底层实现方式，尤其是工作流编排、多 Agent 协作、工具调用和安全边界。

| 名称 | 链接 | 建议看什么 | 适合关注的问题 |
| --- | --- | --- | --- |
| LangGraph 官网 | [LangGraph](https://www.langchain.com/langgraph) | 工作流编排、人审节点、状态和记忆 | 如何表达测试任务流转 |
| LangGraph GitHub | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | README、examples、状态图设计 | 如何组织长任务和多步骤 Agent |
| OpenAI Agents SDK | [Agents SDK Python](https://openai.github.io/openai-agents-python/) | Agent、Runner、Tools、Handoffs、Guardrails、Tracing | 如何构建轻量可控 Agent |
| OpenAI Agents SDK 文档入口 | [OpenAI API Agents SDK](https://platform.openai.com/docs/guides/agents-sdk/) | SDK 定位、Python/TypeScript 入口 | 如何选择 SDK 与工程栈 |
| CrewAI GitHub | [crewAIInc](https://github.com/crewAIInc) | 多 Agent 角色协作、任务分配 | 如何表达团队式 Agent 协作 |
| CrewAI 官网 | [CrewAI](https://crewai.com/) | 快速开始、平台能力、企业工作流 | 如何包装业务流程型 Agent |
| Microsoft Agent Framework 文档 | [Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/) | Agents、Tools、Workflows、Host、Memory | 企业级 Agent 框架能力 |
| Microsoft Agent Framework GitHub | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | .NET/Python、工作流、可观测性、A2A/MCP | 企业技术栈中的 Agent 落地 |

调研重点：

- Agentic QA 不是单个 Prompt，而是可编排、可追踪、可约束的工作流
- 测试场景需要显式建模状态、输入、输出、失败分支和人工审核节点
- Guardrails、Tracing、Observability 对 QA 场景不是附加项，而是上线必要条件

---

## 6. MCP 与浏览器 Agent 调研

这一类资料最贴近“AI 做测试”，尤其适合研究 UI 自动化、黑盒测试生成、自愈测试和浏览器操作。

| 名称 | 链接 | 建议看什么 | 可用于什么测试场景 |
| --- | --- | --- | --- |
| MCP 官方文档 | [Model Context Protocol](https://modelcontextprotocol.io/) | MCP 如何连接工具、文件、数据库和外部系统 | Agent 工具接入规范 |
| MCP GitHub 组织 | [modelcontextprotocol](https://github.com/modelcontextprotocol) | 官方 SDK、Server、协议实现 | 后续接入工具链的协议参考 |
| Playwright MCP | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Accessibility snapshot、页面交互、MCP 配置 | UI 自动化生成、探索测试、自愈测试 |
| Playwright 主仓库 | [microsoft/playwright](https://github.com/microsoft/playwright) | Playwright Test、CLI、MCP 三种路径 | 判断何时用测试框架、CLI 或 MCP |
| Stagehand GitHub | [browserbase/stagehand](https://github.com/browserbase/stagehand) | act、extract、agent、自然语言 + 代码混合控制 | 浏览器 Agent 工程化 |
| Stagehand 文档 | [Stagehand Quickstart](https://docs.browserbase.com/welcome/quickstarts/stagehand) | 本地/云端浏览器、快速开始、Browserbase 集成 | 浏览器 Agent 执行环境 |
| browser-use GitHub | [browser-use/browser-use](https://github.com/browser-use/browser-use) | Python 浏览器 Agent、CLI、示例 | 本地浏览器自动化和探索 |
| browser-use 组织 | [browser-use](https://github.com/browser-use) | 浏览器 Agent 生态、Cloud、SDK | 自托管和平台化方案参考 |

调研重点：

- Playwright MCP 更适合让 LLM 基于页面结构进行浏览器交互
- Playwright Test 更适合稳定、可维护、可进入 CI 的自动化测试
- Stagehand 和 browser-use 更适合研究浏览器 Agent 的产品化和工程化形态
- 对企业测试来说，浏览器 Agent 的价值不只是“点页面”，而是辅助生成、修复和解释测试

---

## 7. 测试报告与质量分析平台

这一类资料适合研究测试结果如何进入质量决策闭环。

| 名称 | 链接 | 建议看什么 | 可借鉴点 |
| --- | --- | --- | --- |
| ReportPortal 文档 | [ReportPortal Docs](https://reportportal.io/docs/) | TestOps、实时结果、分析能力、CI 集成 | 自动化测试结果分析与质量门禁 |
| ReportPortal GitHub 组织 | [reportportal](https://github.com/reportportal) | 服务组成、Auto Analyzer、插件体系 | 报告平台架构和插件化能力 |
| ReportPortal 主仓库 | [reportportal/reportportal](https://github.com/reportportal/reportportal) | 部署结构、服务入口、License | 自建质量分析平台参考 |

调研重点：

- Agentic QA 的最后一环不是“生成报告”，而是形成可解释的质量结论
- 失败归因、趋势分析、缺陷关联和质量门禁应从一开始纳入设计
- 报告平台应服务发布决策，而不是只展示执行结果

---

## 8. 调研产出建议

每看完一类资料，建议沉淀一个具体产出，避免只停留在浏览链接。

| 调研阶段 | 建议产出 | 可落入仓库位置 |
| --- | --- | --- |
| 商业平台调研 | Agentic QA 能力地图 | `docs/` |
| Agent 框架调研 | Agent 工作流编排参考 | `docs/` 或 `references/` |
| MCP / 浏览器 Agent 调研 | UI Agent 能力边界和风险清单 | `skills/` 或 `docs/` |
| 测试报告平台调研 | 失败归因与质量门禁设计草案 | `standards/` 或 `templates/` |
| 综合调研 | Agentic QA 试点方案 | `docs/` |

---

## 9. 建议优先形成的仓库资产

结合当前仓库结构，建议优先沉淀以下资产：

1. `docs/architecture/agentic-qa-capability-map.md`  
   定义 Agentic QA 的能力地图、边界和优先级。

2. `docs/architecture/agentic-qa-workflow.md`  
   定义从需求、变更、执行、失败分析到质量报告的工作流。

3. `standards/ai_output_evaluation_standard.md`  
   定义 AI 输出完整性、正确性、可执行性、可追溯性和安全性评估标准。

4. `skills/regression-selection/SKILL.md`  
   沉淀代码变更驱动精准回归的方法。

5. `skills/failure-analysis/SKILL.md`  
   沉淀自动化失败归因、证据链整理和重跑建议方法。

6. `templates/regression_selection_template.md`  
   固定输出精准回归清单、风险级别和执行计划。

7. `templates/failure_analysis_template.md`  
   固定输出失败摘要、根因判断、证据链、影响范围和处理建议。

---

## 10. 当前判断

从资深测试工程师视角看，当前最值得优先研究和落地的不是“多 Agent 看起来很完整”，而是以下三个闭环：

1. 需求到测试用例  
   解决测试设计效率和覆盖完整性问题。

2. 代码变更到精准回归  
   解决发版回归范围不清、回归成本过高的问题。

3. 自动化失败到根因分析  
   解决自动化失败定位慢、误报多、维护成本高的问题。

其中最推荐优先落地的是“代码变更到精准回归”。原因是：

- 企业痛点明确
- 输入相对容易获取
- 输出容易验证
- 能自然接入 Git、CI、自动化用例和质量门禁
- 后续可以扩展为 Regression Selection Agent 和质量门禁规则

---

## 11. 阅读检查清单

阅读每个资料时，建议按以下问题记录结论：

- 它解决的是测试生命周期中的哪个环节
- 它依赖哪些输入数据
- 它输出什么测试资产或质量结论
- 它是否支持工具调用或真实执行
- 它如何处理失败、重试和人工审核
- 它是否提供可解释依据和审计能力
- 它有哪些权限、安全和数据风险
- 它的能力能否沉淀到当前仓库的 Agent、Skill、Standard 或 Template 中

---

## 12. 不建议的调研方式

不建议只做以下事情：

- 只收集链接，不整理能力地图
- 只看产品宣传，不看实际工作流
- 只看 Agent 框架，不结合测试场景
- 只关注自动生成，不关注失败路径
- 只关注 UI Agent，不关注数据、权限、报告和质量门禁
- 只追求“全自动”，忽略 Human-in-the-loop 和审计

调研最终应服务于仓库资产沉淀，而不是形成新的资料堆积。
