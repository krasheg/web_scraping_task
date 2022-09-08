import requests
import datetime
import re
from urllib.parse import urljoin
import pandas as pd
import sqlalchemy
from bs4 import BeautifulSoup

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/105.0.0.0 Safari/537.36'
}
url = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273'

req = requests.get(url=url, headers=headers)
src = req.text

soup = BeautifulSoup(src, 'lxml')
pages_count = soup.find_all('div', class_=re.compile('pagination'))
print(pages_count)