import scrapy
import re
from random import randint
from time import sleep
from persiantools.digits import fa_to_en
from persiantools.characters import ar_to_fa
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from datetime import datetime, timedelta

jalali_months = {
    "فروردین": 1,
    "اردیبهشت": 2,
    "خرداد": 3,
    "تیر": 4,
    "مرداد": 5,
    "شهریور": 6,
    "مهر": 7,
    "آبان": 8,
    "آذر": 9,
    "دی": 10,
    "بهمن": 11,
    "اسفند": 12
}

class KhabarOnlineSpider(scrapy.Spider):
    name = 'khabaronline'
    # start_urls = ['https://www.khabaronline.ir']
    main_url = "https://www.khabaronline.ir"
    start_date = JalaliDate(1397, 1, 1)
    end_date = JalaliDate(1402, 1, 1)



    def get_index_url(self, year, month, day, page):
        index_url = f"https://www.khabaronline.ir/archive?mn={month}&ty=1&dy={day}&ms=0&yr={year}&pi={page}"
        print(index_url)
        return index_url

    def start_requests(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            year, month, day = current_date.year, current_date.month, current_date.day
            page = 1
            index_url = self.get_index_url(year, month, day, page)
            yield scrapy.Request(index_url, callback=self.parse)
            current_date += timedelta(days=1)


    def parse(self, response):
        for news in response.css('section.list a::attr(href)').getall():
            request = scrapy.Request(
                self.main_url+news, 
                callback=self.parse_news)
            yield request 

        # Get the current page number
        current_page = int(response.url[-1])
        # Get the next page URL

        if current_page < 6:
            next_page = response.url[:-1] , str(current_page + 1)
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_news(self, response):
        # Extract information from a single news article page
        title = response.css('h1.title a::text').get().strip()
        published_date_text = response.css('div.item-header div.item-date span::text').get().strip()
        published_date = self.parse_published_date(published_date_text)
        abstract = response.css('article div.item-summary p::text').get().strip()
        service = response.css('section.page-header ol.breadcrumb a::text')[1].get().strip()
        subgroup = response.css('section.page-header ol.breadcrumb a::text')[2].get().strip()
        tags = ', '.join(response.css('section.tags a::text').getall())
        body = ' '.join(response.css('div[itemprop="articleBody"] > p::text').getall())

        # Store the extracted data in a dictionary
        news_item = {
            'title': title,
            'published_date': published_date,
            'abstract': abstract,
            'service': service,
            'subgroup': subgroup,
            # 'short_link': short_link,
            'tags': tags,
            'body': body,
        }

        yield news_item

    def parse_published_date(self, published_date_text):
        jd_text = published_date_text.strip().split('-')
        jd_time_part = fa_to_en(jd_text[1].strip())
        jd_date_part = fa_to_en(jd_text[0].strip())
        jd_parsed = jd_date_part.split(' ')
        jd_parsed[1] = jalali_months.get(ar_to_fa(jd_parsed[1]))
        jd_year = int(jd_parsed[2])
        jd_month = int(jd_parsed[1])
        jd_day = int(jd_parsed[0])
        jd_hour = int(jd_time_part.split(':')[0])
        jd_min = int(jd_time_part.split(':')[1])
        gregorian_date = JalaliDateTime(jd_year, jd_month, jd_day, jd_hour, jd_min, 0, 0).to_gregorian()
        return gregorian_date
