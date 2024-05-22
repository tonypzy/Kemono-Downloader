import os
import re

import requests
from bs4 import BeautifulSoup

PREFIX: str = 'https://kemono.su'

def extract_links( parse_obj,folder_path):

    # 查找所有指定条件的<article>标签
    articles = parse_obj. find_all('article', class_='post-card post-card--preview')

    # 遍历所有<article>标签
    for article in articles:
        # 在每个<article>标签中查找包含href属性的<a>标签
        a_tag = article. find('a')
        # 获取对应页面,拼接成一个完整的link
        link = a_tag.get('href')
        link = PREFIX + link

        page_result = requests.get(link)
        parse_obj = BeautifulSoup(page_result.content, 'html.parser')

        # 获取帖子的标题
        post_title = parse_obj.find('h1', class_="post__title")
        span_post_title = ''
        span_post_titles = post_title.find_all('span')
        for title in span_post_titles:
            if title.text != '(Pixiv Fanbox)' and title.text != '(Patreon)':
                span_post_title = span_post_title + ' ' + re.sub(r'[\\/:*?<>|]', '-', title.text.rstrip())
        # 获取帖子的发布时间
        div_post_published=parse_obj.find('div',class_="post__published")
        publish_date = div_post_published.text.strip()
        publish_date = re.sub(r':', '-', publish_date)

        # 消除publish_date的前缀：Published:
        subfolder_path = folder_path + publish_date[11:] + ' ' +span_post_title

        # 创建对应帖子的新文件夹
        if not os.path.exists(subfolder_path):
            os.mkdir(subfolder_path)

        # 获取文本内容，如有文本，下载之
        content = ''
        post_content = parse_obj.find('div', class_="post__content")
        if post_content:
            p_content = post_content.find('p')
            if p_content:
                content = p_content.text
                content = re.sub(r'<br>', '\n', content)
                text_path = subfolder_path + '\\.txt'
            else:
                # pre_content = post_content.find('pre')
                # content = pre_content.text
                content = post_content.text
                content = content[1:]
                text_path = subfolder_path + '\\.txt'

            file = open(text_path, 'w', encoding='utf-8')
            file.write(content)
            file.close()


        # 获取下载内容，如有下载内容，下载之
        post_attachments = parse_obj.find('ul', class_="post__attachments")
        if post_attachments:
            attachments = post_attachments.find_all('li', class_="post__attachment")
            for attachment in attachments:
                a_attachment = attachment.find('a', class_="post__attachment-link")
                download_link = a_attachment.get('href')
                # 获取资源名字，获得完整的资源路径
                resource_name = a_attachment.text.strip()
                resource_path = subfolder_path+'\\'+resource_name[9:]

                with requests.get(download_link, stream=True) as response:
                    response.raise_for_status()  # 检查响应是否成功
                    # 打开文件并逐块写入数据
                    with open(resource_path, 'wb') as f:
                         for chunk in response.iter_content(chunk_size=8192):  # 逐块读取响应内容
                             if chunk:  # 如果读取到了数据块
                                 f.write(chunk)  # 将数据块写入文件
                                 f.flush()  # 刷新缓冲区
        # 获取图片文件，如有图片，下载之
        post_files = parse_obj.find('div', class_="post__files")
        if post_files:
            post_thumbnails = post_files.find_all('div', class_="post__thumbnail")
            for post_thumbnail in post_thumbnails:
                figure = post_thumbnail.find('figure')
                a_thumbnail = figure.find('a', class_="fileThumb")
                download_link = a_thumbnail.get('href')
                post_title = a_thumbnail.get('download')
                post_path = subfolder_path+'\\'+post_title

                with requests.get(download_link, stream=True) as response:
                    response.raise_for_status()  # 检查响应是否成功
                    # 打开文件并逐块写入数据
                    with open(post_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):  # 逐块读取响应内容
                            if chunk:  # 如果读取到了数据块
                                f.write(chunk)  # 将数据块写入文件
                                f.flush()  #刷新缓冲区