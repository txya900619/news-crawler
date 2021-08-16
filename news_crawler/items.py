# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsCrawlerItem:
    title: str
    content: str
    url: str
    section: str
    keywords: str
    published_time: datetime

    def __getitem__(self, key):
        return super().__getattribute__(key)
