import re
from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from app.database import get_db
from app.urls.crud import create_crawdled_data, get_or_create_email

EMAIL_REGEX = r"([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)"


def crawl_url(url: HttpUrl):
    db = next(get_db())
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, features="html.parser")

    title: str = soup.title.text
    emails: List[str] = re.findall(EMAIL_REGEX, html)
    # images: List[str] = [img["src"] for img in soup.find_all("img")]

    emails = [get_or_create_email(db, i) for i in emails]
    # images = [get_or_create_image(db, i).id for i in images]

    create_crawdled_data(db, title, html, url=url, emails=emails, images=[])
    return title
