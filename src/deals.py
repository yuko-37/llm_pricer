import feedparser
import time
import re
import requests
from tqdm import tqdm
from typing import List, Self, Dict
from bs4 import BeautifulSoup
from pydantic import BaseModel

feed_urls = [
    "https://www.dealnews.com/c142/Electronics/?rss=1",
    "https://www.dealnews.com/c39/Computers/?rss=1",
    "https://www.dealnews.com/c238/Automotive/?rss=1",
    "https://www.dealnews.com/f1912/Smart-Home/?rss=1",
    "https://www.dealnews.com/c196/Home-Garden/?rss=1",
]


class ScrapedDeal:
    def __init__(self, entry: Dict[str, str | List[Dict]]):
        self.title = entry["title"].strip()
        self.summary = ScrapedDeal.extract_summary(entry["summary"])
        self.url = entry["links"][0]["href"]
        content = ScrapedDeal.extract_content(self.url)

        if "Features" in content:
            index = content.find("Features")
            details = content[:index]
            features = content[index + len("Features") :]
        else:
            details, features = content, ""
        self.details = details.strip()
        self.features = features.strip()

    def describe(self):
        return f"Title: {self.title}\nDetails: {self.details}\nFeatures: {self.features}\nURL: {self.url}"

    @staticmethod
    def extract_content(url):
        content = ""
        try:
            stuff = requests.get(url).content
            soup = BeautifulSoup(stuff, "html.parser")
            content = soup.find("div", class_="content-section").get_text()
            content = content.replace("\nmore", "").replace("\n", " ")
        except Exception as ex:
            print(f"Failed to extract content from [{url}]: {ex}")
        return content

    @staticmethod
    def extract_summary(html_snippet):
        soup = BeautifulSoup(html_snippet, "html.parser")
        snippet_div = soup.find("div", class_="snippet summary")

        if snippet_div:
            description = snippet_div.get_text(strip=True)
            description = BeautifulSoup(description, "html.parser").get_text()
            description = re.sub("<[^<]+?>", "", description)
            result = description.strip()
        else:
            result = html_snippet
        return result.replace("\n", " ")

    @classmethod
    def fetch(cls, show_progress: bool = False) -> List[Self]:
        deal_data_list = []
        feed_iter = tqdm(feed_urls) if show_progress else feed_urls
        for feed_url in feed_iter:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                deal_data = cls(entry)
                deal_data_list.append(deal_data)
                time.sleep(0.5)
        return deal_data_list


class Deal(BaseModel):
    product_description: str
    price: float
    url: str


class DealSelection(BaseModel):
    deals: List[Deal]
