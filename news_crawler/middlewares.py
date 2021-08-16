# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging

from news_crawler.utils import get_random_agent

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
        request.headers.setdefault(
            'User-Agent', get_random_agent()['User-Agent'])
