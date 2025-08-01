"""
# news.py
This module provides functions to find and download news articles using Google News.
It allows searching for articles by keyword, location, or topic, and can also retrieve google trending terms.
It uses the `gnews` library to search for news articles and trendspy to get Google Trends data.
It will fallback to using Playwright for websites that are difficult to scrape with newspaper4k or cloudscraper.
"""

import re
import json
import asyncio
from gnews import GNews
import newspaper  # newspaper4k
from googlenewsdecoder import gnewsdecoder
import cloudscraper
from playwright.async_api import async_playwright, Browser, Playwright
from trendspy import Trends, TrendKeywordLite
from typing import Optional, cast, overload, Literal, Awaitable
from contextlib import asynccontextmanager, AsyncContextDecorator
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)

for logname in logging.root.manager.loggerDict:
    if logname.startswith("newspaper"):
        logging.getLogger(logname).setLevel(logging.ERROR)

tr = Trends()

scraper = cloudscraper.create_scraper(
    interpreter="js2py",  # Best compatibility for v3 challenges
    delay=5,  # Extra time for complex challenges
    # enable_stealth=True,
    # stealth_options={
    #     'min_delay': 2.0,
    #     'max_delay': 6.0,
    #     'human_like_delays': True,
    #     'randomize_headers': True,
    #     'browser_quirks': True
    # },
    browser="chrome",
    debug=False,
)

google_news = GNews(
    language="en",
    # exclude_websites=[],
)

ProgressCallback = Callable[[float, Optional[float]], Awaitable[None]]


class BrowserManager(AsyncContextDecorator):
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _lock = asyncio.Lock()
    _class_contexts: int = 0

    @classmethod
    async def _get_browser(cls) -> Browser:
        if cls._browser is None:
            async with cls._lock:
                if cls._browser is None:
                    logger.info("Starting browser...")
                    try:
                        cls._playwright = await async_playwright().start()
                        cls._browser = await cls._playwright.chromium.launch(headless=True)
                    except Exception as e:
                        logger.critical("Browser startup failed", exc_info=e)
                        raise SystemExit(1)
        return cast(Browser, cls._browser)

    @classmethod
    async def _shutdown(cls):
        logger.info("Shutting down browser...")
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None

    @classmethod
    def browser_context(cls):
        @asynccontextmanager
        async def _browser_context_cm():
            if cls._class_contexts == 0:
                raise RuntimeError("BrowserManager used without context. Wrap in 'async with BrowserManager()'.")
            browser_inst = await cls._get_browser()
            context = await browser_inst.new_context()
            logger.debug("Created browser context...")
            try:
                yield context
            finally:
                logger.debug("Closing browser context...")
                await context.close()

        return _browser_context_cm()

    async def __aenter__(self):
        type(self)._class_contexts += 1
        return self

    async def __aexit__(self, *exc):
        type(self)._class_contexts -= 1
        await self._shutdown()
        return False


async def download_article_with_playwright(url) -> newspaper.Article | None:
    """
    Download an article using Playwright to handle complex websites (async).
    """
    async with BrowserManager.browser_context() as context:
        try:
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(2)  # Wait for the page to load completely
            content = await page.content()
            article = newspaper.article(url, input_html=content)
            return article
        except Exception as e:
            logger.warning(f"Error downloading article with Playwright from {url}\n {e.args}")
            return None


def download_article_with_scraper(url) -> newspaper.Article | None:
    article = None
    try:
        article = newspaper.article(url)
    except Exception as e:
        logger.debug(f"Error downloading article with newspaper from {url}\n {e.args}")
        try:
            # Retry with cloudscraper
            response = scraper.get(url)
            if response.status_code < 400:
                article = newspaper.article(url, input_html=response.text)
            else:
                logger.debug(
                    f"Failed to download article with cloudscraper from {url}, status code: {response.status_code}"
                )
        except Exception as e:
            logger.debug(f"Error downloading article with cloudscraper from {url}\n {e.args}")
    return article


def decode_url(url: str) -> str:
    if url.startswith("https://news.google.com/rss/"):
        try:
            decoded_url = gnewsdecoder(url)
            if decoded_url.get("status"):
                return decoded_url["decoded_url"]
            else:
                logger.debug("Failed to decode Google News RSS link:")
        except Exception as err:
            logger.warning(f"Error while decoding url {url}\n {err.args}")
    return ""


async def download_article(url: str) -> newspaper.Article | None:
    """
    Download an article from a given URL using newspaper4k and cloudscraper (async).
    """
    if not (url := decode_url(url)):
        return None
    article = download_article_with_scraper(url)
    if article is None or not article.text:
        logger.debug("Attempting to download article with playwright")
        article = await download_article_with_playwright(url)
    return article


async def process_gnews_articles(
    gnews_articles: list[dict],
    nlp: bool = True,
    report_progress: Optional[ProgressCallback] = None,
) -> list[newspaper.Article]:
    """
    Process a list of Google News articles and download them (async).
    Optionally report progress via report_progress callback.
    """
    articles = []
    total = len(gnews_articles)
    for idx, gnews_article in enumerate(gnews_articles):
        article = await download_article(gnews_article["url"])
        if article is None or not article.text:
            logger.debug(f"Failed to download article from {gnews_article['url']}:\n{article}")
            continue
        article.parse()
        if nlp:
            article.nlp()
        articles.append(article)
        if report_progress:
            await report_progress(idx, total)
    return articles


