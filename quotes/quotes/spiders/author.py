import scrapy
from scrapy.http import HtmlResponse


class AuthorSpider(scrapy.Spider):
    name = 'author'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response: HtmlResponse, **kwargs):
        self.logger.info(f"status: {response.status}, response url: {response.url}, request url: {response.request}")

        author_page_links = response.css('.author + a')
        yield from response.follow_all(author_page_links, self.parse_author)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_author(self, response: HtmlResponse):
        self.logger.info(f"<Author> status: {response.status}, response url: {response.url}")

        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }
