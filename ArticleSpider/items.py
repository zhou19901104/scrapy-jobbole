# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobble(self, value):
    return value + "-bbole"


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        # 获取当前日期
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    """
    去掉tags中提取的评论字样
    :param value: 
    :return: 
    """
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    """
    数据保持原有的值
    :param value: 
    :return: 
    """
    return value


class ArticleItemLoader(ItemLoader):
    """
    继承自ItemLoader，自定义itemloader,集中处理取出item列表第一个数据
    """
    default_output_processor = TakeFirst()



class JobBoleArticleItem(scrapy.Item):



    """
    配置item字段
    """
    # title = scrapy.Field()
    # create_date = scrapy.Field()
    # url = scrapy.Field()
    # url_object_id = scrapy.Field()
    # front_image_url = scrapy.Field()
    # front_image_path = scrapy.Field()
    # praise_nums = scrapy.Field()
    # comment_nums = scrapy.Field()
    # fav_nums = scrapy.Field()
    # tags = scrapy.Field()
    # content = scrapy.Field()


    """
    配置Item字段，并对字段进行处理
    """
    title = scrapy.Field()  # input_processor = MapCompose(lambda x:x+"-jobbole",add_jobble)

    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert), # date时间处理
        output_processor = TakeFirst() # 只取列表第一个
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    # 保持原有的列表值
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(",")
    )
    content = scrapy.Field()
