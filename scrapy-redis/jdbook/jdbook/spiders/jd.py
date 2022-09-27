import scrapy
import json
import time
from JD.items import JdItem


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com', 'list.jd.com']
    start_urls = [
        'https://book.jd.com/booksort.html'
    ]

    def parse(self, response):
        # 获取所有图书大分类节点列表
        big_node_list = response.xpath('//*[@id="booksort"]/div[2]/dl/dt/a')

        for big_node in big_node_list: #由于测试，此处只获取哦第一个[:1]
            big_category = big_node.xpath('./text()').extract_first()
            big_category_link = response.urljoin(big_node.xpath('./@href').extract_first())

            # 获取所有图书小分类节点列表
            small_node_list = big_node.xpath('../following-sibling::dd[1]/em/a')

            for small_node in small_node_list:  #由于测试，此处只获取哦第一个[:1]
                temp = {}
                temp['big_category'] = big_category
                temp['big_category_link'] = big_category_link
                temp['small_category'] = small_node.xpath('./text()').extract_first()
                temp['small_category_link'] = response.urljoin(small_node.xpath('./@href').extract_first())

                #京东页面更新，此处须重新构造请求url
                tmp_url = 'https://list.jd.com/list.html?cat=' + ','.join(temp['small_category_link'].split('/')[-1].split('.')[0].split('-'))

                # 模拟点击小分类链接
                yield scrapy.Request(
                    url=tmp_url,
                    callback=self.parse_book_list,
                    meta={'py_21': temp},
                    dont_filter=True
                )

    # 图书列表页面
    def parse_book_list(self, response):
        temp = response.meta['py_21']
        book_list = response.xpath('//*[@id="J_goodsList"]/ul/li/div')
        for book in book_list:
            item = JdItem()

            item['big_category'] = temp['big_category']
            item['big_category_link'] = temp['big_category_link']
            item['small_category'] = temp['small_category']
            item['small_category_link'] = temp['small_category_link']

            item['book_name'] = book.xpath('./div[3]/a/em/text()').extract_first()  # .strip()
            item['link'] = response.urljoin(book.xpath('./div[1]/a/@href').extract_first())
            item['author'] = book.xpath('./div[4]/span/a/text()').extract_first()
            item['price'] = book.xpath('./div[2]/strong/i/text()').extract_first()
            item['img_cover'] = response.urljoin(book.xpath('./div[1]/a/img/@data-lazy-img').extract_first())


            yield item