async def get_news_by_keyword(
    keyword: str,
    period=7,
    max_results: int = 10,
    nlp: bool = True,
    report_progress: Optional[ProgressCallback] = None,
) -> list[newspaper.Article]:
    """
    Find articles by keyword using Google News.
    """
    google_news.period = f"{period}d"
    google_news.max_results = max_results
    gnews_articles = google_news.get_news(keyword)
    if not gnews_articles:
        logger.debug(f"No articles found for keyword '{keyword}' in the last {period} days.")
        return []
    return await process_gnews_articles(gnews_articles, nlp=nlp, report_progress=report_progress)


async def get_top_news(
    period: int = 3,
    max_results: int = 10,
    nlp: bool = True,
    report_progress: Optional[ProgressCallback] = None,
) -> list[newspaper.Article]:
    """
    Get top news stories from Google News.
    """
    google_news.period = f"{period}d"
    google_news.max_results = max_results
    gnews_articles = google_news.get_top_news()
    if not gnews_articles:
        logger.debug("No top news articles found.")
        return []
    return await process_gnews_articles(gnews_articles, nlp=nlp, report_progress=report_progress)


async def get_news_by_location(
    location: str,
    period=7,
    max_results: int = 10,
    nlp: bool = True,
    report_progress: Optional[ProgressCallback] = None,
) -> list[newspaper.Article]:
    """Find articles by location using Google News."""
    google_news.period = f"{period}d"
    google_news.max_results = max_results
    gnews_articles = google_news.get_news_by_location(location)
    if not gnews_articles:
        logger.debug(f"No articles found for location '{location}' in the last {period} days.")
        return []
    return await process_gnews_articles(gnews_articles, nlp=nlp, report_progress=report_progress)


async def get_news_by_topic(
    topic: str,
    period=7,
    max_results: int = 10,
    nlp: bool = True,
    report_progress: Optional[ProgressCallback] = None,
) -> list[newspaper.Article]:
    """Find articles by topic using Google News.
    topic is one of
    WORLD, NATION, BUSINESS, TECHNOLOGY, ENTERTAINMENT, SPORTS, SCIENCE, HEALTH,
    POLITICS, CELEBRITIES, TV, MUSIC, MOVIES, THEATER, SOCCER, CYCLING, MOTOR SPORTS,
    TENNIS, COMBAT SPORTS, BASKETBALL, BASEBALL, FOOTBALL, SPORTS BETTING, WATER SPORTS,
    HOCKEY, GOLF, CRICKET, RUGBY, ECONOMY, PERSONAL FINANCE, FINANCE, DIGITAL CURRENCIES,
    MOBILE, ENERGY, GAMING, INTERNET SECURITY, GADGETS, VIRTUAL REALITY, ROBOTICS, NUTRITION,
    PUBLIC HEALTH, MENTAL HEALTH, MEDICINE, SPACE, WILDLIFE, ENVIRONMENT, NEUROSCIENCE, PHYSICS,
    GEOLOGY, PALEONTOLOGY, SOCIAL SCIENCES, EDUCATION, JOBS, ONLINE EDUCATION, HIGHER EDUCATION,
    VEHICLES, ARTS-DESIGN, BEAUTY, FOOD, TRAVEL, SHOPPING, HOME, OUTDOORS, FASHION.
    """
    google_news.period = f"{period}d"
    google_news.max_results = max_results
    gnews_articles = google_news.get_news_by_topic(topic)
    if not gnews_articles:
        logger.debug(f"No articles found for topic '{topic}' in the last {period} days.")
        return []
    return await process_gnews_articles(gnews_articles, nlp=nlp, report_progress=report_progress)


@overload
async def get_trending_terms(geo: str = "US", full_data: Literal[False] = False) -> list[dict[str, str]]: ...


@overload
async def get_trending_terms(geo: str = "US", full_data: Literal[True] = True) -> list[TrendKeywordLite]: ...


async def get_trending_terms(geo: str = "US", full_data: bool = False) -> list[dict[str, str]] | list[TrendKeywordLite]:
    """
    Returns google trends for a specific geo location.
    """
    try:
        trends = cast(list[TrendKeywordLite], tr.trending_now_by_rss(geo=geo))
        trends = sorted(trends, key=lambda tt: int(tt.volume[:-1]), reverse=True)
        if not full_data:
            return [{"keyword": trend.keyword, "volume": trend.volume} for trend in trends]
        return trends
    except Exception as e:
        logger.warning(f"Error fetching trending terms: {e}")
        return []


def save_article_to_json(article: newspaper.Article, filename: str = "") -> None:
    def sanitize_filename(title: str) -> str:
        """
        # save Article to json file
        # filename is based on the article title
        # if the title is too long, it will be truncated to 50 characters
        # and replaced with underscores if it contains any special characters
        """
        # Replace special characters and spaces with underscores, then truncate to 50 characters
        sanitized_title = re.sub(r'[\\/*?:"<>|\s]', "_", title)[:50]
        return sanitized_title + ".json"

    """
    Save an article to a JSON file.
    """
    article_data = {
        "title": article.title,
        "authors": article.authors,
        "publish_date": str(article.publish_date) if article.publish_date else None,
        "top_image": article.top_image,
        "images": article.images,
        "text": article.text,
        "url": article.original_url,
        "summary": article.summary,
        "keywords": article.keywords,
        "keyword_scores": article.keyword_scores,
        "tags": article.tags,
        "meta_keywords": article.meta_keywords,
        "meta_description": article.meta_description,
        "canonical_link": article.canonical_link,
        "meta_data": article.meta_data,
        "meta_lang": article.meta_lang,
        "source_url": article.source_url,
    }

    if not filename:
        # Use the article title to create a filename
        filename = sanitize_filename(article.title)
    else:
        # Ensure the filename ends with .json
        if not filename.endswith(".json"):
            filename += ".json"
    with open(filename, "w") as f:
        json.dump(article_data, f, indent=4)
    logger.debug(f"Article saved to {filename}")
