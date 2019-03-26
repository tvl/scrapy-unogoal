# -*- coding: utf-8 -*-
from scrapy import Spider, Request
#from scrapy.loader import ItemLoader
from unogoal.items import Odd
from urllib.parse import parse_qs
from datetime import datetime, date, timedelta
import re

class OddsSpider(Spider):
    name = "odds"
    #allowed_domains = ["http://data.unogoal.me"]
    start_urls = ['http://data.unogoal.life/1x2/index.htm',
            'http://data.unogoal.life/1x2/TomorrowOdds.aspx']
    params = {
        "sport": "soccer",
        "page": "match",
        "id" : "2255155",
        "localization_id": "www"
    }

    def start_requests(self):
        #dates = ['2017-09-09', '2017-09-10', '2017-09-11']
        for u in self.start_urls:
            request = Request(url=u, callback=self.parse)
            request.meta['proxy'] = 'http://127.0.0.1:8118'
            yield request

    def parse(self, response):
        items = []
        matches = response.xpath('//table[@class="schedule"]//tr')
        for i, m in enumerate(matches):
            if i % 2 == 0:
                continue
            item = Odd()

            d = parse_qs(m.xpath('./td[@class="gocheck"]/a/@href').extract_first())
            item['id'] = d[list(d)[0]][0]
            date_time = m.xpath('./td[@class="en"]/script/text()').extract_first()[9:-1].split(',')
            date_time[1] = date_time[1].split('-')[0]
            yy, mm, dd, hh, mmm, ss = list(map(int, date_time))
            item['datetime'] = datetime(yy, mm, dd, hh, mmm, 0).isoformat(' ')
            item['competition_id'] = m.xpath('@name').extract_first()
            item['fifa_id'] = m.xpath('./td[@class="style31"]/text()').extract_first()
            if item['fifa_id'] is None:
                item['fifa_id'] = m.xpath('./td[@class="style31"]/a/text()').extract_first()
            item['home_team_id'] = re.findall(r'\d+', m.xpath('./td[@class="team"]/a/@href').extract()[0])[0]
            item['home_team'] = m.xpath('./td[@class="team"]/a/text()').extract()[0]
            item['away_team_id'] = re.findall(r'\d+', m.xpath('./td[@class="team"]/a/@href').extract()[1])[0]
            item['away_team'] = m.xpath('./td[@class="team"]/a/text()').extract()[1]
            item['home'], item['draw'], item['away'] = m.xpath('./td[@class="en"]/text()').extract()[:3]
            #item['hts'], item['fts'] = m.xpath('./td/font[@color="red"]/text()').extract()

            item['updated'] = datetime.utcnow().isoformat(' ')
            yield item
            items.append(item)
        return items
        #self.log('URL: {}'.format(response.url))


