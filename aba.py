import asyncio
from aiolimiter import AsyncLimiter
import httpx
count = 0
async def fetch(url, limiter, semaphore):
    async with semaphore:  # 控制并发数
        async with limiter:  # 控制每秒请求数
            async with httpx.AsyncClient() as client:
                await client.get(url)
                global count
                count += 1
                print(count)


async def main():
    url = "https://www.baidu.com"  # 替换为实际的 API 地址
    limiter = AsyncLimiter(10, 1)  # 每秒最多100个请求
    semaphore = asyncio.Semaphore(5)  # 并发最多10个请求

    tasks = [asyncio.ensure_future(fetch(url, limiter, semaphore)) for _ in range(300)]
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
