from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.watcher import *


class GeneralWatcherSerializer(DocumentSerializer):
    class Meta:
        model = Watcher
        depth = 2
        fields = [
            'sku_id', 'product_name', 'item_url', 'default_price', 'final_price', 'seller_name', 'seller_url', 'images',
            'platform', 'current_stock', 'comments_count', 'bundle', 'detail', 'support', 'model', 'seller_location',
            'sales_count', 'search_keyword', 'search_rank', 'search_order', 'last_crawling_timestamp', ]
