import re
import os
import requests
from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
from requests import RequestException
from mmjpg.config import album_list

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
    'Referer': 'http://www.mmjpg.com/'
}


def get_photo_album_info(url: str) -> dict:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = BeautifulSoup(response.text, 'lxml')
            name = html.select_one('.article h2').string.split('(')[0]
            total_page = int(html.select('#page a')[-2].string)
            album_id = html.select_one('#content a')['href'].split('/')[-2]
            return {'name': name, 'total': total_page, 'id': album_id}
    except RequestException as error:
        print(error)
        return {}


def get_photo_album(url: str):
    album_info = get_photo_album_info(url)
    for i in range(1, album_info['total'] + 1):
        img_url = get_image_url('http://www.mmjpg.com/mm/%s/%s' % (album_info['id'], i))
        save_img(img_url, album_info['name'])


def get_image_url(url: str) -> str:
    """
    获取图片地址
    :param url: 页面URL
    :return: 图片URL
    """
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = BeautifulSoup(response.text, 'lxml')
            return html.select_one('#content img')['src']
    except RequestException as error:
        print(error)
        return ''


def save_img(img_url: str, dir_name: str) -> None:
    """
    保存图片到本地
    :param img_url: 图片链接
    :param dir_name: 文件夹名称
    """
    try:
        response = requests.get(img_url, headers=headers)
        if response.status_code == 200:
            # 判断文件夹是否已存在，若未存在则新建文件夹📁
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            # 保存图片到文件夹中
            print('正在保存%s' % img_url)
            with open(dir_name + '/' + get_image_name(url=img_url), 'wb') as file:
                file.write(response.content)
        else:
            print('error')
    except RequestException as error:
        print(error)
        pass


def get_image_name(url: str) -> str:
    """
    获取图片名称
    :param url: 图片链接
    :return: 图片名称
    >>> get_image_name('http://fm.shiyunjj.com/2018/1562/5idk.jpg')
    '5idk.jpg'
    """
    return re.split(r'/', url)[-1]


def main():
    pool = Pool()
    pool.map(get_photo_album, album_list)


if __name__ == '__main__':
    main()
