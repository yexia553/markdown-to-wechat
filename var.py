import os

CONTENT_SOURCE_URL = "https://panzhixiang.cn"  # 文章原地址，比如自己的博客网站
AUTHOR = "潘智祥"  # 希望显示在公众号文章中的作者名字
IMAGE_PATH = "/home/zhixiang_pan/learningspace/myNotes/images"
MARKDOWN_PATH = [
    "/home/zhixiang_pan/learningspace/myNotes/essays",
    "/home/zhixiang_pan/learningspace/myNotes/invest",
    "/home/zhixiang_pan/learningspace/myNotes/tech",
    "/home/zhixiang_pan/learningspace/myNotes/tourism",
]
FOOTER = """

**同步发布在我的个人博客上：[https://panzhixiang.cn](https://panzhixiang.cn)**
"""
ONLINE_IMAGE_BASE_URI = CONTENT_SOURCE_URL + "/images"
WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET")
WECHAT_APP_ID = os.environ.get("WECHAT_APP_ID")
