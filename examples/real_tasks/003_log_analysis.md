# 003｜日志分析任务验证

## 任务

请你作为高级测试工程师分析以下日志。

## 日志

```text
2026-05-07 10:12:01 INFO  request_id=abc123 api=/api/order/create user_id=10001 start
2026-05-07 10:12:01 INFO  request_id=abc123 check stock sku_id=SKU001 available=0
2026-05-07 10:12:01 ERROR request_id=abc123 order create failed error=StockNotEnoughException message="stock not enough"
2026-05-07 10:12:01 INFO  request_id=abc123 rollback coupon coupon_id=C001 success=true
2026-05-07 10:12:01 INFO  request_id=abc123 rollback points points=100 success=true
2026-05-07 10:12:01 WARN  request_id=abc123 payment prepay skipped reason=order_create_failed
```

## 输出要求

1. 判断失败发生在哪个环节；
2. 提取关键 `request_id`、接口、用户、SKU、异常类型；
3. 分析是否存在数据一致性风险；
4. 判断补偿/回滚是否完整；
5. 给出下一步排查建议；
6. 如果信息不足，请明确说明还需要哪些日志或数据库字段；
7. 输出中文，结论要明确，不要只复述日志。
