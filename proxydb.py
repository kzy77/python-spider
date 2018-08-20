# -*- coding:UTF-8 -*-
import random
import re
import subprocess as sp
import time
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

"""
函数说明:获取IP代理
Parameters:
	page - 高匿代理页数,默认获取第一页
Returns:
	proxys_list - 代理列表
Modify:
	2017-05-27
"""
def get_proxys():
	#requests的Session可以自动保持cookie,不需要自己维护cookie内容
	S = requests.Session()
	#proxydb高匿IP地址
	target_url = 'http://proxydb.net/?protocol=https&country=CN'
	#完善的headers
	target_headers = {'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Referer':'http://proxydb.net/?protocol=https&country=CN',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.9',
	}
	#get请求
	target_response = S.get(url = target_url, headers = target_headers)
	#utf-8编码
	target_response.encoding = 'utf-8'
	#获取网页信息
	target_html = target_response.text

	# 基于google headless chromedriver 配置 需要在系统环境变量中配置chromedriver.exe路径 或者 将chromedriver.exe放到python黄精变量中
	chrome_options = Options()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.get(target_url)
	time.sleep(1)
	target_elem = driver.find_element_by_css_selector(' table > tbody').text
	print(driver.find_element_by_css_selector(' table > tbody ').text)

	ip_port_list = re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d]):(?:\d{1,5})', str(target_elem), re.S)
	print(ip_port_list)
	# bs = BeautifulSoup(driver.page_source, "lxml")
	#获取id为ip_list的table
	# ip_port_list = bs.find_all('table')[0].find_all("tbody")[0].find_all("tr")

	# driver.close()
	#存储代理的列表
	proxys_list = []
	#爬取每个代理信息
	for index in range(len(ip_port_list)):
			ip_port = ip_port_list[index]
			# ip_port = driver.find_element_by_css_selector(' table > tbody > tr:nth-child('+ str(index + 1) +') > td > a').text
			ip = ip_port.split(':')[0]
			port = ip_port.split(':')[1]
			protocol = 'https'
			proxys_list.append(protocol.lower() + '#' + ip + '#' + port)
	#返回代理列表
	return proxys_list

"""
函数说明:检查代理IP的连通性
Parameters:
	ip - 代理的ip地址
	lose_time - 匹配丢包数
	waste_time - 匹配平均时间
Returns:
	average_time - 代理ip平均耗时
Modify:
	2017-05-27
"""
def check_ip(ip, lose_time, waste_time):
	#命令 -n 要发送的回显请求数 -w 等待每次回复的超时时间(毫秒)
	cmd = "ping -n 3 -w 3 %s"
	#执行命令
	p = sp.Popen(cmd % ip, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True) 
	#获得返回结果并解码
	out = p.stdout.read().decode("gbk")
	#丢包数
	lose_time = lose_time.findall(out)
	#当匹配到丢失包信息失败,默认为三次请求全部丢包,丢包数lose赋值为3
	if len(lose_time) == 0:
		lose = 3
	else:
		lose = int(lose_time[0])
	#如果丢包数目大于2个,则认为连接超时,返回平均耗时1000ms
	if lose > 2:
		#返回False
		return 1000
	#如果丢包数目小于等于2个,获取平均耗时的时间
	else:
		#平均时间
		average = waste_time.findall(out)
		#当匹配耗时时间信息失败,默认三次请求严重超时,返回平均好使1000ms
		if len(average) == 0:
			return 1000
		else:
			#
			average_time = int(average[0])
			#返回平均耗时
			return average_time

"""
函数说明:初始化正则表达式
Parameters:
	无
Returns:
	lose_time - 匹配丢包数
	waste_time - 匹配平均时间
Modify:
	2017-05-27
"""
def initpattern():
	#匹配丢包数
	lose_time = re.compile(u"丢失 = (\d+)", re.IGNORECASE)
	#匹配平均时间
	waste_time = re.compile(u"平均 = (\d+)ms", re.IGNORECASE)
	return lose_time, waste_time

if __name__ == '__main__':
	#初始化正则表达式
	lose_time, waste_time = initpattern()
	#获取IP代理
	proxys_list = get_proxys()

	#如果平均时间超过200ms重新选取ip
	while True:
		#从100个IP中随机选取一个IP作为代理进行访问
		proxy = random.choice(proxys_list)
		split_proxy = proxy.split('#')
		#获取IP
		ip = split_proxy[1]
		#检查ip
		average_time = check_ip(ip, lose_time, waste_time)
		if average_time > 200:
			#去掉不能使用的IP
			proxys_list.remove(proxy)
			print("ip连接超时, 重新获取中!")
		if average_time < 200:
			break

	#去掉已经使用的IP
	proxys_list.remove(proxy)
	proxy_dict = {split_proxy[0]:split_proxy[1] + ':' + split_proxy[2]}
	print("使用代理:", proxy_dict)
