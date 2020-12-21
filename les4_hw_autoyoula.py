import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_gb_12'][self.name]

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)
            print(1)
    def ads_parse(self, response):

        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,

            'author': self.author_url(response),
            'features': self.get_features(response),
        }
        self.db.insert_one(data)

    def author_url(self, response):
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        author = re.findall(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar',script)

        return f'https://youla.ru/user/{author[0]}' if author else None

    def get_features(self, response):
        feautures = response.css('.AdvertSpecs_row__ljPcX')
        feautures_dict = {}
        for itm in feautures:

            feautures_dict.update({itm.css('.AdvertSpecs_label__2JHnS::text').get(): itm.css(
            '.AdvertSpecs_data__xK2Qx::text').get() or itm.css('a::text').get()})
            return feautures_dict