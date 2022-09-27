import scrapy
from scrapy.http import HtmlResponse


class ScheduleSpider(scrapy.Spider):
    name = 'schedule'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com/',
                  'https://quotes.toscrape.com/tag/love/',
                  'https://quotes.toscrape.com/tag/inspirational/',
                  'https://quotes.toscrape.com/tag/life/',
                  'https://quotes.toscrape.com/tag/humor/',
                  'https://quotes.toscrape.com/tag/books/',
                  ]

    def parse(self, response: HtmlResponse, **kwargs):
        self.logger.info(f"status: {response.status}, response url: {response.url}")

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

    def close(self, spider, reason):
        self.logger.info(reason)
