
import os
import json
from datetime import datetime
from .scraper import extract_content_with_format
from .parser import extract_links_from_markdown
from .storage import save_to_readme
from urllib.parse import urlparse


def crawler(url: str, output_file: str, ai_prompt: str) -> list[str]:
    """
    Single-URL crawl:
      1. Extract the HTML content from `url`.
      2. Parse links out of that content.
      3. Save the textual summary to `data/processed` (via save_to_readme).
      4. Return the list of discovered URLs.
    """
    content = extract_content_with_format(url)
    list_urls = extract_links_from_markdown(url,content)
    save_to_readme(content, filename=output_file, ai_prompt=ai_prompt)

    print("URL processed:", url)
    print("Total of new URLs found:", len(list_urls))
    return list_urls


def load_crawled_data() -> dict:
    """
    Loads a JSON file from `data/raw/crawled_urls.json`.
    Returns an empty dict if the file does not exist.
    """
    os.makedirs("data/raw", exist_ok=True) 
    json_path = os.path.join("data", "raw", "crawled_urls.json")

    if not os.path.isfile(json_path):
        return {}

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f) 


def save_crawled_data(data: dict):
    """
    Saves `data` dict into `data/raw/crawled_urls.json`.
    """
    os.makedirs("data/raw", exist_ok=True) 
    json_path = os.path.join("data", "raw", "crawled_urls.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def crawl_deep(
    start_url: str,
    output_file: str,
    ai_prompt: str,
    max_depth: int = 1  
):
    """
    BFS approach with a maximum depth:
      - Keep a queue of (url, depth) to process.
      - If a url hasn't been processed, crawl it, mark it as processed in JSON.
      - For each new link found, if the depth < max_depth, add it to the queue.
    """
    base_domain = urlparse(start_url).netloc
    crawled_data = load_crawled_data()

    # If the starting URL is not in the dictionary, initialize it
    if start_url not in crawled_data:
        crawled_data[start_url] = {"processed": False, "read_at": None}

    # Queue: each element is a tuple (url, current_depth)
    queue = [(start_url, 0)]

    while queue:
        current_url, current_depth = queue.pop(0)

        # If already processed, skip
        if crawled_data[current_url]["processed"] is True:
            continue

        try:
            # Crawl this URL
            new_links = crawler(current_url, output_file, ai_prompt)
            
            # Mark as processed
            crawled_data[current_url]["processed"] = True
            crawled_data[current_url]["read_at"] = datetime.utcnow().isoformat()

            # If we haven't reached max_depth, enqueue discovered links
            if current_depth < max_depth:
                next_depth = current_depth + 1
                for link in new_links:
                    if link not in crawled_data:
                        crawled_data[link] = {"processed": False, "read_at": None}
                        queue.append((link, next_depth))

        except Exception as e:
            print(f"[ERROR] Failed to crawl {current_url}: {e}")

        # Save progress after each URL
        save_crawled_data(crawled_data)

    print("Crawling completed. Check data/raw/crawled_urls.json for details.")
    return crawled_data






