from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip


# 读取本地 Markdown 文件内容
def read_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# 写入内容到本地文件
def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def get_rich_text(markdown_content, output_format="zhihu"):
    # 配置 Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 无头模式，如果你不需要看到浏览器界面
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    rendered_content = None
    try:
        # 打开 Markdown 在线编辑器
        driver.get("https://markdown.com.cn/editor/")

        # 定位到 CodeMirror 编辑区域的父节点
        editor_parent = driver.find_element(By.CLASS_NAME, "CodeMirror")

        # 点击以激活编辑区域
        editor_parent.click()

        # 获取 CodeMirror 内部实际的输入节点
        editor = driver.find_element(By.CSS_SELECTOR, ".CodeMirror textarea")

        # 清空输入区域
        editor.send_keys(Keys.CONTROL + "a")
        editor.send_keys(Keys.DELETE)

        # 将 Markdown 内容发送到编辑区域
        editor.send_keys(markdown_content)

        layout_theme_button = driver.find_element(By.ID, "nice-menu-theme")
        layout_theme_button.click()
        # time.sleep(1)
        all_stack_blue_option = driver.find_element(
            By.XPATH, "//span[contains(text(), '全栈蓝')]"
        )
        all_stack_blue_option.click()

        # 点击“代码主题”，选择“vs2015”
        code_theme_button = driver.find_element(By.ID, "nice-menu-codetheme")
        code_theme_button.click()
        # time.sleep(1)
        vs2015_option = driver.find_element(
            By.XPATH, "//span[contains(text(), 'vs2015')]"
        )
        vs2015_option.click()

        if output_format == "zhihu":
            # 点击右上角的“复制到知乎”
            copy_to_zhihu_button = driver.find_element(By.ID, "nice-sidebar-zhihu")
            copy_to_zhihu_button.click()
        elif output_format == "wechat":
            copy_to_wechat_button = driver.find_element(By.ID, "nice-sidebar-wechat")
            copy_to_wechat_button.click()

        rendered_content = pyperclip.paste()
    except Exception as err:
        print(err)

    finally:
        driver.quit()
        return rendered_content
