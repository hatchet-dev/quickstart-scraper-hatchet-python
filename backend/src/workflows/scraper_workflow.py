import logging
from .hatchet import hatchet
from hatchet_sdk import Context
import requests
from bs4 import BeautifulSoup
import asyncio
from .models import Article, ScrapingResult

logger = logging.getLogger(__name__)

"""
Setup the workflow
This is the main workflow that will trigger both the TechCrunch and Google News scraping workflows.
It streams the progress and results to the client.
"""
@hatchet.workflow(on_events=["scraper:start"])
class ScraperWorkflow:
    
    @hatchet.step()
    async def start(self, context: Context):
        techcrunch_result = await (await context.aio.spawn_workflow("TechCrunchAIScraperWorkflow", {})).result()
        google_news_result = await (await context.aio.spawn_workflow("GoogleNewsScraperWorkflow", {})).result()

        return {
            "techCrunchArticles": techcrunch_result,
            "googleNewsArticles": google_news_result
        }

@hatchet.workflow(on_events=["scraper:techcrunch_ai_homepage"])
class TechCrunchAIScraperWorkflow:
    
    @hatchet.step(retries=3)
    async def fetch_homepage(self, context: Context):
        logger.info("Fetching TechCrunch AI homepage articles")
        url = "https://techcrunch.com/category/artificial-intelligence/"
        
        result = await asyncio.to_thread(self._fetch_homepage, url)
        return result

    def _fetch_homepage(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            articles_data = []
            for article in soup.find_all('div', class_='wp-block-tc23-post-picker')[:10]:  # Limit to first 10 articles
                title_element = article.find('h2', class_='wp-block-post-title')
                author_element = article.find('div', class_='wp-block-tc23-author-card-name')
                link_element = title_element.find('a', href=True) if title_element else None
                excerpt_element = article.find('div', class_='wp-block-post-excerpt__excerpt')
                time_element = article.find('time')
                image_element = article.find('img', src=True)

                if title_element and author_element and link_element:
                    articles_data.append({
                        "title": title_element.get_text(strip=True),
                        "author": author_element.get_text(strip=True),
                        "link": link_element['href'],
                        "excerpt": excerpt_element.get_text(strip=True) if excerpt_element else "",
                        "published_time": time_element.get_text(strip=True) if time_element else "",
                    })
            return {"status": "success", "articles": articles_data}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching TechCrunch AI homepage: {e}")
            return {"status": "error", "message": str(e)}

    @hatchet.step(parents=["fetch_homepage"])
    async def parse_articles(self, context: Context):
        step_output = context.step_output("fetch_homepage")
        
        if not isinstance(step_output, dict) or "articles" not in step_output:
            error_message = f"Error in TechCrunchAIScraperWorkflow: Invalid step output format"
            logger.error(error_message)
            raise Exception(error_message)

        parsed_articles = []
        for article_data in step_output.get("articles", [])[:10]: 
            parsed_articles.append(Article(
                title=article_data.get("title", ""),
                author=article_data.get("author", ""),
                link=article_data.get("link", ""),
                excerpt=article_data.get("excerpt", "")[:100] + "..." if article_data.get("excerpt") else "",
                published_time=article_data.get("published_time", ""),
            ))
        
        return {"status": "success", "articles": [article.dict() for article in parsed_articles]}

@hatchet.workflow(on_events=["scraper:google_news_homepage"])
class GoogleNewsScraperWorkflow:
    
    @hatchet.step(retries=3) 
    async def fetch_homepage(self, context: Context):
        logger.info("Fetching Google News homepage articles")
        url = "https://news.google.com/topstories"

        result = await asyncio.to_thread(self._fetch_homepage, url)
        return result 

    def _fetch_homepage(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            articles_data = []
            for article in soup.find_all('article'):
                link_element = article.find('a', href=True)
                title_element = article.find('a', class_='gPFEn')
                source_element = article.find('div', class_='vr1PYe')
                time_element = article.find('time')
                image_element = article.find('img', class_='Quavad', src=True)

                if link_element and title_element:
                    articles_data.append({
                        "title": title_element.get_text(strip=True),
                        "author": source_element.get_text(strip=True) if source_element else "Unknown Source",
                        "link": link_element['href'],
                        "published_time": time_element.get_text(strip=True) if time_element else "Unknown Time",
                    })

            return {"status": "success", "articles": articles_data}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Google News homepage: {e}")
            return {"status": "error", "message": str(e)}

    @hatchet.step(parents=["fetch_homepage"])
    async def parse_articles(self, context: Context):
        step_output = context.step_output("fetch_homepage")
        
        if not isinstance(step_output, dict) or "articles" not in step_output:
            error_message = f"Error in GoogleNewsScraperWorkflow: Invalid step output format"
            logger.error(error_message)
            raise Exception(error_message)

        parsed_articles = []
        for article_data in step_output.get("articles", [])[:10]: 
            parsed_articles.append(Article(
                title=article_data.get("title", ""),
                author=article_data.get("author", ""),
                link=f"https://news.google.com{article_data.get('link', '')[1:]}",
                published_time=article_data.get("published_time", ""),
            ))
        
        return {"status": "success", "articles": [article.dict() for article in parsed_articles]}