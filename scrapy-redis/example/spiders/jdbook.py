from scrapy_redis.spiders import RedisSpider
import scrapy
import json
import urllib
from copy import deepcopy


# class BookSpider(scrapy.Spider):
class BookSpider(RedisSpider):
    name = 'jd'
    allowed_domains = ['jd.com', 'p.3.cn']
    # start_urls = ['https://book.jd.com/booksort.html']
    redis_key = 'jd:start_urls'

    def parse(self, response, **kwargs):
        item = {}
        # 大分类
        dt_list = response.xpath('//div[@class="mc"]/dl/dt')
        for dt in dt_list:
            item['b_cate'] = dt.xpath('./a/text()').extract_first()  # 大分类title
            em_list = dt.xpath('./following-sibling::dd[1]/em')
            # 小分类
            for em in em_list:
                item['s_cate'] = em.xpath('./a/text()').extract_first()
                item['s_href'] = em.xpath('./a/@href').extract_first()
                if item['s_href'] is not None:
                    item['s_href'] = 'https:' + item['s_href']
                # 构造请求
                yield scrapy.Request(
                    item['s_href'],
                    callback=self.parse_book_list,
                    meta={'item': deepcopy(item)}  # 深拷贝，给item一个空间，防止数据重复
                )

    # 解析书列表页
    def parse_book_list(self, response):
        item = response.meta['item']
        li_list = response.xpath('//div[@id="plist"]/ul/li')
        for li in li_list:
            item['book_name'] = li.xpath('.//div[@class="p-name"]/a/em/text()').extract_first().strip()
            item['book_href'] = 'https:' + li.xpath('.//div[@class="p-img"]/a/@href').extract_first()
            item['book_img'] = li.xpath('.//div[@class="p-img"]/a/img/@src').extract_first()
            if item['book_img'] is None:
                item['book_img'] = li.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img').extract_first()
            item['book_img'] = 'https:' + item['book_img'] if item['book_img'] is not None else None
            item['authors'] = li.xpath('.//span[@class="p-bi-name"]/span/a//text()').extract()
            item['publish_date'] = li.xpath('.//span[@class="p-bi-date"]/text()').extract_first().strip()
            item['store'] = li.xpath('.//span[@class="p-bi-store"]/a/@title').extract_first()
            item['skuid'] = li.xpath('./div/@data-sku').extract_first()
            yield scrapy.Request(
                'http://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['skuid']),  # 价格的响应地址
                callback=self.parse_book_price,
                meta={'item': deepcopy(item)}
            )

        # 寻找下一页url地址
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url, next_url)
            # 构造下一页url的请求
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )

    # 获取价格
    def parse_book_price(self, response):
        item = response.meta['item']
        item['price'] = json.loads(response.body.decode())[0]['op']
        print(item)  # 这里我没有保存到item里去，只是打印下查看效果，保存工作自己来完成吧
        # yield item
