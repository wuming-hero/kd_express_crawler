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
        express_name = item['express_name']
        template_list = json.loads(item['template_list'][0])
        now = self.daytime_formate(datetime.now())
        try:
            with self.connection.cursor() as cursor:
                # 插入快递公司
                sql = 'SELECT * FROM ida_express WHERE name = %s'
                cursor.execute(sql, express_name)
                # 获取查询结果
                express = cursor.fetchone()
                if express:
                    print 'express: %s exist, expressId is: %s' % (express_name, express['id'])
                    express_id = express['id']
                else:
                    sql = "INSERT INTO ida_express (name, created_at, updated_at) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (express_name, now, now))
                    express_id = cursor.lastrowid
                print '++++express_id: %s' % express_id

                # 插入模板
                for template in template_list:
                    image_url = '%s%s' % (self.image_url, template['image'])
                    data = (express_id, express_name, template['template_name'], template['template_type'], image_url,
                            template['width'], template['height'], template['left'], template['top'], now, now)
                    sql = "INSERT INTO ida_express_template (express_id, express_name, name, type, image_url, width, height, offset_left, offset_top, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
                    cursor.execute(sql, data)
                    template_id = cursor.lastrowid
                    field_list = template['field_list']
                    for field in field_list:
                        field_name = field['field_name']
                        fix_value = field['fix_value']  # 固定值，需要特殊处理，电子面单的时候，表示fieldName
                        if field_name == u'http://www.kd118.net':
                            # 五联单的时候有这个固定条目，此处忽略
                            continue
                        # 根据fix_value 有无拆分成两个逻辑，保证正常逻辑没问题
                        if fix_value:
                            field_data = (template_id, field_name, self.get_field_type(field_name, fix_value),
                                          field['width'], field['height'], field['left'], field['top'], fix_value, now, now)
                            sql = "INSERT INTO ida_express_template_value (template_id, field_name, field_type, width, height, offset_left, offset_top, value, created_at, updated_at) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
                            cursor.execute(sql, field_data)
                        else:
                            field_data = (template_id, field_name, self.get_field_key(field_name),
                                          self.get_field_type(field_name, None), field['width'], field['height'],
                                          field['left'], field['top'], now, now)
                            # print '---->>>>field value data: ', field_data
                            sql = "INSERT INTO ida_express_template_value (template_id, field_name, field, field_type, width, height, offset_left, offset_top, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
                            # print '---->>>>insert field value sql: %s' % sql
                            cursor.execute(sql, field_data)
            # connection is not autocommit by default. So you must commit to save your changes.
            self.connection.commit()
        except Exception, e:
            print '-------------------exception', e
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
            u'收件人公司': 'consigneeCompany',
            u'订单号码': 'orderNo',
            u'快递单号': 'expressNo',
            u'快递单号条码': '快递单号条码',
            u'目的地城市': 'destination'}
        return field_dict[field]

    def get_field_type(self, field, fix_value):
        field_type = 1  # 发件人field
        consignee_field_type_dict = {
            u'收件人姓名': 'consigneeName',
            u'收件人昵称': 'consigneeNickName',
            u'收件人手机': 'consigneeMobile',
            u'收件人固话': 'consigneePhone',
            u'收件人省': 'consigneeProvince',
            u'收件人市': 'consigneeCity',
            u'收件人区/县': 'consigneeArea',
            u'收件人详细地址': 'consigneeAddress',
            u'收件人邮编': 'consigneePostcode',
            u'收件人公司': 'consigneeCompany'}
        if fix_value:
            field_type = 3  # 文本固定值
        elif consignee_field_type_dict.has_key(field):
            field_type = 2  # 收件人field
        return field_type
