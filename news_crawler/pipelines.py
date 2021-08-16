# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import psycopg2
from news_crawler.items import NewsCrawlerItem


class NewsCrawlerPGStoragePipeline(object):

    def __init__(self) -> None:
        host = os.getenv("NEWSDB_HOST", "localhost")
        port = os.getenv("NEWSDB_PORT", "5432")
        database = os.getenv("NEWSDB_DATABASE", "postgres")
        user = os.getenv("NEWSDB_USER", "root")
        password = os.getenv("NEWSDB_PASS", "12345678")
        self.conn = psycopg2.connect(
            host=host, port=port, database=database, user=user, password=password)
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS news ("
                    "id SERIAL PRIMARY KEY,"
                    "title TEXT NOT NULL,"
                    "content TEXT NOT NULL,"
                    "url TEXT NOT NULL UNIQUE,"
                    "section TEXT NOT NULL,"
                    "keywords TEXT NOT NULL,"
                    "published_time TIMESTAMPTZ"
                    ")"
                    )
        cur.close()
        self.conn.commit()

    def open_spider(self, spider):
        spider.pg_pipeline = self

    def process_item(self, item: NewsCrawlerItem, spider):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO news(title, content, url, section, keywords, published_time) "
                    "VALUES ( %(title)s, %(content)s, %(url)s, %(section)s, %(keywords)s, %(published_time)s) "
                    "ON CONFLICT(url) "
                    "DO "
                    "UPDATE SET content=EXCLUDED.content, title=EXCLUDED.title, keywords=EXCLUDED.keywords", item)
        cur.close()
        self.conn.commit()
        return item

    def is_news_exist(self, url: str) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            "select exists ( select 1 from news where url= %s )", (url,))
        result = cur.fetchone()[0]
        cur.close()
        return result
