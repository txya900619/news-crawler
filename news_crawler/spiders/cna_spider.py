from news_crawler.pipelines import NewsCrawlerPGStoragePipeline
from news_crawler.utils import get_random_agent
from news_crawler.items import NewsCrawlerItem
from scrapy import Spider
from requests import post
from scrapy.http.request import Request
from datetime import datetime


class CentralNewsAgencyNewsSpider(Spider):
    name = "cna"

    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self.pg_pipeline: NewsCrawlerPGStoragePipeline = None

    def start_requests(self):
        page_index = 1
        duplicate_count = 0
        while(True):
            news_list_res = post(
                "https://www.cna.com.tw/cna2018api/api/WNewsList", json={"action": "0", "category": "aall", "pagesize": "99", "pageidx": page_index}, headers=get_random_agent())
            news_list_data = news_list_res.json()['ResultData']
            news_list = news_list_data['Items']
            for news in news_list:
                if self.pg_pipeline is not None:
                    if self.pg_pipeline.is_news_exist(news['PageUrl']):
                        duplicate_count += 1
                    else:
                        duplicate_count = 0
                    if duplicate_count > 4:
                        return
                section = news['ClassName']
                yield Request(url=news['PageUrl'], callback=lambda res: self.parse(res, section))
            if news_list_data['NextPageIdx'] == "":
                return
            page_index += 1

    def parse(self, response, section: str):
        title = response.css('div.centralContent h1 span::text').get()
        url = response.url
        content = '\n'.join(response.css('div.paragraph p::text').getall()).split(
            '（編輯')[0].split('（譯者')[0]
        keywords = ",".join(response.xpath(
            "//meta[@property='article:tag']/@content").getall()) or ""
        published_time = response.xpath(
            "//meta[@property='article:published_time']/@content").get()
        
        try:
            datetime.fromisoformat(published_time)
        except:
            published_time = published_time.replace("/", "-")
            published_time = published_time.replace(" ", "T")
            published_time += ":00"
            

        yield NewsCrawlerItem(title, content, url, section, keywords, datetime.fromisoformat(published_time))
