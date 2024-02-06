import scrapy
import csv
from datetime import datetime
import pytz
from tqdm import tqdm

class SharghCrawler(scrapy.Spider):
    name = 'shargh_crawler'
    start_urls = [
        "https://www.sharghdaily.com/newsstudios/archive/?query=&dateRange%5Bstart%5D%5Bday%5D=01&dateRange%5Bstart%5D%5Bmonth%5D=01&dateRange%5Bstart%5D%5Byear%5D=1399&dateRange%5Bend%5D%5Bday%5D=01&dateRange%5Bend%5D%5Bmonth%5D=11&dateRange%5Bend%5D%5Byear%5D=1402&order=publish_time&categories=6&categories=216&categories=218&categories=219&categories=220&categories=224&categories=226&categories=12&categories=250&categories=287&categories=308&categories=310&categories=311&chk%5B%5D=on&types%5B%5D=3&types%5B%5D=4&types%5B%5D=11&queryType=lk&categories=2&button=submit"
    ]
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'articles_data.csv'
    }

    def parse(self, response):
        articles = response.css('ul.archive-n-land  li.dashed_brd div.left_service h2.title a')
        for i, article in enumerate(articles, start=1):
            article_url = response.urljoin(article.attrib['href'])
            yield scrapy.Request(article_url, callback=self.parse_article)

            # Check date every 20 articles
            if i % 20 == 0:
                progress_bar = tqdm(total=i, unit='articles')
                self.check_date_progress(progress_bar)

        next_page_link = response.css('footer.archive_next_page a::attr(href)').getall()[-1]
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1.title::text').get()
        abstract = response.css('p.lead::text').get()
        article_content = '\n'.join(response.css('div.article_body div#echo_detail p::text').getall())
        tags = response.css('div.article_tag a::text').getall()
        tags_str = ', '.join(tags)
        category = response.css('meta[itemprop="name"]::attr(content)').get()
        datetime_str = response.css('time.news_time::attr(datetime)').get()
        formatted_datetime = self.format_datetime(datetime_str)

        yield {
            'Title': title,
            'Abstract': abstract,
            'Content': article_content,
            'Tags': tags_str,
            'Category': category,
            'Datetime': formatted_datetime
        }

    def format_datetime(self, datetime_str):
        try:
            article_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
            tehran_timezone = pytz.timezone('Asia/Tehran')
            article_datetime = article_datetime.astimezone(tehran_timezone)
            formatted_datetime = article_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')
            return formatted_datetime
        except ValueError:
            return None

    def check_date_progress(self, progress_bar):
        # Check the date and update the progress bar accordingly
        # Add your logic here
        progress_bar.update(20)
