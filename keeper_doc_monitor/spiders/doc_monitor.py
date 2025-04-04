import scrapy
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path
import html2text

class KeeperDocsSpider(scrapy.Spider):
    name = "keeper_docs"
    allowed_domains = ["docs.keeper.io"]
    start_urls = ["https://docs.keeper.io/en/keeperpam/"]

    def parse(self, response):
        # Extract path after /en/keeperpam/
        parsed = urlparse(response.url)
        relative_path = parsed.path.replace("/en/keeperpam/", "").strip("/")
        if not relative_path:
            relative_path = "index"
        if relative_path.endswith("/"):
            relative_path = relative_path.rstrip("/")

        html_content = response.css("body").get()
        content = html2text.html2text(html_content) if html_content else "[NO CONTENT FOUND]"

        # Determine output path (nested folders okay)
        output_path = Path("output") / Path(relative_path).with_suffix(".md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Saving {response.url} to {output_path}")
        with open (output_path, "w", encoding='utf-8') as f:
            f.write(content)

        # Follow valid subpage links
        for href in response.css("a::attr(href)").getall():
            full_url = urljoin(response.url, href)
            if full_url.startswith("https://docs.keeper.io/en/keeperpam/"):
                yield response.follow(full_url, self.parse)
