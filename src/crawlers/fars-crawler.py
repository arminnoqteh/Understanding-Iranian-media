import scrapy
import csv
from random import randint
from time import sleep
from tqdm import tqdm
from persiantools.jdatetime import JalaliDate
from datetime import datetime, timedelta
import requests

start_date = datetime.strptime('2018-03-21', '%Y-%m-%d')
end_date = datetime.strptime('2023-03-21', '%Y-%m-%d')
class FarsCrawler(scrapy.Spider):
    name = 'fars_crawler'

    def start_requests(self):
        current_date = start_date
        while current_date <= end_date:
            jalali_date = JalaliDate(current_date)
            formated_date = f'{jalali_date.year}%2F{jalali_date.month}%2F{jalali_date.day}'
            start_url = f'https://www.farsnews.ir/archive?cat=-1&subcat=-1&date={formated_date}&p=1'
            yield scrapy.Request(start_url, self.parse)
            print(f'\n Date {jalali_date.year}-{jalali_date.month}-{jalali_date.day} is finished \n')
            current_date += timedelta(days=1)

    def parse(self, response):
        news_list = response.css('ul.last-news li > a')
        # if news_list is empty, it means that the page does not exist
        if not news_list:
            return
        for link in news_list:
            yield response.follow(link.attrib['href'], self.parse_news)

        # Get the current page number
        page = int(response.url.split('p=')[-1])

        # Get the next page URL
        next_page = response.url.split('p=')[-1] + 'p=' +str(page + 1)

        yield scrapy.Request(next_page, callback=self.parse)
    
    def page_exists(self, url):
        response = requests.head(url)
        return response.status_code == 200
    
    def parse_news(self, response):
        # Get Published Datetime
        published_date_object = response.css('div.header time')
        if published_date_object:
            published_date = datetime.strptime(published_date_object.attrib['datetime'], '%m/%d/%Y %H:%M:%S %p')
        else:
            published_date = datetime.now().strftime('%m/%d/%Y %H:%M:%S %p')

        # Get Title
        title_object = response.css('h1.title::text')
        title = title_object.get().strip()

        # Get Abstract
        abstract_object = response.css('p.lead ::text').extract()
        if len(abstract_object)==2:
            abstract = abstract_object[1].strip()
        else:
            abstract = None

        # Get Service name and Subgroup Name
        service_object = response.css('div.header h2.category-name a::text')
        if len(service_object) == 2:
            service = service_object[0].get().strip()
            subgroup = service_object[1].get().strip()
        elif len(service_object)==1:
            service = service_object[0].get().strip()
            subgroup = None
        else:
            service = None
            subgroup = None

        # Get Tags
        tags_list_object = response.css('div.tags a::text')
        tags_list = [tag.get().strip() for tag in tags_list_object]
        tags = ', '.join(tags_list)

        # Get Body
        body_objects = response.css('div[itemprop="articleBody"] > p::text')
        paragraphs = [pr.get().strip() for pr in body_objects]
        body = ' '.join(paragraphs)

        yield {
            'title': title,
            'service': service,
            'subgroup': subgroup,
            'abstract': abstract,
            'body': body,
            'tags': tags,
            'published_datetime': published_date,
        }
