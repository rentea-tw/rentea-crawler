from os import path
from datetime import datetime
from peewee import Model, CharField, DateTimeField, \
    ForeignKeyField, IntegerField, FloatField, SqliteDatabase

db = SqliteDatabase(path.join(path.dirname(__file__), '../data/db.sqlite'))

class TimestampModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Task(TimestampModel):
    minute_ago = IntegerField()
    end_time = DateTimeField(null=True)
    minute_taken = FloatField(null=True)

    class Meta:
        database = db

class TaskHouse(TimestampModel):
    task_id = ForeignKeyField(Task, backref='houses')
    house_id = CharField()
    per_ping_price = IntegerField(null=True)
    update_count = IntegerField(default=0)

    class Meta:
        database = db
        indexes = (
            (('task_id', 'house_id'), True),
        )

db.create_tables([Task, TaskHouse])
