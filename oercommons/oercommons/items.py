# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OercommonsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    _id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    subject = scrapy.Field()
    level = scrapy.Field()
    author = scrapy.Field()
    language = scrapy.Field()
    license = scrapy.Field()
    date_added = scrapy.Field()
    material_type = scrapy.Field()
    lor = scrapy.Field()
    rating = scrapy.Field()
    number_visits = scrapy.Field()
    number_saves = scrapy.Field()
    pass
