import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse import settings
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    hash_tags = ['python', 'dataanalysis', 'computerscience', 'algorithms']

    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)

    crawl_proc.crawl(InstagramSpider,
                     start_tags=hash_tags,
                     login=os.getenv('INST_LOGIN'),
                     password=os.getenv('INST_PASS'))
    crawl_proc.start()