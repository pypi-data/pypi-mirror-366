import click
import asyncio
from google_news_trends_mcp.news import (
    get_news_by_keyword,
    get_news_by_location,
    get_news_by_topic,
    get_trending_terms,
    get_top_news,
    save_article_to_json,
    BrowserManager,
)
import logging

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command(help=get_news_by_keyword.__doc__)
@click.argument("keyword")
@click.option("--period", type=int, default=7, help="Period in days to search for articles.")
@click.option(
    "--max-results",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return.",
)
@click.option("--no-nlp", is_flag=True, default=False, help="Disable NLP processing for articles.")
def keyword(keyword, period, max_results, no_nlp):
    @BrowserManager()
    async def _keyword():
        articles = await get_news_by_keyword(keyword, period=period, max_results=max_results, nlp=not no_nlp)
        print_articles(articles)
        logger.info(f"Found {len(articles)} articles for keyword '{keyword}'.")

    asyncio.run(_keyword())


@cli.command(help=get_news_by_location.__doc__)
@click.argument("location")
@click.option("--period", type=int, default=7, help="Period in days to search for articles.")
@click.option(
    "--max-results",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return.",
)
@click.option("--no-nlp", is_flag=True, default=False, help="Disable NLP processing for articles.")
def location(location, period, max_results, no_nlp):
    @BrowserManager()
    async def _location():
        articles = await get_news_by_location(location, period=period, max_results=max_results, nlp=not no_nlp)
        print_articles(articles)
        logger.info(f"Found {len(articles)} articles for location '{location}'.")

    asyncio.run(_location())


@cli.command(help=get_news_by_topic.__doc__)
@click.argument("topic")
@click.option("--period", type=int, default=7, help="Period in days to search for articles.")
@click.option(
    "--max-results",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return.",
)
@click.option("--no-nlp", is_flag=True, default=False, help="Disable NLP processing for articles.")
def topic(topic, period, max_results, no_nlp):
    @BrowserManager()
    async def _topic():
        articles = await get_news_by_topic(topic, period=period, max_results=max_results, nlp=not no_nlp)
        print_articles(articles)
        logger.info(f"Found {len(articles)} articles for topic '{topic}'.")

    asyncio.run(_topic())


@cli.command(help=get_trending_terms.__doc__)
@click.option("--geo", type=str, default="US", help="Country code, e.g. 'US', 'GB', 'IN', etc.")
@click.option("--full-data", is_flag=True, default=False, help="Return full data for each trend.")
def trending(geo, full_data):
    # Browser not used for Google Trends
    async def _trending():
        trending_terms = await get_trending_terms(geo=geo, full_data=full_data)
        if trending_terms:
            logger.info("Trending terms:")
            for term in trending_terms:
                if isinstance(term, dict):
                    logger.info(f"{term['keyword']:<40} - {term['volume']}")
                else:
                    logger.info(term)
        else:
            logger.info("No trending terms found.")

    asyncio.run(_trending())


@cli.command(help=get_top_news.__doc__)
@click.option("--period", type=int, default=3, help="Period in days to search for top articles.")
@click.option(
    "--max-results",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return.",
)
@click.option("--no-nlp", is_flag=True, default=False, help="Disable NLP processing for articles.")
def top(period, max_results, no_nlp):
    @BrowserManager()
    async def _top():
        articles = await get_top_news(max_results=max_results, period=period, nlp=not no_nlp)
        print_articles(articles)
        logger.info(f"Found {len(articles)} top articles.")

    asyncio.run(_top())


def print_articles(articles):
    for article in articles:
        logger.info(f"Title: {article.title}")
        logger.info(f"URL: {article.original_url}")
        logger.info(f"Authors: {article.authors}")
        logger.info(f"Publish Date: {article.publish_date}")
        logger.info(f"Top Image: {article.top_image}")
        logger.info(f"Summary: {article.summary}\n")
        save_article_to_json(article)


if __name__ == "__main__":
    cli()
