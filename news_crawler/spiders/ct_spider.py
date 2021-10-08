from news_crawler.pipelines import NewsCrawlerPGStoragePipeline
from news_crawler.items import NewsCrawlerItem
from scrapy import Spider
from scrapy.http.request import Request
from datetime import datetime


class ChinaTimesNewsSpider(Spider):
    name = "ct"
    start_urls = ["https://www.chinatimes.com/realtimenews/?page=1&chdtv"]
    duplicate_count = 0

    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self.pg_pipline: NewsCrawlerPGStoragePipeline = None

    def parse(self, response):
        news_in_page = response.css(
            ".article-list .vertical-list li h3.title a")
        if not news_in_page:
            return

        for news in news_in_page:
            news_url = news.css('a::attr(href)').extract_first()
            news_url = f"{response.urljoin(news_url)}?chdtv"

            if self.pg_pipline is not None:
                if self.pg_pipline.is_news_exist(news_url):
                    self.duplicate_count += 1
                else:
                    self.duplicate_count = 0
                if self.duplicate_count > 4:
                    return

            yield Request(news_url, callback=self.parse_news)

        next_page_url = response.css(
            "ul.pagination :nth-last-child(2) a::attr(href)").extract_first()
        if not next_page_url:
            return

        next_page_url = f"{response.urljoin(next_page_url)}&chdtv"
        yield Request(next_page_url, callback=self.parse)

    def parse_news(self, response):
        title: str = response.css("h1.article-title::text").get()
        content: str = "\n".join(response.css(
            ".article-body p::text").getall())
        url: str = response.url
        section: str = response.xpath(
            "//meta[@property='article:section']/@content").get()
        keywords: str = response.xpath(
            "//meta[@name='keywords']/@content").get()
        published_time: datetime = response.xpath(
            "//meta[@itemprop='datePublished']/@content").get()
        yield NewsCrawlerItem(title, content, url, section, keywords, datetime.fromisoformat(published_time))
