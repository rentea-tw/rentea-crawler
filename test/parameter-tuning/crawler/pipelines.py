import uuid
from datetime import datetime
from os import path
from scrapy_twrh.items import GenericHouseItem
from .models import Task, TaskHouse

SEC_PER_MIN = 60

class TestRecorder(object):
    """Write result into sqlite for test validation"""

    def open_spider(self, spider):
        task = Task(id=uuid.uuid4(), minute_ago=spider.minute_ago)
        self.task = task
        task.save(force_insert=True)

    def close_spider(self, spider):
        self.task.end_time = datetime.now()
        total_sec = (self.task.end_time - self.task.created_at).total_seconds()
        self.task.minute_taken = total_sec / SEC_PER_MIN
        self.task.save()

    def process_item(self, item, spider):
        if isinstance(item, GenericHouseItem):
            house, created = TaskHouse.get_or_create(
                task_id=self.task.id,
                house_id=item['vendor_house_id']
            )
            if created:
                house.update_count = 0
            
            house.update_count = house.update_count + 1
            house.per_ping_price = item['per_ping_price']
            house.save()

        return item
