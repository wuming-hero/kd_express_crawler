# -*-coding:utf-8-*-
import os
import pymysql
import requests


class CrawlImage(object):
    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password="123456",
                                          db='ixiye_ida',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def crawl_image(self):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM ida_express_template WHERE uid = 0"
                cursor.execute(sql)
                template_list = cursor.fetchall()
                for template in template_list:
                    dir_path = '/Users/wuming/tmp'
                    image_url = template['image_url']
                    # 判断文件夹是否存在
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                    image_file_name = image_url.split("/")[-1]
                    file_path = '%s/%s' % (dir_path, image_file_name)
                    if os.path.exists(file_path):
                        print '====file_path:', file_path
                        continue

                    with open(file_path, 'wb') as handle:
                        response = requests.get(image_url, stream=True)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
                    print '++++file_path:', file_path
        except Exception, e:
            print '-------------------exception', e


# 测试入口
CrawlImage().crawl_image()
