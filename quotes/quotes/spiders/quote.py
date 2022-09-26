import scrapy
from scrapy.http import HtmlResponse


class QuoteSpider(scrapy.Spider):
    # 爬虫名称，它在一个项目中必须是唯一的，即不能为不同的爬行器设置相同的名称。
    name = 'quote'

    # 爬虫启动URL，等价于重写 start_requests 方法，这将调用默认的 start_requests 实现为爬行器创建初始请求
    start_urls = ['https://quotes.toscrape.com/']

    # def start_requests(self):
    #     """
    #     必须返回请求的可迭代(您可以返回请求列表或编写生成器函数)，爬行器将从该请求开始爬行。
    #     后续请求将从这些初始请求中相继生成。
    #     """
    #     urls = ['https://quotes.toscrape.com/page/1',
    #             'https://quotes.toscrape.com/page/2',
    #             'https://quotes.toscrape.com/page/3',
    #             'https://quotes.toscrape.com/page/4',
    #             'https://quotes.toscrape.com/page/5'
    #             ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        """
        将被调用以处理为每个请求下载的响应的方法。Response参数是 TextResponse 它保存页面内容，并具有进一步有用的方法来处理它。
        parse() 方法通常解析响应，将抓取的数据提取为字典，还查找要遵循的新URL并创建新请求 (Request )。
        :param response: TextResponse，请求响应内容
        :param kwargs:
        :return:
        """
        self.logger.info(f'status code: {response.status}, response url: {response.url}')
        self.logger.debug(response.body)

        # 提取响应中的标题内容
        ################################################################################################################
        # CSS 选择器提取元素
        # response.css() 是一个名为SelectorList，它表示Selector对象，这些对象环绕XML/HTML元素，
        # 并允许您运行进一步的查询以细化选择或提取数据。
        title = response.css('title').getall()  # ['<title>Quotes to Scrape</title>']
        title = response.css('title::text').getall()  # ['Quotes to Scrape']
        title = response.css('title::text')[0].get()  # 'Quotes to Scrape', 这样取值将在CSS未匹配到值时引发IndexError异常
        title = response.css('title::text').get()  # 'Quotes to Scrape', 这样取值将在CSS未匹配到值时返回None，而不是引发异常
        title = response.css('title::text').re(r'Q\w+')  # ['Quotes']
        title = response.css('title::text').re(r'(\w+) to (\w+)')  # ['Quotes', 'Scrape']
        self.logger.info(f'extract title with css: {title}')

        ################################################################################################################
        # Xpath 提取元素
        # 参考文档：http://zvon.org/comp/r/tut-XPath_1.html，http://plasmasturm.org/log/xpath101/。

        title = response.xpath('//title')  # [<Selector xpath='//title' data='<title>Quotes to Scrape</title>'>]
        title = response.xpath('//title/text()')  # [<Selector xpath='//title/text()' data='Quotes to Scrape'>]
        title = response.xpath('//title/text()').getall()  # ['Quotes to Scrape']
        title = response.xpath('//title/text()').get()  # 'Quotes to Scrape'

        # <bound method SelectorList.getall of [<Selector xpath='//title/text()' data='Quotes to Scrape'>]>
        # title = response.xpath('//title/text()').extract
        # <bound method SelectorList.get of [<Selector xpath='//title/text()' data='Quotes to Scrape'>]>
        # title = response.xpath('//title/text()').extract_first

        self.logger.info(f'extract title with xpath: {title}')

        ################################################################################################################
        # 通过yield关键字将提取的数据转换为字典类型返回
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        ################################################################################################################
        # 获取下一页
        """
        response.follow 直接支持相对URL-无需调用URLJOIN。注意 response.follow 只返回一个请求实例；您仍然需要生成这个请求。
        1>如果下一页连接为 <a> 元素有一个快捷方式： response.follow 自动使用其href属性。因此代码可以进一步缩短：
            for a in response.css('ul.pager a'):
                yield response.follow(a, callback=self.parse)
        2> 要从iterable创建多个请求，可以使用 response.follow_all 取而代之的是：
            anchors = response.css('ul.pager a')
                yield from response.follow_all(anchors, callback=self.parse) 
           或者进一步缩短：yield from response.follow_all(css='ul.pager a', callback=self.parse)
        """
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            self.logger.debug(f"next page: {next_page}")
            yield response.follow(next_page, callback=self.parse)

        ################################################################################################################

