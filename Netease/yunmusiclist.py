from selenium import webdriver

import csv

# 网易云音乐第一页的地址
url = 'http://music.163.com/#/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset=0'

# 使用PhantomJS接口创建一个Selenium的WebDriver  Selenium与PhantomJS已分家，这里采用chromedriver
# driver = webdriver.PhantomJS
options = webdriver.ChromeOptions()
options.add_argument(
    'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"')
# 把chrome设置成无界面模式，不论windows还是linux都可以，自动适配对应参数
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

# 准备好存储歌单的csv文件
csv_file = open('playlist.csv', 'w', newline='',encoding='utf-8')
writer = csv.writer(csv_file)
writer.writerow(['标题', '播放数', '链接'])
count = 0;

# 解析每一页，直到下一页为空
while url != 'javascript:void(0)':
    # 用WebDriver加载画面
    driver.get(url)
    # 切换到内容的iframe
    driver.switch_to.frame("contentFrame")
    # 定位歌单标签
    data = driver.find_element_by_id("m-pl-container"). \
        find_elements_by_tag_name("li")

    # 解析一页中的所有歌单
    for i in range(len(data)):
        # 获取播放数
        nb = data[i].find_element_by_class_name("nb").text
        # 获取播放数大于500万的歌曲封面
        msk = data[i].find_element_by_css_selector("a.msk")
        count += 1
        print("%s 播放量：%s 已解析歌单：%s" %(msk.get_attribute("title"),nb,count))
        # 获取歌曲封面
        if '万' in nb and int(nb.split("万")[0]) > 500:
            # 把封面上的标题和链接播放数写到同一个文件中
            writer.writerow([msk.get_attribute("title"), nb, msk.get_attribute("href")])

    # 定位下一页
    url = driver.find_element_by_css_selector("a.zbtn.znxt"). \
        get_attribute('href')

csv_file.close();