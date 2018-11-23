import json
import sqlite3
import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
    'Accept-Language': 'zh-cn'
}


def create_table():
    conn = sqlite3.connect('maoyan.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''create table if not exists top100
            (ranking integer ,
            image varchar(100),
            title varchar(100),
            actor varchar (100),
            time varchar (100),
            score float 
            );
            ''')
    except sqlite3.OperationalError:
        return None
    cursor.close()
    conn.commit()
    conn.close()


def insert_to_top100(insert_data):
    conn = sqlite3.connect('maoyan.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        insert into top100 
        (ranking, image, title, actor, time, score) 
        values (?, ?, ?, ?, ?, ?)
                ''', (
            insert_data['ranking'],
            insert_data['image'],
            insert_data['title'],
            insert_data['actor'],
            insert_data['time'],
            insert_data['score']
        ))
        print(cursor.rowcount)
    except sqlite3.Error:
        return None
    cursor.close()
    conn.commit()
    conn.close()


def get_one_page(url):
    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    soup = BeautifulSoup(html, 'lxml')
    wrapper = soup.find('dl', class_='board-wrapper').find_all('dd')
    print(wrapper)
    for item in wrapper:
        yield {
            'ranking': int(item.find('i', class_='board-index').string),
            'image': item.find('img', class_='board-img')['data-src'],
            'title': item.find('p', class_='name').string,
            'actor': item.find('p', class_='star').string.strip()[3:],
            'time': item.find('p', class_='releasetime').string.strip()[5:],
            'score': float(item.find('p', class_='score').get_text())
        }


def write_to_file(content):
    with open('maoyan-top100.txt', 'a', encoding='utf-8') as file:
        file.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(offset):
    page_url = 'http://maoyan.com/board/4?offset=' + str(offset)
    print(page_url)
    html = get_one_page(page_url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
        insert_to_top100(item)


if __name__ == '__main__':
    create_table()
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
