import sys

from scrapy import cmdline


def crawler_process():
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    from quotes.spiders.schedule import ScheduleSpider
    from quotes.spiders.author import AuthorSpider
    process.crawl(ScheduleSpider)
    process.crawl(AuthorSpider)
    process.start()


def crawler_runner():
    from scrapy.crawler import CrawlerRunner
    from scrapy.utils.project import get_project_settings
    from twisted.internet import reactor
    from scrapy.utils.log import configure_logging
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    from quotes.spiders.schedule import ScheduleSpider
    from quotes.spiders.author import AuthorSpider
    runner.crawl(ScheduleSpider)
    runner.crawl(AuthorSpider)
    task = runner.join()
    task.addBoth(lambda _: reactor.stop())
    reactor.run()


def main(args):
    """
    scrapy crawl
    Usage
    =====
      scrapy crawl [options] <spider>

    Run a spider

    Options
    =======
      -h, --help            show this help message and exit
      -a NAME=VALUE         set spider argument (may be repeated)
      -o FILE, --output FILE
                            append scraped items to the end of FILE (use - for stdout)
      -O FILE, --overwrite-output FILE
                            dump scraped items into FILE, overwriting any existing file
      -t FORMAT, --output-format FORMAT
                            format to use for dumping items

    Global Options
    --------------
      --logfile FILE        log file. if omitted stderr will be used
      -L LEVEL, --loglevel LEVEL
                            log level (default: DEBUG)
      --nolog               disable logging completely
      --profile FILE        write python cProfile stats to FILE
      --pidfile FILE        write process ID to FILE
      -s NAME=VALUE, --set NAME=VALUE
                            set/override setting (may be repeated)
      --pdb                 enable pdb on failure

    :param args: command args
    :return:
    """
    cmdline.execute(['scrapy', 'crawl', *args])


if __name__ == '__main__':
    # main(sys.argv[1:] + ['-L', 'INFO', 'author'])
    # crawler_process()
    crawler_runner()

