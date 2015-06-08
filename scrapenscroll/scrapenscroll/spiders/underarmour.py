import scrapy
import json
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from scrapenscroll.items import ProductItem


## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class UnderArmourSpider(CrawlSpider):
    name = "underarmour"
    allowed_domains = ["underarmour.com"]
    start_urls = [
        "https://www.underarmour.com/en-us/footwear/all?s=DF",
    ]

    

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(restrict_xpaths='//a[contains(@class,"product-img-link")]',
                deny=('_[WM]\.html',)),
                callback='singleProductParse'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(restrict_xpaths='//a[contains(@class,"btn-next")]'),
                follow=True),
            )

    # Function to parse information from the product grid. Currently unused
    def productPageParse(self,response):
        products = response.css('div[id^="product-"]')[1:]
        for p in products:
            item = ProductItem()
            item['name'] = p.css('span.title').xpath('text()').extract()[0]
            item['brand'] = 'Adidas'
            desc = p.css('span.subtitle').xpath('text()').extract()[0]
            try:
                item['division'], item['category'] = desc.split(" ",1)
            except ValueError:
                item['category'] = desc
                item['division'] = 'None'
            item['price'] = p.css('span.salesprice').xpath('text()').extract()[0].strip()
            item['image_link'] = p.css('img.show::attr(data-stackmobileview)').extract()[0]
            yield item

    # Function to parse information from a single product page
    def singleProductParse(self,response):
        categories = ["Baseball Cleats", "Basketball Shoes", "Soccer Cleats", "Running Shoes", "Shoes", "Sandals", "Trail Shoe", "Running Shoe", "Boots", "Cleats", "Training Shoes", "Football Cleats"]
        item = ProductItem()
        item['brand'] = 'Under Armour'
        # item['name'] = response.css('.title-32').xpath('text()').extract()[0]
        try:
            desc = response.css('.buypanel_producttitle -women').xpath('text()').extract()[0].strip()
        except IndexError:
            desc = response.css('.buypanel_producttitle').xpath('text()').extract()[0].strip()   
        
        scripts = response.css('script').xpath('text()').extract()
        data = filter(lambda k: 'window.UA' in k,scripts)[0]
        var = data[data.index('{'):data.index('}')+1]
        item['category'] = json.loads(var)['PRODUCT_DATA'][0]



        # for i in categories:
        #     if i in desc:
        #         item['category'] = i
        #         desc.replace(i, "")
        #     else:
        #         item['category'] = 'None'



        try:
            item['division'], item['name'] = desc.split(" ",1)
        except ValueError:
            item['category'] = desc
            item['division'] = 'None'

        item['price'] = response.css('span.buypanel_productprice-value').xpath('text()').extract()[0].strip()
        item['price'] = item['price'].replace("$","")
        item['image_link'] = response.css('img.pdp_main_image::attr(src)').extract()[0]
        return item
