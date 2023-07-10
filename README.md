# markdown-to-wechat

这是在喵叔的[markdown-to-wechat](https://github.com/chenyukang/markdown-to-wechat)基础上根据自己的需求修改了一些代码，感谢喵叔开源。

## 功能
主要作用就是把markdown文件同步到微信公众号中，不用手动一篇一篇重新编辑。

## 安装依赖
```bash
pip3 install -r requirements.txt
```

## 配置白名单和 token
微信公众号只允许来自于白名单的IP请求相关API，所以需要在微信公众号后台配置白名单。
后台路径：设置和开发 -> 基本配置 ：填入服务器 IP，生成 token。

## 配置自定义变量
1. var.py
    我创建了一个var.py，内容如下：
    ```python
    CONTENT_SOURCE_URL = "https://panzhixiang.cn"  # 文章原地址，比如自己的博客网站
    AUTHOR = "潘智祥"  # 希望显示在公众号文章中的作者名字
    IMAGE_PATH = "./myNotes/images"  # markdown中引用的图片的路径
    MARKDOWN_PATH = ["./myNotes/"]  # markdown文件的路径，可以传入多个路径
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
    ```
    需要根据自己的实际情况进行修改  

2. 设置同步时间范围
    这个工具是同步一定时间范围内的博客到公众号，代码如下：
    ```python
    # 在sync.py 
    for x in date_range(
            datetime.now() - timedelta(days=7), datetime.now() + timedelta(days=2)
        ):
    ```
    以上代码就是会同步从当前时间往前7天，往后2天的博客到公众号，可以根据自己的需求进行修改。

    需要解释的是，这里用来对比的时间，是markdown文件中的属性**date**的值，而不是文件创建或者修改的时间，
    所以需要在markdown文件中添加date属性，比如：
    ```markdown
    ---
    title: markdown to wechat
    date: 2020-12-12
    tags:
    - python
    ---
    以下是正文
    ```

## 运行
```python
python3 sync.py
```

## 注意事项  
1. 防止重复上传博客到公众号  
   - 代码是通过计算markdown文件的md5值来判断是否已经被处理过，所以任何对文件的修改都会导致md5值的变化，从而导致重复上传。  
   - 代码运行过一次之后产生一个名为“cache.bin”的文件，这里面存储了已经处理过的文件的md5值等信息，这是代码能“记住”处理过哪些博客的关键，如果要移动代码位置，一定要把这个文件一同移动，否则就会导致重复上传。  

2. 封面图片  
    建议在每一篇博客的markdown文件中都要有至少一个图片，这样可以用你自己的图片作为封面图片，否则会随机冲[https://picsum.photos](https://picsum.photos)中获取一张图片作为封面图片。
