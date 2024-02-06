import scrapy
from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
from persiantools.characters import ar_to_fa
from persiantools.digits import fa_to_en
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

date = "۰۲ فروردين ۱۳۹۹ - ۱۲:۵۶"

def datetime_converstion(datetimestr):
    try:
        jd_text = datetimestr.strip().split('/')
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

import pandas as pd
df = pd.read_csv('data/isna.csv')
df['time'] = df['time'].apply(datetime_converstion)
# Drop some columns
df = df.drop(columns=['shortlink', 'news_id', 'managers', 'reporter'])
df.dropna().to_csv('isna_time_fixed.csv', index=False)
