#coding=UTF-8

import random
import time

# 产生模拟的url
url_path = [
	"class/112.html",
	"class/128.html",
	"class/145.html",
	"class/146.html",
	"class/131.html",
	"class/130.html",
	"learn/821",
	"course/list"
]

# 产生模拟的ip地址
ip_slices = [132, 156, 124, 10, 29, 167, 143, 187, 30, 46, 55, 63, 72, 87, 98]

http_referes = [
	"http://www.baidu.com/s?wd={query}",
	"http://www.sougou.com/web?query={query}",
	"http://cn.bing.com/search?q={query}",
	"https://search.yahoo.com/search?p={query}",
]

search_keyword = [
	"Spark SQL实战",
	"Hadoop基础",
	"Storm实战",
	"Spark Streaming实战",
	"大数据面试"
]

status_code = [404, 500, 200]

def sample_url():
	return random.sample(url_path, 1)[0]

def sample_ip():
	slice = random.sample(ip_slices, 4)
	return ".".join([str(item) for item in slice])

def sample_refer():
	if random.uniform(0, 1) > 0.2:
		return "-"

	refer_str = random.sample(http_referes, 1)
	query_str = random.sample(search_keyword, 1)
	return refer_str[0].format(query=query_str[0])

def sample_status_code():
	return random.sample(status_code, 1)[0]

def getnerate_log(count = 10):
	time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

	# 写入到文件
	f = open("/Users/hecun/Desktop/access.log", "w+")

	while count >= 1:
		query_log = '{ip}\t{local_time}\t"GET /{url} HTTP/1.1"\t{status_code}\t{refer}'.format(local_time=time_str, url=sample_url(), ip=sample_ip(), refer=sample_refer(), status_code=sample_status_code())
		print(query_log)

		f.write(query_log + "\n")

		count = count - 1

if __name__ == '__main__':
	getnerate_log(10000)










