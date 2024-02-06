import scrapy
from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
from persiantools.characters import ar_to_fa
from persiantools.digits import fa_to_en
from datetime import timedelta, date
import requests
import re

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

topics = [14,34,9,17]

class IsnaSpider(scrapy.Spider):
    
    main_url = "https://www.isna.ir"
    name = "ISNA"
    start_date = JalaliDate(1401, 9, 13)
    end_date = JalaliDate(1402, 1, 1)

    def get_index_url(self, year, month, day, page,topic):
        index_url = f"https://www.isna.ir/archive?tp={topic}&ms=0&dy={day}&mn={month}&yr={year}&pi={page}"
        return index_url
    
    def start_requests(self):
        current_date = self.start_date
        for topic in topics:
            while current_date <= self.end_date:
                year, month, day = current_date.year, current_date.month, current_date.day
                page = 1
                index_url = self.get_index_url(year, month, day, page,topic)
                yield scrapy.Request(index_url, callback=self.parse, cb_kwargs=dict(category=topic))
                current_date += timedelta(days=1)

    def parse(self, response, category):

        for news in response.css('div.items a::attr(href)').getall():
            request = scrapy.Request(
                self.main_url+news, 
                callback=self.parse_news,
                cb_kwargs=dict(category=category))
            yield request 


        # Get the current page number
        current_page = int(response.url[-1])
        # Get the next page URL

        if current_page < 6:
            next_page = response.url[:-1] +str(current_page + 1)
            yield scrapy.Request(next_page, callback=self.parse)

    def page_exists(self, url):
        response = requests.head(url)
        return response.status_code == 200

    def parse_news(self, response, category):
        item = {
                'title': response.css('article#item h1::text').get(),
                'time':  datetime_converstion(response.css('article#item li:nth-child(1) > span.text-meta::text').get()),
                'service': response.css('article#item li:nth-child(2) > span.text-meta::text').get(),
                'body': ' '.join(response.css('article#item div.item-body *::text').getall()),
        }
        yield item

    
def datetime_converstion(datetime):
    jd_text = datetime.strip().split('/')
    jd_time_part = fa_to_en(jd_text[1].strip())
    jd_date_part = fa_to_en(jd_text[0].strip())
    jd_month_name = ar_to_fa(''.join(re.findall(r'\D', jd_date_part))).strip()
    jd_month_number = jalali_months.get(jd_month_name)
    jd_parsed = jd_date_part.replace(jd_month_name, f'-{jd_month_number}-').replace(' ', '').split('-')
    jd_year = int(jd_parsed[2])
    jd_month = int(jd_parsed[1])
    jd_day = int(jd_parsed[0])
    jd_hour = int(jd_time_part.split(':')[0])
    jd_min = int(jd_time_part.split(':')[1])
    gregorian_date = JalaliDateTime(jd_year, jd_month, jd_day, jd_hour, jd_min, 0, 0).to_gregorian()
    return gregorian_date