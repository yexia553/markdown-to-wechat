import argparse
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import string
import random
import hashlib
import html
import json
import logging
import os
import pickle
import random
import string
import time
import urllib
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
import re

import markdown
import requests
from markdown.extensions import codehilite
from pyquery import PyQuery
from werobot import WeRoBot

from get_rich_text import get_rich_text
import var

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def write_to_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)


def replace_image_with_link(
    post_path, footer=var.FOOTER, image_base_uri=var.ONLINE_IMAGE_BASE_URI
):
    """
    用给定的图片链接替换markdown文件中路径，并在末尾添加页脚。

    :param post_path: 博客文章的路径。
    :param footer: 需要添加到文章末尾的页脚内容。
    :param image_base_uri: 图片的基础URL，用于替换图片路径中的相对路径。
    :return: 替换图片链接并添加页脚后的文章内容。
    """
    try:
        with open(post_path, "r", encoding="utf-8") as file:
            content = ""
            for line in file:
                content += re.sub(r"\(../images/", f"({image_base_uri}/", line)
            if footer:
                content += footer
            # 只选取文章内容，去掉属性部分
            content = content.split("---\n")[-1]
            return content
    except FileNotFoundError:
        print(f"文件 {post_path} 不存在。")
        return ""
    except PermissionError:
        print(f"没有权限读取文件 {post_path}。")
        return ""


def fetch_attr(content, key):
    """
    从markdown文件中提取属性
    """
    lines = content.split("\n")
    for line in lines:
        if line.startswith(key):
            return line.split(":")[1].strip()
    return ""


def get_images_from_markdown(content):
    lines = content.split("\n")
    images = []
    for line in lines:
        line = line.strip()
        if line.startswith("![") and line.endswith(")"):
            image = line.split("(")[1].split(")")[0].strip()
            images.append(image)
    return images


def convert_date_format(date_str):
    # 检测输入日期字符串的格式，并进行相应的转换
    try:
        if "-" in date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        elif "/" in date_str:
            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError as e:
        logging.error(f"Error: {e}")
        return None

    # 将日期对象转换为 "yyyy/mm/dd" 格式的字符串
    # converted_date_str = date_obj.strftime("%Y/%m/%d")

    return date_obj.year


class WeChatClient:
    def __init__(self):
        self.__accessToken = ""
        self.__leftTime = 0

    def __real_get_access_token(self):
        postUrl = (
            "https://api.weixin.qq.com/cgi-bin/token?grant_type="
            "client_credential&appid=%s&secret=%s"
            % (var.WECHAT_APP_ID, var.WECHAT_APP_SECRET)
        )
        urlResp = urllib.request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp["access_token"]
        self.__leftTime = urlResp["expires_in"]

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken


def Client():
    robot = WeRoBot()
    robot.config["APP_ID"] = var.WECHAT_APP_ID
    robot.config["APP_SECRET"] = var.WECHAT_APP_SECRET
    client = robot.client
    token = client.grant_token()
    return client, token


def upload_image_from_path(image_path):
    """
    从本地上传图片到微信公众号
    """
    if "images" in image_path:
        image_path = var.IMAGE_PATH + image_path.split("images")[-1]
    client, _ = Client()
    logging.info("正在上传 {}".format(image_path))
    try:
        media_json = client.upload_permanent_media(
            "image", open(image_path, "rb")
        )  ##永久素材
        media_id = media_json["media_id"]
        media_url = media_json["url"]
        logging.info("file: {} => media_id: {}".format(image_path, media_id))
        return media_id, media_url
    except Exception as e:
        logging.info("上传图片遇到错误，错误信息如下: {}".format(e))
        return None, None


def upload_image(img_url):
    """
    * 上传临时素材
    * 1、临时素材media_id是可复用的。
    * 2、媒体文件在微信后台保存时间为3天，即3天后media_id失效。
    * 3、上传临时素材的格式、大小限制与公众平台官网一致。
    """
    resource = urllib.request.urlopen(img_url)
    name = img_url.split("/")[-1]
    f_name = "/tmp/{}".format(name)
    if "." not in f_name:
        f_name = f_name + ".png"
    with open(f_name, "wb") as f:
        f.write(resource.read())
    return upload_image_from_path(f_name)


