# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from ..items import PropertyItem, PropertyLoader

BASE_DOMAIN = 'https://www.zoopla.co.uk'

class ZooplaSpider(scrapy.Spider):
    name = 'zoopla'
    allowed_domains = ['zoopla.co.uk']
    locations = ['Edinburgh']
    start_urls = [
        '{}/for-sale/property/{}'.format(BASE_DOMAIN, location)
        for location in locations
        ]
    print(start_urls)

    def parse(self, response):
        properties = response.css('ul.listing-results > li.srp')

        pagination = response.css('div.paginate > a')
        next_page = pagination[-1]

        if next_page.xpath('text()').extract()[0] == 'Next':
            next_url = BASE_DOMAIN + next_page.css('a::attr(href)').extract()[0]
            yield scrapy.Request(next_url, callback=self.parse)

        for prop in properties:
            price = prop.css('a.text-price').xpath('text()').extract()
            offer_type = prop.css('a.text-price > span').xpath('text()').extract()
            bedrooms = prop.css('span.num-beds').xpath('text()').extract()
            address = prop.css('a.listing-results-address').xpath('text()').extract()
            postcode = address[0].split(' ')[-1]

            link = BASE_DOMAIN + prop.css('a.photo-hover::attr(href)').extract()[0]

            yield scrapy.Request(
                link,
                callback=self.parse_property_page,
                cb_kwargs=dict(price=price,
                    offer_type=offer_type,
                    bedrooms=bedrooms,
                    address=address,
                    postcode=postcode)
                    )

    def parse_property_page(self, response, price, offer_type, bedrooms, address, postcode):
        

        il = PropertyLoader()

        il.add_value('price', price)
        il.add_value('offer_type', offer_type)
        il.add_value('bedrooms', bedrooms)
        il.add_value('address', address)
        il.add_value('postcode', postcode)

        url = response.css('link[rel="canonical"]::attr(href)').extract()[0]
        property_id = url.split('/')[-1]
        date_string = response.css('span.dp-price-history__item-date').xpath('text()').extract()
        
        map_image_url = response.css('img.ui-static-map__img::attr(src)').extract()[1]
        lat_lon_regex = r"center=(\S*)\&size"
        lat_lon = re.search(lat_lon_regex, map_image_url).group(1).split(',')
        latitude = lat_lon[0]
        longitude = lat_lon[1]

        title = response.css('article >.ui-property-summary__title').xpath('text()').extract()
        images = response.css('ul.dp-gallery__list > li > img::attr(src)').extract()
        description = response.css('div.dp-description__text').xpath('text()').extract()
        tags = response.css('li.dp-features-list__item').xpath('text()').extract()
        agency_name = response.css('h4.ui-agent__name').xpath('text()').extract()

        il.add_value('url', url)
        il.add_value('property_id', property_id)
        il.add_value('posting_date', date_string)
        il.add_value('latitude', latitude)
        il.add_value('longitude', longitude)
        il.add_value('title', title)
        il.add_value('images', images)
        il.add_value('description', description)
        il.add_value('description', tags)
        il.add_value('agency_name', agency_name)
        il.add_value('crawled_at', datetime.now())
        il.add_value('spider', self.name)

        return il.load_item()