# news-crawler
A news crawler for Life-Long Learning LM
## Support website
|Media Name|Website|Spider Name|
|  :---:  | :---: |   :---:   |
|自由時報|news.ltn.com.tw|ltn|
|中央社|www.cna.com.tw|cna|
|中國時報|www.chinatimes.com|ct|
|三立新聞|www.setn.com|setn|

## How to use
`scrapy crawl <spider_name>`

- if you don't want to save data to database, you can delete NewsCrawlerPGStoragePipeline in setting.py
- you can change postgresql setting use environment variables, see more info in pipelines.py 


