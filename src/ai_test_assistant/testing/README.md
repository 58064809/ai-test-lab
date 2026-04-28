# Testing 模块说明

## 当前状态

当前模块已实现 **pytest_runner 最小真实执行 adapter**。

定位必须明确：

- 这是对成熟 `pytest` 的薄封装
- 不是自研测试框架
- 不是 shell 通用执行器
- 当前不接 Allure

## 已实现

- `PytestRunner`
- `PytestRunResult`
- 使用当前 Python 解释器执行：`sys.executable -m pytest <target>`
- `subprocess.run(args=list, shell=False)` 安全执行
- 默认 target 为 `tests`
- target 只允许仓库内相对路径
- 拒绝绝对路径、`..` 路径穿越、glob 和额外参数注入
- stdout / stderr 长度限制

## 当前限制

- 当前只允许运行仓库内 pytest 目标
- 当前不支持任意 pytest 参数
- 当前不支持 shell 命令
- 当前不生成 Allure 报告
- 当前不访问外部网络
- 当前不修改项目文件

## 明确不做

- 不自研测试框架
- 不实现 shell 通用执行器
- 不开放任意本地命令执行
- 不支持仓库外路径
- 不支持 glob
