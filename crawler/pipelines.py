import time
from os import path
from scrapy.exporters import JsonLinesItemExporter
from scrapy_twrh.items import GenericHouseItem

class SimpleJsonExporter(object):
    """Write result into .jsonl for POC"""

    def open_spider(self, spider):
        now = time.strftime('%Y%m%d-%H%M%S')
        filename = path.join(path.dirname(__file__), f'../data/{now}.jsonl')
        fh = open(filename, 'wb')
        self.exporter = JsonLinesItemExporter(fh, encoding="utf-8")
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.exporter.file.close()

    def process_item(self, item, spider):
        if isinstance(item, GenericHouseItem):
            self.exporter.export_item(item)
        return item
