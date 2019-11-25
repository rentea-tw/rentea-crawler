"""
1. Show overall stats. of per house duplication per test
2. Show duplication rate between consecutive job
"""
import statistics
from collections import namedtuple
from peewee import fn, JOIN
from crawler.models import Task, TaskHouse

def get_overall_stats(minute_ago):
    # house_occurrence = []

    n_occurrence = fn.COUNT(TaskHouse.house_id)

    house_stats = (TaskHouse
        .select(TaskHouse.house_id, n_occurrence.alias('n_dup'))
        .join(Task, JOIN.INNER)
        .where(Task.minute_ago == minute_ago)
        .group_by(TaskHouse.house_id)
    )

    house_occurrence = list(map(
        lambda row: row.n_dup,
        house_stats
    ))

    n_house_occurrence = len(house_occurrence)

    n_jobs = (
        Task
            .select(fn.COUNT(Task.id).alias('n_jobs'))
            .where(Task.minute_ago == minute_ago)
            .get()
    ).n_jobs

    dup_houses = list(filter(lambda n: n > 1, house_occurrence))
    
    stdev = statistics.stdev(dup_houses)
    mean = statistics.mean(dup_houses)
    median = statistics.median(dup_houses)
    low = min(dup_houses)
    high = max(dup_houses)
    n_dup = len(dup_houses)

    print(
        f'Test[{minute_ago:02}], '
        f'get {n_house_occurrence:6} houses during {n_jobs:5} jobs. '
        f'{n_house_occurrence/n_jobs:5.1f} houses per job. '
        f'{n_dup:3} dup houses. '
        f'Dup stats: mean/median/stdev [{mean:5.1f}/{median:3.0f}/{stdev:5.1f}], '
        f'range [{high:5}-{low:1}]'
    )

JobStats = namedtuple('JobStats', ['total', 'n_dup', 'dup_rate'])

def get_jobs_stats(minute_ago):
    cur_job = {}
    stats = []

    jobs = (
        Task
            .select(Task.id)
            .where(Task.minute_ago == minute_ago)
            .order_by(Task.created_at.asc())
    )

    for job in jobs:
        houses = (
            TaskHouse
                .select(TaskHouse.house_id)
                .where(TaskHouse.task_id == job.id)
        )
        new_job = {}
        total = 0
        n_dup = 0

        for house in houses:
            hid = house.house_id
            new_job[hid] = 0
            total += 1
            if hid in cur_job:
                cur_job[hid] += 1
                n_dup += 1

        if total and cur_job.keys():
            stats.append(JobStats(total, n_dup, n_dup*100/total))

        cur_job = new_job

    dup_rates = list(map(lambda stats: stats.dup_rate, stats))
    mean_rate = statistics.mean(dup_rates)
    std_rate = statistics.stdev(dup_rates) 
    max_rate = max(dup_rates)
    min_rate = min(dup_rates)

    print(
        f'Test[{minute_ago:02}], '
        f'mean/stdev [{mean_rate:5.1f}% /{std_rate:5.1f}%], '
        f'man/min [{max_rate:5.1f}% -{min_rate:5.1f}%]'
    )


def analyze():
    test_params = list(map(
        lambda row: row.minute_ago,
        Task.select(Task.minute_ago)
            .distinct()
            .where(Task.minute_ago != 1)
            .order_by(Task.minute_ago.asc())
    ))

    print('=== Overall Stats ===')
    for minute_ago in test_params:
        get_overall_stats(minute_ago)

    print('\n=== Consecutive Job Stats ===')
    for minute_ago in test_params:
        get_jobs_stats(minute_ago)
     
if __name__ == "__main__":
    analyze()