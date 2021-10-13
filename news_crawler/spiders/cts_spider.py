from requests.api import get
from news_crawler.pipelines import NewsCrawlerPGStoragePipeline
from news_crawler.utils import get_random_agent
from news_crawler.items import NewsCrawlerItem
from scrapy import Spider
from requests import post
from scrapy.http.request import Request
from datetime import date, datetime


class ChineseTelevisionServiceNewsSpider(Spider):
    name = "cts"
    start_urls = ["https://news.cts.com.tw/real/index.html"]

    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self.pg_pipeline: NewsCrawlerPGStoragePipeline = None

    def parse(self, response):
        duplicate_count = 0

        news_urls = response.css(
            '.left-container .newslist-container a::attr(href)').getall()

        for news_url in news_urls:
            if self.pg_pipeline is not None:
                if self.pg_pipeline.is_news_exist(news_url):
                    duplicate_count += 1
                else:
                    duplicate_count = 0
                if duplicate_count > 4:
                    return

            yield Request(news_url, callback=self.parse_news)

    def parse_news(self, response):
        title: str = response.css(".artical-title::text").get()

        lines: list = response.xpath(
            "//div[contains(@class,'artical-content')]//p[not(@class)]/text()").getall()
        filtered_lines: list = [
            line for line in lines if u'報導 \xa0/' not in line]
        content: str = '\n'.join(filtered_lines)

        url: str = response.url
        section: str = response.xpath(
            "//meta[@name='section']/@content").get()
        keywords: str = response.xpath(
            "//meta[@name='news_keywords']/@content").get()
        published_time: datetime = response.xpath(
            "//meta[@name='pubdate']/@content").get()

        yield NewsCrawlerItem(title, content, url, section, keywords, datetime.fromisoformat(published_time))
