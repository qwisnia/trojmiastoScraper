# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from trojmiasto.items import TrojmiastoItem
from validate_email import validate_email
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class CompaniesSpider(CrawlSpider):
    name = "companies"
    allowed_domains = ["www.trojmiasto.pl", "praca.trojmiasto.pl"]
    start_urls = [
        'https://praca.trojmiasto.pl/pracodawca/lista.html',
    ]

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=["//h3[@class='company-name']"]),
            callback='parse_item',
        ),
        Rule(
            LinkExtractor(restrict_xpaths=["//ol[@class='navi-pages']"]),
            callback=None,
            follow=True
        ),
    )

    def parse_item(self, response):

        www_val = URLValidator()
        item = TrojmiastoItem()
        item['name'] = response.css('div.ogl__details__user__name::text').extract()[0].strip()
        data = response.css('div.contact__field.ogl__details__desc a::text').extract()

        for index, element in enumerate(data):
            element = element.strip()
        
            if index > 0 and 'email' not in item:
                return
                
            if validate_email(element, check_mx=True):
                item['email'] = element
                continue

            try:
                www_val(element)
                item['website'] = element
            except ValidationError, e:
                item['website'] = None
                break

        yield item
