from pydantic import BaseModel
from typing import List, Optional

class Article(BaseModel):
    title: Optional[str] = ""
    author: Optional[str] = ""
    link: Optional[str] = ""
    excerpt: Optional[str] = ""
    published_time: Optional[str] = ""

class ScrapingResult(BaseModel):
    status: str
    articles: List[Article] = []
    message: Optional[str] = None
