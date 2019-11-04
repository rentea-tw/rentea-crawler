from collections import namedtuple
from datetime import timedelta
from crawler.models import Task
import statistics

CRONTAB_BUFFER_SEC = 10

class PerPeriodRecord():
    def __init__(self, minute_ago):
        self.minute_ago = minute_ago
        self.tasks = []
        self.miss_count = 0

    def append(self, task):
        self.tasks.append(task)

    def miss(self, count = 1):
        self.miss_count += count

def count_late(task, time_cursor, period_sec):
    time_after_prev = (task.created_at - time_cursor).total_seconds()
    if time_after_prev - CRONTAB_BUFFER_SEC > period_sec:
        return round(time_after_prev / period_sec) - 1
    return 0

def analyze():
    tasks = (Task
        .select()
        .where(Task.minute_ago != 1)
        .order_by(Task.minute_ago.asc(), Task.created_at.asc())
    )

    records = {}
    time_cursor = 0

    for task in tasks:
        period = task.minute_ago
        period_sec = timedelta(minutes=task.minute_ago).total_seconds()
        if period not in records:
            records[period] = PerPeriodRecord(period)
            time_cursor = task.created_at - timedelta(minutes=period)
        
        records[period].append(task)
        n_late = count_late(task, time_cursor, period_sec)
        if n_late > 0:
            records[period].miss(n_late)

        time_cursor = task.created_at

    for period in records.keys():
        record = records[period]
        minute_takens = list(filter(
            lambda x: x is not None,
            map(lambda task: task.minute_taken, record.tasks)
        ))
        stdev = statistics.stdev(minute_takens)
        mean = statistics.mean(minute_takens)
        median = statistics.median(minute_takens)
        shortest = min(minute_takens)
        longest = max(minute_takens)

        print((
            f'Test[{period:02}], total: {len(record.tasks):5} jobs, miss {record.miss_count:4} jobs, '
            f'mean: {mean:.1f} min, median: {median:.1f} min, range: [{longest:4.1f}-{shortest:4.1f}] min, '
            f'stdev: {stdev:.1f} min'
        ))

if __name__ == "__main__":
    analyze()
