import scrapy


class JdbookSpider(scrapy.Spider):
    name = 'jdbook'
    allowed_domains = ['jd.com']
    start_urls = ['https://list.jd.com/list.html?cat=1713,3258,3297']

    def parse(self, response):
        book_list = response.xpath('//*[@id="J_goodsList"]/ul/li/div')
        for book in book_list:
            item = {}

            # item['big_category'] = temp['big_category']
            # item['big_category_link'] = temp['big_category_link']
            # item['small_category'] = temp['small_category']
            # item['small_category_link'] = temp['small_category_link']

            item['book_name'] = book.xpath('./div[3]/a/em/text()').extract_first().strip()
            item['link'] = response.urljoin(book.xpath('./div[1]/a/@href').extract_first())
            item['author'] = book.xpath('./div[4]/span/a/text()').extract_first().strip()
            item['price'] = book.xpath('./div[2]/strong/i/text()').extract_first()
            item['img_cover'] = response.urljoin(book.xpath('./div[1]/a/img/@data-lazy-img').extract_first())

            print(item)
            # yield item


