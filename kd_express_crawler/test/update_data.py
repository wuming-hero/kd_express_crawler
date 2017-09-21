# -*-coding:utf-8-*-
import os
import pymysql
import requests


class UpdateData(object):
    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password="123456",
                                          db='ixiye_ida',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def update_data(self):
        try:
            with self.connection.cursor() as cursor:
                # 旧的模板数据
                sql = "SELECT * FROM ida_express_template_value WHERE template_id = 3"
                cursor.execute(sql)
                template_value_list = cursor.fetchall()
                print 'size1: %s' % len(template_value_list)

                # 新的模板数据
                new_sql = "SELECT * FROM ida_express_template_value WHERE template_id = 106"
                cursor.execute(new_sql)
                new_template_value_list = cursor.fetchall()
                print 'size2: %s' % len(new_template_value_list)

                for template_value in template_value_list:
                    for new_template_value in new_template_value_list:
                        if new_template_value['field'] == template_value['field']:
                            update_sql = "update ida_express_template_value set width=%s, height=%s, offset_left=%s, offset_top=%s WHERE id = %s"
                            result = cursor.execute(update_sql, (new_template_value['width'], new_template_value['height'], new_template_value['offset_left'], new_template_value['offset_top'], template_value['id']))
                            print '----%s----update result: %s' % (template_value['id'], result)
                            continue
                # 最后提交修改
                self.connection.commit()
        except Exception, e:
            print '-------------------exception', e


# 测试入口
UpdateData().update_data()
