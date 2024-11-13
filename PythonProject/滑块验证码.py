import re
import time

import ddddocr
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Edge()

# 1.打开首页
driver.get('https://www.om.cn/')

# 2.点击【滑动拼图验证】
tag = WebDriverWait(driver, 30, 0.5).until(lambda dv: dv.find_element(
    By.XPATH,
    '//*[@id="app"]/div[1]/div/header/div/div[2]/div[3]/div/div[1]'
))
tag.click()

# 3.点击【注册】
tag = WebDriverWait(driver, 30, 0.5).until(lambda dv: dv.find_element(
    By.XPATH,
    '//*[@id="login"]/div/div[1]/span'
))
tag.click()

# 4.点击【手机注册】
tag = WebDriverWait(driver, 30, 0.5).until(lambda dv: dv.find_element(
    By.XPATH,
    '//*[@id="register"]/div/div[2]/div[1]/div[2]/span'
))
tag.click()

# 5.输入手机号
tag = WebDriverWait(driver, 30, 0.5).until(lambda dv: dv.find_element(
    By.XPATH,
    '//*[@id="register"]/div/div[1]/div[2]/div[1]/input'
))
tag.send_keys('13301440507')

# 6.开始验证
tag = WebDriverWait(driver, 30, 0.5).until(lambda dv: dv.find_element(
    By.XPATH,
    '//*[@id="register"]/div/div[1]/div[2]/div[3]/button[1]'
))
tag.click()

# 4.读取背景图片
def fetch_bg_func(dv):
    tag_object = dv.find_element(
        By.CLASS_NAME,
        'tc-bg-img unselectable'
    )
    style_string = tag_object.get_attribute("style")
    match_list = re.findall('url\(\"(.*)\"\);', style_string)  # ["http..." ]
    print(match_list)
    if match_list:
        return match_list[0]


bg_image_url = WebDriverWait(driver, 30, 0.5).until(fetch_bg_func)  # 新的函数 = 某个函数('geetest_bg')
print("背景图：", bg_image_url)


# 4.读取缺口图片
def fetch_slice_func(dv):
    tag_object = dv.find_element(
        By.CLASS_NAME,
        'tc-fg-item'
    )
    style_string = tag_object.get_attribute("style")
    match_list = re.findall('url\(\"(.*)\"\);', style_string)
    print(match_list)
    if match_list:
        return match_list[0]

slice_image_url = WebDriverWait(driver, 30, 0.5).until(fetch_slice_func)  # 新的函数 = 某个函数('geetest_slice_bg')
print("缺口图：", slice_image_url)

# 5.识别图片坐标
slice_bytes = requests.get(slice_image_url).content
bg_bytes = requests.get(bg_image_url).content

slide = ddddocr.DdddOcr(det=False, ocr=False,
                        show_ad=False)  # det=False：表示不进行文本检测。ocr=False：表示不进行文本识别。show_ad=False：表示不显示广告。
res = slide.slide_match(slice_bytes, bg_bytes, simple_target=True)
x1, y1, x2, y2 = res['target']
print(x1, y1, x2, y2)  # 196 12 276 92

# 6.滑动滑块
tag = driver.find_element(By.CLASS_NAME, 'tc-fg-item tc-slider-normal')
time.sleep(2)
ActionChains(driver).click_and_hold(tag).perform()  # 点击并抓住标签
ActionChains(driver).move_by_offset(xoffset=x1, yoffset=0).perform()  # 向右滑动114像素（向左是负数）
ActionChains(driver).release().perform()  # 释放

time.sleep(3)
