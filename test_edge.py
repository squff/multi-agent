import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        # 使用系统安装的 Microsoft Edge
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,
        )
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")
        print(f"页面标题: {await page.title()}")
        await page.screenshot(path="edge_baidu.png")
        print("截图已保存: edge_baidu.png")
        await browser.close()


asyncio.run(main())
