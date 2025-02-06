# Crawler
This project contains a web crawler that can:

Extract HTML content using Playwright and BeautifulSoup.
Summarize and transform the extracted content using LangChain and Mistral AI.
Either crawl only one URL (shallow) or recursively follow discovered links (deep).
 1. ### Overview
    Shallow Crawl: Fetch, parse, and summarize only the provided URL.
    Deep Crawl: Iteratively discover new links, store them, and process them until all discovered URLs are crawled.
    All extracted content is saved in Markdown format in data/processed, and the list of discovered URLs is tracked in a JSON file in data/raw.


2. ### CLI Usage
    The entry point is cli.py inside src/crawler/. You can run it with:

    ```python
    python -m src.crawler.cli [OPTIONS]

    ```
    Arguments:

    * --url: The base URL to crawl. Default: "https://www.google.com".
    * --api-key: Mistral AI API key. (Required if no environment variable is set.)
    * --output-file: The name (and extension) of the output file. Default: crawler.md.
    * --ai-prompt: Prompt for the AI summarization. Default: "Write a concise summary of the following".
    * --crawler-type:
    * --max-depth  Deep crawl with 1 level (start URL + immediate children) and Deep crawl with 2 levels (start URL + children + grandchildren)
    shallow: Crawl the single URL only.
    deep: Perform recursive crawling, storing & processing discovered links. Default: shallow.
    ### Example: Shallow Crawl
    ```python
    python -m src.crawler.cli \
    --url "https://www.fifa.com" \
    --output-file "FIFA.md" \
    --ai-prompt "Write a concise summary of the following, highlighting relevant information about the upcoming tournaments FIFA Club World Cup in 2025 or the FIFA World Cup in 2026 and answer clearly and  accurately questions related to the tournament, such as its history, participating teams, match schedules, results, stadiums and statistics. You should always ensure that the information provided is accurate and,  at the end of each answer, remind users to visit the official FIFA website for more detailed information." \
    --crawler-type deep  \
    --max-depth 1
    ```

3.  ###  Environment Variables
    MISTRAL_API_KEY: If you don't pass --api-key explicitly, the crawler will look for this environment variable.
    ```bash
    export MISTRAL_API_KEY="YOUR_MISTRAL_KEY"
    python -m src.crawler.cli --url "https://example.com"
    ```


python -m src.crawler.cli     --url "https://www.fifa.com/en/tournaments/mens/club-world-cup/usa-2025/articles/stadium-guide-venues-named"     --output-file "FIFA.md"     --ai-prompt "Write a concise summary of the following, highlighting relevant information about the upcoming tournaments FIFA Club World Cup in 2025 and stadiums and answer clearly and  accurately questions related to the tournament or about stadiums, such as its history, participating teams, match schedules, results, stadiums and statistics,why is important. You should always ensure that the information provided is accurate and,  at the end of each answer, remind users to visit the official FIFA website for more detailed information."     --crawler-type deep      --max-depth 1

FIFA_Club_World_Cup_2025_stadiums