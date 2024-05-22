import os
import stat

import requests
from bs4 import BeautifulSoup

from extract_links import extract_links

PREFIX: str = 'https://kemono.su'

url: str = input('输入想要提取作者资源的kemono网址：')

download_location = 'D:\\Users\\tonypzy\\Downloads'

try:
    page_result = requests.get(url)
    page_result.raise_for_status()  # 检查请求是否成功
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
else:
    # 解析HTML内容
    parse_obj = BeautifulSoup(page_result.content, 'html.parser')
    # 打印解析后的HTML内容
    # print(parse_obj.prettify())  # 使用prettify方法更好地格式化输出

    # 寻找作者名字，然后新建文件夹
    span = parse_obj.find('span', itemprop="name")
    creator_name = span.text
    folder_path = download_location + '\\' + creator_name + '\\'

    # 使用 os.makedirs() 函数创建文件夹
    # os.mkdir(folder_path)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        # 更改文件夹的写入权限，避免 PermissionError: [Errno 13]
        os.chmod( folder_path, stat.S_IWOTH)

    menu = parse_obj.find('menu')

    # menu不存在，则代表只有一页的内容
    if menu is None:
        extract_links( parse_obj, folder_path)
    else:
        a_tags = menu.find_all('a')
        page_index = []
        # 第一个a_tag不用处理，因为是初始界面
        page_index.append(PREFIX+a_tags[0].get('href'))

        for a_tag in a_tags[1:]:
            b_tag = a_tag.find('b')
            if b_tag.text.isdigit():
                page_index.append(PREFIX+a_tag.get('href'))

        for index in page_index:
            subpage_result = requests.get(index)
            subpage_parse_obj = BeautifulSoup(subpage_result.content, 'html.parser')

            extract_links(subpage_parse_obj, folder_path)
    print('Complete the task!')
