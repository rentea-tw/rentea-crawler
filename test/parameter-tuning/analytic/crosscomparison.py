"""
Ignore minute_ago == 5 as it has too many false alarm

1. Show #house crawled per test
2. Show per-hour house overlap behavior across tests
"""
import argparse
from collections import namedtuple
from datetime import timedelta
import statistics
from peewee import fn, JOIN
from crawler.models import Task, TaskHouse

PerTestRecord = namedtuple('PerTestRecord', ['minute_ago', 'task_id', 'count'])

class PerHourRecord():
    def __init__(self, time):
        self.time = time
        self.occurrence = {}
        self.per_test_count = {}
    
    def append(self, minute_ago, house_id):
        if house_id not in self.occurrence:
            self.occurrence[house_id] = {}

        if minute_ago not in self.per_test_count:
            self.per_test_count[minute_ago] = 0

        occur = self.occurrence[house_id]
        if minute_ago not in occur:
            occur[minute_ago] = 0
            # ignore duplicated count in per_test_count
            self.per_test_count[minute_ago] += 1

        occur[minute_ago] += 1

    def get_coverage(self):
        ret = dict(tests={}, overall=[])
        total = len(self.occurrence.keys())

        # per test coverage
        for minute_ago in self.per_test_count.keys():
            coverage = self.per_test_count[minute_ago]/total*100
            ret['tests'][minute_ago] = coverage

        # per house coverage
        n_tests = len(self.per_test_count.keys())
        overall = []

        for house_id in self.occurrence.keys():
            appearance = len(self.occurrence[house_id].keys())
            ratio = appearance/n_tests*100
            overall.append(ratio)

        ret['overall'] = overall
        return ret

def house_crawled_per_test():
    n_occurrence = fn.COUNT (TaskHouse.house_id)

    house_counts = (Task
        .select(Task.minute_ago, Task.id, n_occurrence.alias('n'))
        .join(TaskHouse, JOIN.INNER)
        .where(Task.minute_ago > 5)
        .group_by(Task.minute_ago, Task.id)
    )

    stats = {}

    for count in house_counts:
        if count.minute_ago not in stats:
            stats[count.minute_ago] = []
        
        stats[count.minute_ago].append(
            PerTestRecord(count.minute_ago, count.id, count.n)
        )

    print('=== Number of (duplicated) house crawled per test ===')
    for minute_ago in sorted(stats.keys()):
        mean = statistics.mean(map(lambda x: x.count, stats[minute_ago]))
        print(f'Test[{minute_ago:02}] avg: {mean:6.1f}')
    print()

def compare_step_hour_data(target_time, hour_per_step):
    end_time = target_time + timedelta(minutes=1)
    start_time = end_time - timedelta(hours=hour_per_step)

    houses = (TaskHouse
        .select(Task.minute_ago, TaskHouse.house_id)
        .join(Task, JOIN.INNER)
        .where(
            Task.created_at <= end_time,
            Task.created_at > start_time,
            Task.minute_ago > 5
        )
    )

    hourly_record = PerHourRecord(target_time)

    for house in houses:
        hourly_record.append(house.task_id.minute_ago, house.house_id)

    return hourly_record.get_coverage()

def per_house_overlap(hour_per_step):
    time_range = (Task
        .select(
            fn.MAX(Task.created_at).alias('max_created_at'),
            fn.MIN(Task.created_at).alias('min_created_at'),
        )
        .get()
    )

    time_cursor = time_range.min_created_at.replace(
        minute=0,
        second=0,
        microsecond=0
    )
    one_step = timedelta(hours=hour_per_step)

    start_time = time_cursor
    end_time = time_range.max_created_at
    time_duration = end_time - start_time
    time_cursor += one_step
    per_test_coverage = {}
    overall_coverage = []

    print(f'=== Every {hour_per_step} Hours Coverage ===')
    print('progress:  0%', end='\r')

    while time_cursor < end_time:
        progress = (time_cursor - start_time) / time_duration
        print(f'progress:  {progress*100:5.1f}%', end = '\r')

        stats = compare_step_hour_data(time_cursor, hour_per_step)

        for minute_ago in stats['tests'].keys():
            if minute_ago not in per_test_coverage:
                per_test_coverage[minute_ago] = []
            per_test_coverage[minute_ago].append(stats['tests'][minute_ago])

        overall_coverage += stats['overall']

        time_cursor += one_step

    for minute_ago in sorted(per_test_coverage.keys()):
        mean = statistics.mean(per_test_coverage[minute_ago])
        stdev = statistics.stdev(per_test_coverage[minute_ago])
        print(f'Test[{minute_ago:02}] coverage avg: {mean:5.1f}%, std: {stdev:5.1f}%')

    mean = statistics.mean(overall_coverage)
    stdev = statistics.stdev(overall_coverage)
    print(f'Overall  coverage avg: {mean:5.1f}%, std: {stdev:5.1f}%')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--hour_per_step',
        '-s',
        default=24,
        type=int,
        help='Hours per step'
    )
    args = parser.parse_args()

    house_crawled_per_test()
    per_house_overlap(args.hour_per_step)
