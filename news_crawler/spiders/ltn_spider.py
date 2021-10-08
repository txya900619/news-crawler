from news_crawler.pipelines import NewsCrawlerPGStoragePipeline
from news_crawler.utils import get_random_agent
from news_crawler.items import NewsCrawlerItem
from scrapy import Spider
from requests import get
from scrapy.http.request import Request
from datetime import datetime


class LibertyTimesNewsSpider(Spider):
    name = "ltn"

    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self.pg_pipeline: NewsCrawlerPGStoragePipeline = None

    def start_requests(self):
        page_index = 1
        duplicate_count = 0
        while(True):
            news_list_res = get(
                "https://news.ltn.com.tw/ajax/breakingnews/all/{}".format(page_index), headers=get_random_agent())
            if news_list_res.status_code != 200:
                continue
            news_list = news_list_res.json()['data']
            if len(news_list) == 0:
                return
            if type(news_list) is dict:
                news_list = news_list.values()
            for news in news_list:
                if self.pg_pipeline is not None:
                    if self.pg_pipeline.is_news_exist(news['url']):
                        duplicate_count += 1
                    else:
                        duplicate_count = 0
                    if duplicate_count > 4:
                        return
                yield Request(url=news['url'], callback=self.parse)
            page_index += 1

    def parse(self, response):
        title = response.css('div.whitecon h1::text').get()
        url = response.url
        content = '\n'.join(response.xpath(
            "//div[contains(@class,'text')]/p[not(a) and not(@class)]/text()").getall())
        section = response.xpath(
            "//meta[@property='article:section']/@content").get()
        keywords = response.xpath(
            "//meta[@name='keywords']/@content").get()
        published_time = response.xpath(
            "//meta[@property='article:published_time']/@content").get()
        if published_time is None:
            published_time = "{}:00+08:00".format(
                response.css('span.time::text').get()).replace("/", "-")

        yield NewsCrawlerItem(title, content, url, section, keywords, datetime.fromisoformat(published_time))
