# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from ..items import PropertyItem, PropertyLoader

BASE_DOMAIN = 'https://www.rightmove.co.uk'

class RightmoveSpider(scrapy.Spider):
    name = 'rightmove'
    allowed_domains = ['rightmove.co.uk']
    locations = ['Edinburgh']
    start_urls = [
        '{}/property-for-sale/{}.html'.format(BASE_DOMAIN, location)
        for location in locations
        ]

    def parse(self, response):
        links = [BASE_DOMAIN + a for a in response.css(
            'div.propertyCard-details > a.propertyCard-link::attr(href)').extract()]
        
        if len(links) != 0:
            split_url = response.url.split('?')
            if len(split_url) == 1:
                next_index = 24
            elif len(split_url) == 2:
                next_index = int(split_url[1].split('=')[1]) + 24
            
            next_url = split_url[0] + '?index=' + str(next_index)
            yield scrapy.Request(next_url, callback=self.parse)

        for link in links:
            yield scrapy.Request(link, callback=self.parse_property_page)            

    def parse_property_page(self, response):
        lat_lon_url = response.css('img[alt="Get map and local information"]::attr(src)').extract()[0]

        lat_regex = r"latitude=(\S*)&longitude"
        long_regex = r"longitude=(\S*)&zoom"

        url = response.css('link[rel="canonical"]::attr(href)').extract()[0]
        property_id = url.split('sale/property-')[1].split('.')[0]

        date_string = response.css('div#firstListedDateValue').xpath('text()').extract()[0]

        latitude = re.search(lat_regex, lat_lon_url).group(1) 
        longitude = re.search(long_regex, lat_lon_url).group(1) 

        tags = response.css('div.key-features li').xpath('text()').extract() 

        title = response.css('h1[itemprop=name]').xpath('text()').extract()

        description = response.css('p[itemprop=description]').xpath('text()').extract()  

        address = response.css('div.property-header address meta::attr(content)').extract()

        postcode = address[0].split(', ')[-1]

        title = response.css('title').xpath('text()').extract()[0]

        rooms = title.split(' ')[0]

        images = response.css('ul.gallery-thumbs-list li meta::attr(content)').extract()

        price = response.css('#propertyHeaderPrice strong').xpath('text()').extract()

        offer_type = response.css('#propertyHeaderPrice > small').xpath('text()').extract()

        agency_name = response.css('#aboutBranchLink strong').xpath('text()').extract() 

        il = PropertyLoader()

        il.add_value('url', url)
        il.add_value('property_id', property_id)
        il.add_value('posting_date', date_string)
        il.add_value('latitude', latitude)
        il.add_value('longitude', longitude)
        il.add_value('address', address)
        il.add_value('postcode', postcode)
        il.add_value('title', title)
        il.add_value('description', tags)
        il.add_value('images', images)
        il.add_value('description', description)
        il.add_value('bedrooms', rooms)
        il.add_value('price', price)
        il.add_value('offer_type', offer_type)
        il.add_value('agency_name', agency_name)
        il.add_value('crawled_at', datetime.now())
        il.add_value('spider', self.name)

        return il.load_item()