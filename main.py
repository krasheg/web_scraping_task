from bs4 import BeautifulSoup
import requests
import datetime
import re
from urllib.parse import urljoin
import pandas as pd
import sqlalchemy


def collect(url: str):
    """
    Script for parsing site https://www.kijiji.ca/ and saving data into dataframe
    :param url: url for parsing
    :return: dataframe with scrapped data
    """
    # dict with empty lists for collected data
    d = {
        'image': [],
        'title': [],
        'date': [],
        'city': [],
        'beds': [],
        'description': [],
        'currency': [],
        'price': []
    }
    # counter for pages
    count = 1
    # loop over all pages until "Next" button will disappear
    while True:
        # getting page
        response = requests.get(url)
        # creating a bs4 object with lxml parser
        soup = BeautifulSoup(response.text, "lxml")
        # finding all the ads in page
        ads = soup.find_all('div', class_='search-item')
        # loop over all ads and writes scrapped data
        for ad in ads:
            # image
            try:
                image = ad.find('source').get('data-srcset')
            except Exception:
                image = None
            # title
            try:
                title = ad.find('a', class_='title').text.strip()
            except Exception:
                title = None
            # date
            try:
                date = ad.find('div', class_='location').find('span', class_='date-posted').text.strip()
                if date.startswith('<') or 'minutes' in date or 'hours' in date:
                    date = datetime.datetime.now().date().strftime("%d-%m-%Y")
                elif 'yesterday' in date.lower():
                    date = datetime.datetime.now().date() - datetime.timedelta(days=1)
                    date.strftime("%d-%m-%Y")
                else:
                    date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%d-%m-%Y')
            except Exception:
                date = None
            # city
            try:
                city = ad.find('div', class_='location').find('span', class_='').text.strip()
            except Exception:
                city = None
            # number of beds
            try:
                beds = ad.find('span', class_='bedrooms').text.split(":")[1].strip()
            except Exception:
                beds = None
            # description
            try:
                description = ad.find('div', class_='description').text.strip().replace('\n', "")
                description = re.sub(' +', ' ', description)
            except Exception:
                description = None
            # Price
            try:
                price = ad.find('div', class_='price').text.strip()
                if price.startswith('$'):
                    currency = price[0]
                    price = float(price[1:].replace(',', ''))
                else:
                    price = None
                    currency = None
            except Exception:
                price = None
                currency = None
            # append in dictionary all data that we collected
            d['image'].append(image)
            d['title'].append(title)
            d['date'].append(date)
            d['city'].append(city)
            d['beds'].append(beds)
            d['description'].append(description)
            d['currency'].append(currency)
            d['price'].append(price)
        print(f'Page #{count} was collected successfully')
        # Handling pages with the Next button
        next_page = soup.find('a', {'title': "Next"})

        if next_page:
            next_page_url = next_page.get('href')
            url = urljoin(url, next_page_url)
            count += 1
        else:
            break
    # Create dataframe for export to database
    data_frame = pd.DataFrame(d)
    return data_frame


if __name__ == '__main__':
    url = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273'
    # write scrapped data
    df = collect(url)
    # create sqlalchemy engine
    engine = sqlalchemy.create_engine('postgresql://postgres:postgres@localhost:5432')  # use your own passwords
    # write our df to database
    df.to_sql('ads', engine, index=False)
    print('saving to database completed')