def update_images_urls(content, uploaded_images):
    """
    用新的图片链接替换markdown中的链接
    """
    for image, meta in uploaded_images.items():
        orig = "({})".format(image)
        new = "({})".format(meta[1])
        content = content.replace(orig, new)
    return content


def upload_media_news(post_path, rich_text_content):
    """
    上传到微信公众号素材
    """
    content = open(post_path, "r").read()
    TITLE = fetch_attr(content, "title").strip('"').strip("'")
    publish_date = fetch_attr(content, "date").strip()
    gen_cover = fetch_attr(content, "gen_cover").strip('"')  # 是否自动生成封面图片
    images = get_images_from_markdown(content)
    logging.info(f"博客标题是：{TITLE}")

    if len(images) == 0 or gen_cover == "true":
        # 原文章中没有图片或者gen_cover属性为true时，自动生成一张图片
        letters = string.ascii_lowercase
        seed = "".join(random.choice(letters) for i in range(10))
        logging.info(f"picsum seed 是：{seed}")
        images = ["https://picsum.photos/seed/" + seed + "/400/600"] + images
    uploaded_images = {}
    for image in images:
        media_id = ""
        media_url = ""
        if image.startswith("http"):
            media_id, media_url = upload_image(image)
        else:
            media_id, media_url = upload_image_from_path(var.IMAGE_PATH + image)
        if media_id is not None:
            uploaded_images[image] = [media_id, media_url]

    # content = update_images_urls(content, uploaded_images)

    THUMB_MEDIA_ID = (len(images) > 0 and uploaded_images[images[0]][0]) or ""
    AUTHOR = var.AUTHOR
    RESULT = rich_text_content
    link = os.path.basename(post_path).replace(".md", "")
    digest = fetch_attr(content, "subtitle").strip().strip('"').strip("'")
    CONTENT_SOURCE_URL = (
        f"{var.CONTENT_SOURCE_URL}/{convert_date_format(publish_date)}/{link}"
    )

    articles = {
        "articles": [
            {
                "title": TITLE,
                "thumb_media_id": THUMB_MEDIA_ID,
                "author": AUTHOR,
                "digest": digest,
                "show_cover_pic": 1,
                "content": RESULT,
                "content_source_url": CONTENT_SOURCE_URL,
            }
            # 若新增的是多图文素材，则此处应有几段articles结构，最多8段
        ]
    }

    fp = open("./result.html", "w")
    fp.write(RESULT)
    fp.close()

    client = WeChatClient()
    token = client.get_access_token()
    headers = {"Content-type": "text/plain; charset=utf-8"}
    datas = json.dumps(articles, ensure_ascii=False).encode("utf-8")

    postUrl = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=%s" % token
    r = requests.post(postUrl, data=datas, headers=headers)
    resp = json.loads(r.text)
    logging.info(resp)
    media_id = resp["media_id"]
    return resp


def process_blog(string_date):
    MARKDOWN_PATH = var.MARKDOWN_PATH
    for item in MARKDOWN_PATH:
        path_list = Path(item).glob("**/*.md")
        for path in path_list:
            path_str = str(path)
            content = open(path_str, "r").read()
            date = fetch_attr(content, "date").strip()
            if string_date in date:
                logging.info(path_str)
                markdown_content = replace_image_with_link(path_str)
                rich_text_content = get_rich_text(markdown_content)
                write_to_file(f"{path_str}.html", rich_text_content)
                upload_media_news(path_str, rich_text_content)


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def main(start_date, end_date):
    start_time = time.time()  # 开始时间
    for x in date_range(start_date, end_date):
        # 设置同步时间范围
        string_date = x.strftime("%Y-%m-%d")
        process_blog(string_date)
    end_time = time.time()  # 结束时间
    logging.info("程序耗时%f秒." % (end_time - start_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start", help="Start date as days before current date", type=int, default=2
    )
    parser.add_argument(
        "--end", help="End date as days before current date", type=int, default=1
    )
    args = parser.parse_args()

    current_date = datetime.now()
    start_date = current_date - timedelta(days=args.start)
    end_date = current_date - timedelta(days=-args.end)

    main(start_date, end_date)
