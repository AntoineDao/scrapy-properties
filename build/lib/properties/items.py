# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from re import sub
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst
import dateparser

class PropertyItem(scrapy.Item):
    property_id = scrapy.Field()
    url = scrapy.Field()
    posting_date = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    address = scrapy.Field()
    postcode = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    bedrooms = scrapy.Field()
    surface = scrapy.Field()
    price = scrapy.Field()
    offer_type = scrapy.Field()
    source = scrapy.Field()
    year_built = scrapy.Field()
    agency_name = scrapy.Field()
    images = scrapy.Field()
    crawled_at = scrapy.Field()
    spider = scrapy.Field()


def lowercase_processor(self, values):
    for v in values:
        yield v.lower()

def extract_float(self, values):
    for v in values:
        try:
            yield float(sub(r'[^\d.]', '', v))   
        except:
            pass

def clean_description(self, values):
    for v in values:
        v = v.strip()
        v = v.lower()
        if v != '' or v != None:
            yield v

def parse_date_string(self, values):
    for v in values:
        yield dateparser.parse(v)

class PropertyLoader(ItemLoader):

    default_item_class=PropertyItem

    default_output_processor = TakeFirst()

    source_id_in = lowercase_processor

    latitude_in = extract_float
    longitude_in = extract_float

    address_in = clean_description

    postcode_in = clean_description

    offer_type_in = clean_description

    bedrooms_in = extract_float

    description_in = clean_description

    posting_date_in = parse_date_string

    price_in = extract_float

    images_out = Join(',')

    description_out = Join()

    agency_name_in = lowercase_processor
