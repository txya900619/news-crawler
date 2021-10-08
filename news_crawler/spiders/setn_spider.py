from news_crawler.pipelines import NewsCrawlerPGStoragePipeline
from news_crawler.items import NewsCrawlerItem
from scrapy import Spider
from scrapy.http.request import Request
from datetime import datetime


class SanlihETelevisionNewsSpider(Spider):
    name = "setn"
    start_urls = ["https://www.setn.com/ViewAll.aspx?p=1"]
    page_index = 1
    duplicate_count = 0

    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self.pg_pipeline: NewsCrawlerPGStoragePipeline = None

    def parse(self, response):
        news_in_page = response.css(
            "div.NewsList h3.view-li-title a")
        if not news_in_page:
            return

        for news in news_in_page:
            news_url = news.css('a::attr(href)').extract_first()
            if "https" not in news_url:
                news_url = response.urljoin(news_url)

            if self.pg_pipeline is not None:
                if self.pg_pipeline.is_news_exist(news_url):
                    self.duplicate_count += 1
                else:
                    self.duplicate_count = 0
                if self.duplicate_count > 4:
                    return

            yield Request(news_url, callback=self.parse_news)

        self.page_index += 1
        if self.page_index > 20:
            return

        next_page_url = f"https://www.setn.com/ViewAll.aspx?p={self.page_index}"
        yield Request(next_page_url, callback=self.parse)

    def parse_news(self, response):
        title: str = response.xpath(
            "//meta[@property='og:title']/@content").get().split(" | ")[0]
        content: str = '\n'.join(response.xpath(
            "//article//p[not(@class)]/text()").getall())
        url: str = response.url
        section: str = response.xpath(
            "//meta[@property='article:section']/@content").get()
        keywords: str = response.xpath(
            "//meta[@name='news_keywords']/@content").get()
        published_time: datetime = response.xpath(
            "//meta[@property='article:published_time']/@content").get()

        if "z" in published_time:
            published_time.replace("z", "")
        published_time += "+08:00"
        yield NewsCrawlerItem(title, content, url, section, keywords, datetime.fromisoformat(published_time))
