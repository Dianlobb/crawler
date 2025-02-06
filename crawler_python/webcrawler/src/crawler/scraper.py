from playwright.sync_api import sync_playwright
from .parser import langchain_docs_extractor

def extract_content_with_format(url: str) -> str:
    """
    Render page using Playwright and extract formatted content
    using the 'langchain_docs_extractor' function.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        )
        page = context.new_page()
        

        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_timeout(90000)  
        content = page.content()
        browser.close()

    return langchain_docs_extractor(content, include_output_cells=True)
