# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import pymysql
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    """
    自定义处理数据写入json文件
    """
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        """
        处理 item
        :return: 
        """
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_close(self, spider):
        self.file.close()


class MysqlPipeline(object):
    """
    同步机制写入mysql数据
    """
    def __init__(self):
        self.conn = pymysql.connect(host="localhost", user="root", password="zhou_123", db="article_spider", port=3306, charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        inster_sql = "INSERT INTO jobbole_article(title, create_date, url,  url_object_id, front_image_url, front_image_path, comment_nums, fav_nums, praise_nums, tags, content) VALUES " \
                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(inster_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'], item['front_image_path'],
                                         item['comment_nums'], item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
        self.conn.commit()


class MysqlTwistePipeline(object):
    """
    数据量过大,twiste提供异步插入数据
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        host = settings['MYSQL_HOST'],
        dbprams = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass = pymysql.cursors.DictCursor,
        )

        dbpool = adbapi.ConnectionPool("pymysql", **dbprams)
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将mysql插入变成异步执行
        :param item: 
        :param spider: 
        :return: 
        """
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        """
        处理异步插入异常
        :return: 
        """
        print(failure)

    def do_insert(self, cursor, item):
        """
        执行具体的插入
        :param cursor: 
        :param item: 
        :return: 
        """
        inster_sql = "INSERT INTO jobbole_article(title, create_date, url,  url_object_id, front_image_url, front_image_path, comment_nums, fav_nums, praise_nums, tags, content) VALUES " \
                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(inster_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'], item['front_image_path'],
                                         item['comment_nums'], item['fav_nums'], item['praise_nums'], item['tags'], item['content']))



class JsonExporterPipeline(object):
    """
    调用scrapy提供的json_export导出json文件
    """
    def __init__(self):
        self.file = open("articleexport.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    """
    重写 ImagesPipeline 的 item_completed方法, 获取图片路径
    """
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item

