import pymongo
import sys
from .items import OercommonsItem
import certifi

class MongoDBPipeline:

    collection = 'oercommons_test'

    def __init__(self, mongodb_uri, mongodb_db):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        if not self.mongodb_uri: sys.exit("You need to provide a Connection String.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE', 'moodlerec')
        )

    def open_spider(self, spider):
        ca = certifi.where()
        self.client = pymongo.MongoClient(self.mongodb_uri, tlsCAFile=ca)
        self.db = self.client[self.mongodb_db]
        # Start with a clean database
        # self.db[self.collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = dict(OercommonsItem(item))
        try:
            self.db[self.collection].insert_one(data)
        except pymongo.errors.DuplicateKeyError:
            print("duplicate")
        return item