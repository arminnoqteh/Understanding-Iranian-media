import scrapy
from persiantools.jdatetime import JalaliDate
import requests
from datetime import timedelta, date
from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
from persiantools.characters import ar_to_fa
from persiantools.digits import fa_to_en

topics = [1,2,7,8]

class TasnimSpider(scrapy.Spider):
    
    main_url = "https://www.tasnimnews.com"
    name = "Tasnim"
    base_url = 'https://www.tasnimnews.com/fa/service/1/'
    start_date = JalaliDate(1397, 1, 1)
    end_date = JalaliDate(1402, 1, 1)

    def get_index_url(self, year, month, day, page,topic):
        index_url = f"https://www.tasnimnews.com/fa/archive?service={topic}&sub=-1&date={year}%2F{month}%2F{day}&page={page}"
        print(index_url)
        return index_url
    
    def start_requests(self):
        current_date = self.start_date
        for topic in topics:
            while current_date <= self.end_date:
                year, month, day = current_date.year, current_date.month, current_date.day
                page = 1
                index_url = self.get_index_url(year, month, day, page,topic)
                yield scrapy.Request(index_url, callback=self.parse,cb_kwargs=dict(topic=topic))
                current_date += timedelta(days=1)

    def parse(self, response,topic):

        for news in response.css('article.list-item a::attr(href)').getall():
            request = scrapy.Request(
                self.main_url+news, 
                callback=self.parse_news,
                cb_kwargs=dict(category=topic))
            yield request 

        # Get the current page number
        page = int(response.url[-1])

        # Get the next page URL
        next_page = response.url[:-1] +str(page + 1)
        yield scrapy.Request(next_page, callback=self.parse)


    def parse_news(self, response, category):
        item = {
            'category': category,
            'title': response.css('article.single-news h1.title::text').get(),
            'abstract': response.css('article.single-news h3.lead::text').get(),
            'body': ' '.join(response.css('article.single-news div.story p::text').getall()),
            # 'time': JalaliDate.strptime(response.css('article.single-news div._sticky ul.list-inline li.time::text').get(),"%H:%M - %d %B %Y").to_gregorian()
            'time': datetime_converstion(response.css('article.single-news div._sticky ul.list-inline li.time::text').get())
        }
        yield item

def datetime_converstion(datetimestr):
    try:
        jd_text = datetimestr.strip().split('-')
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
    except:
        return None
    
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

