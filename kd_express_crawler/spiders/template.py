# -*- coding: utf-8 -*-
import json

import requests
import scrapy
from scrapy.loader import ItemLoader

from kd_express_crawler.items import ExpressTemplateItem


# 爬取传统快递五联单模板配置信息
class TemplateSpider(scrapy.Spider):
    name = "express_template"
    allowed_domains = ["kd118.com"]
    start_urls = ['http://www.kd118.com/']
    # 构建登录后cookies信息，以授权申请
    cookies = {}
    cookie_str = 'ASP.NET_SessionId=m2nvrfdpayffll5zloczxxyg'
    cookies_array = cookie_str.split(';')
    for cookie in cookies_array:
        key, value = cookie.split('=', 1)
        cookies[key] = value
    # 可以不传
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

    def parse(self, response):
        # print response.text
        # 快递公司名称URL
        company_url = 'http://www.kd118.com/template/expresscompany'
        # 根据快递公司名查询模板列表URL
        template_url = 'http://www.kd118.com/template/gettemplatelist'
        # 模板基础信息
        setting_url = 'http://www.kd118.com/template/gettemplate'
        # 模板字段信息
        field_url = 'http://www.kd118.com/template/gettemplatedetailnor'

        # 查询快递公司列表
        res_text = requests.post(company_url, cookies=self.cookies).text
        # print 'res_text: ', res_text
        express_list = json.loads(res_text)['message']
        for express in express_list:
            express_id = express['id']
            express_name = express['uname']
            # TODO 只拿模板 顺丰速运
            # if u'顺丰速运' != express_name:
            #     continue
            print express_id, express_name
            # 根据快递名字查询快递模板列表
            tmpl_list = []
            template_text = requests.post(template_url, {'ec': express_name}, cookies=self.cookies).text
            print '----express_name: %s----template_text: %s' % (express_name, template_text)
            template_list = json.loads(template_text)['message']
            for template in template_list:
                template_id = template['id']
                template_name = template['uname']
                # TODO 只拿模板 顺丰2016 数据
                # if u'顺丰2016' != template_name:
                #     continue
                # 根据模板ID查询模板配置信息
                setting_text = requests.post(setting_url, {'id': template_id}, cookies=self.cookies).text
                print '----template_name: %s----setting_text: %s' % (template_name, setting_text)
                setting_json = json.loads(setting_text)['message']
                tmpl = {'template_type': 1,  # 传统五联单
                        'template_name': template_name,
                        'image': setting_json['backPic'],
                        'width': setting_json['width'],
                        'height': setting_json['height'],
                        'left': setting_json['fixLeft'],
                        'top': setting_json['fixTop']}

                # 根据模板ID查询模板字段信息
                res_text = requests.post(field_url, {'id': template_id}, cookies=self.cookies).text
                res_json = json.loads(res_text)
                detail_list = res_json['detaillist']
                field_list = []
                for detail in detail_list:
                    field = {}
                    field['field_name'] = detail['fieldDisplayText']  # field 在写库前转换
                    field['fix_value'] = detail['fixValue']  # 固定值，比如 '发件人：'
                    attr_list = detail['attributes'].split(',')
                    field['left'] = attr_list[0]
                    field['top'] = attr_list[1]
                    field['width'] = attr_list[2]
                    field['height'] = attr_list[3]
                    field_list.append(field)
                tmpl['field_list'] = field_list
                tmpl_list.append(tmpl)
            yield self.parse_item(express_name, tmpl_list)

    def parse_item(self, express_name, tmpl_list):
        item = ItemLoader(item=ExpressTemplateItem())
        # item 的value 必须是str类型的，否则放进去不报错，后面使用的时候，报KeyError
        item.add_value('express_name', express_name)
        item.add_value('template_list', json.dumps(tmpl_list))
        print '-----express_name: %s------template_list: %s' % (express_name, tmpl_list)
        return item.load_item()
