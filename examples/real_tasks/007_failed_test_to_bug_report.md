# 007｜失败测试结果生成缺陷报告任务验证

## 任务

请根据以下失败测试结果生成缺陷报告。

## 失败信息

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

## 输出要求

1. 输出缺陷标题；
2. 输出严重级别；
3. 输出优先级；
4. 输出前置条件；
5. 输出复现步骤；
6. 输出预期结果；
7. 输出实际结果；
8. 输出初步定位；
9. 输出建议补充排查信息；
10. 语言专业、简洁，适合提交到缺陷系统；
11. 不要编造日志或数据库字段，信息不足时明确说明。
