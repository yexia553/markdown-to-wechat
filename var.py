import os

CONTENT_SOURCE_URL = "https://panzhixiang.cn"  # 文章原地址，比如自己的博客网站
AUTHOR = "潘智祥"  # 希望显示在公众号文章中的作者名字
IMAGE_PATH = "/home/zhixiang_pan/learningspace/myNotes"  # markdown中引用的图片的路径
MARKDOWN_PATH = [
    "/home/zhixiang_pan/learningspace/myNotes/essays",
    "/home/zhixiang_pan/learningspace/myNotes/invest",
    "/home/zhixiang_pan/learningspace/myNotes/tech",
    "/home/zhixiang_pan/learningspace/myNotes/tourism",
]  # markdown文件的路径
FOOTER = '''
<div>
    <br />
    <br />
    同步发布在我的个人博客上：<a href="https://panzhixiang.cn">https://panzhixiang.cn</a>
</div>
'''  # 添加在每篇文章的底部的内容,如果没有，保留空字符串即可
# 以下是微信公众号的配置， 可以通过环境变量设置或者直接写在第二个引号中
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', '')
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')
