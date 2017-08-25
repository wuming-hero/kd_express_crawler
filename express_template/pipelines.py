# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from datetime import datetime

import pymysql as pymysql


class ExpressTemplatePipeline(object):
    image_url = 'http://www.kd118.com/templateimg/'

    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password="123456",
                                          db='ixiye_ida',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def process_item(self, item, spider):
        print "----------item: %s" % item
        express_name = item['express_name']
        template_list = json.loads(item['template_list'][0])
        now = self.daytime_formate(datetime.now())
        print '==========%s=====%s========' % (express_name, now)
        try:
            with self.connection.cursor() as cursor:
                # 插入快递公司
                sql = "INSERT INTO ida_express (name, created_at, updated_at) VALUES (%s, %s, %s)"
                cursor.execute(sql, (express_name, now, now))
                express_id = cursor.lastrowid
                print '++++express_id: %s' % express_id

                # 插入模板
                for template in template_list:
                    image_url = '%s%s' % (self.image_url, template['image'])
                    insert_data = (express_id, express_name, template['template_name'], image_url,
                                   template['width'], template['height'], template['left'], template['top'], now, now)
                    sql = "INSERT INTO ida_express_template (express_id, express_name, name, image_url, width, height, offset_left, offset_top, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
                    cursor.execute(sql, insert_data)
                    template_id = cursor.lastrowid
                    field_list = template['field_list']
                    for field in field_list:
                        field_name = field['fieldName']
                        if not field_name == u'http://www.kd118.net':
                            insert_data = (template_id, field_name, self.get_field_key(field_name),
                                           self.get_field_type(field_name), field['width'], field['height'],
                                           field['left'], field['top'], now, now)
                            sql = "INSERT INTO ida_express_template_value (template_id, field_name, field, field_type, width, height, offset_left, offset_top, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
                            cursor.execute(sql, insert_data)
            # connection is not autocommit by default. So you must commit to save your changes.
            self.connection.commit()
        except Exception, e:
            print '-----------------------', e
            # finally:
            #     connection.close()

    def daytime_formate(self, date):
        if date is None: return ""
        return date.strftime('%Y-%m-%d %H:%M:%S')

    def get_field_key(self, field):
        field_dict = {
            u'发件日期': 'printTime',
            u'内装货品': 'title',
            u'发件人姓名': 'consignorName',
            u'发件人昵称': 'consignorNickName',
            u'发件人电话': 'consignorMobile',
            u'发件人固定电话': 'consignorPhone',
            u'发件人省份': 'consignorProvince',
            u'发件人城市': 'consignorCity',
            u'发件人区/县': 'consignorArea',
            u'发件人地址': 'consignorAddress',
            u'发件人邮编': 'consignorPostcode',
            u'发件人公司': 'consignorCompany',
            u'收件人姓名': 'consigneeName',
            u'收件人昵称': 'consigneeNickName',
            u'收件人手机': 'consigneeMobile',
            u'收件人固话': 'consigneePhone',
            u'收件人省': 'consigneeProvince',
            u'收件人市': 'consigneeCity',
            u'收件人区/县': 'consigneeArea',
            u'收件人详细地址': 'consigneeAddress',
            u'收件人邮编': 'consigneePostcode',
            u'收件人公司': 'consigneeCompany'
        }
        return field_dict[field]

    def get_field_type(self, field):
        field_type = 1
        field_dict = {
            u'收件人姓名': 'consigneeName',
            u'收件人昵称': 'consigneeNickName',
            u'收件人手机': 'consigneeMobile',
            u'收件人固话': 'consigneePhone',
            u'收件人省': 'consigneeProvince',
            u'收件人市': 'consigneeCity',
            u'收件人区/县': 'consigneeArea',
            u'收件人详细地址': 'consigneeAddress',
            u'收件人邮编': 'consigneePostcode',
            u'收件人公司': 'consigneeCompany'
        }
        if field_dict.has_key(field):
            field_type = 2
        return field_type
