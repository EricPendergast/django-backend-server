from __future__ import unicode_literals
from mongoengine import *
from .users import Group


class Watcher(Document):
    """
    Watcher saves...
    """

    """
    Primary item information
    """
    sku_id = StringField()  # Unique for evert product
    product_name = StringField()
    item_url = StringField()  # Product url

    default_price = FloatField()
    final_price = FloatField()  # Float or "None"

    seller_name = StringField()
    seller_url = StringField()  # Seller url

    images = ListField()  # List of image file name

    platform = StringField()
    current_stock = ListField(DictField())

    comments_count = FloatField()

    """
    Secondary item information
    """
    bundle = ListField(DictField())
    detail = ListField(DictField())
    support = ListField(DictField())
    model = DictField()

    seller_location = StringField()
    sales_count = FloatField()

    """
    Searching information
    """
    search_keyword = StringField()
    search_rank = IntField()
    search_order = StringField()
    last_crawling_timestamp = DateTimeField()
    group = ReferenceField(Group)
