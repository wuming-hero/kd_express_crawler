# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExpressTemplateItem(scrapy.Item):
    # define the fields for your item here like:
    express_name = scrapy.Field()
    template_list = scrapy.Field()
