# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy.conf import settings
import pymongo

class DuplicatesPipeline(object):
    def __init__(self):
        self.jid_set = set()

        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbName = settings['MONGODB_DBNAME']
        collection_name = settings['MONGODB_DOCNAME']

        client = pymongo.MongoClient(host=host, port=port)
        db = client[dbName]

        items = db[collection_name].find({}, {'pid':1}).sort('pid')
        for item in items:
            self.jid_set.add(item['pid'])

        client.close()

    def process_item(self, item, spider):
        pid = item['pid']
        if pid in self.jid_set:
            raise DropItem("Duplicate job found:%s" % item)

        self.jid_set.add(pid)
        return item


class MongoPipeline(object):

    #collection_name = 'scrapy_items'

    def __init__(self):
        self.host = settings['MONGODB_HOST']
        self.port = settings['MONGODB_PORT']
        self.dbName = settings['MONGODB_DBNAME']
        self.collection_name = settings['MONGODB_DOCNAME']
        #client = pymongo.MongoClient(host=host, port=port)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.host, port=self.port)
        self.db = self.client[self.dbName]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
