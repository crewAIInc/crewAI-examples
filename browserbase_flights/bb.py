import os
from crewai_tools import tool
from playwright.sync_api import sync_playwright
from html2text import html2text
from time import sleep


@tool("Browserbase tool")
def browserbase(url: str):
    """
    Loads a URL using a headless webbrowser
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(
            "wss://connect.browserbase.com?apiKey=" + os.environ["BROWSERBASE_API_KEY"]
        )
        context = browser.contexts[0]
        page = context.pages[0]
        page.goto(url)

        sleep(5)

        page.screenshot(path="screenshot.png")
        content = html2text(page.content())
        browser.close()
        return content
