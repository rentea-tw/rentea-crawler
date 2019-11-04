# Parameter Tuning Test

This test aims to find optimized `minuteago` parameter for rentea-crawler, so that

1. Crawler can perform all its work in `minuteago` 24 hours a day, 7 days a week.
2. Reduce target website #request at best
3. The higher update frequency the better

## System Requirement

1. Python 3.7
2. See `requirements.txt` in this test folder
3. jq

## Test Design and Assumption

This test will measure performance of `periodic591` crawler directly, but ignore network delay and potential DB latency.

Each round of test consists of multiple crawler job, which use different `minuteago` and run for the same test period.

Each crawler job is triggered by script. The script guarantees there will be at most one crawler bind to an 
external IP at a time and records the following info in sqlite for later analysis:

1. Job ID, start time, end time, time spent, and `minuteago` of the test.
2. House ID, time crawled, and per_ping_price collected during this test.

There will be follow up analysis after all jobs are done:

1. Execution time analysis.
   - Verify whether there is job takes more than its `minuteago`. If yes, show related job info and stats.
   - Verify whether there is job not executed, so we can do cross reference.
2. Duplication detection in the same `minuteago` job.
   - Check whether there's chance to get a house more than one time. If yes, show related job and house info.
3. Equivalency of different `minuteago` job.
   - Check whether we can get the same set of house in the same time period no matter what `minuteago` we set.
   - If not, populate the diff set.

A valid `minuteago` should at least past analysis 1. If analysis 2 or 3 shows abnormal event, we may need to adjust crawler design and redo this test.

## Test Plan

The test will start from simple and increase its complexity by iteration.

1. Test 1 - test with `minuteago` = [5min] for 1 hour.
2. Test 2 - test with `minuteago` = [5min, 15min] for 1 hour.
3. Test 3 - test with `minuteago` = [5min, 15min] for 1 day.
4. Test 4 - test with `minuteago` = [5min, 15min, 30min, 60min] for 1 day.
5. Test 5 - test with `minuteago` = [5min, 15min, 30min, 60min] for 7 days.

## How to Run Test

Run the following commands in current directory.

```bash
# Enable virtualenv if needed
. .venv/bin/activate

pip install -r requirements.txt

./run.sh <minuteago>

```

## How to Run Analysis

After enable virtualenv, type the following command under directory `test/parameter-tuning`.

### Execution Time Analysis

```bash
python -m analytic.executiontime
```

Example result:

```
Test[05], total:   137 jobs, miss 4397 jobs, mean: 11.5 min, median: 11.4 min, range: [13.0- 8.1] min, stdev: 0.7 min
Test[15], total:  1469 jobs, miss   52 jobs, mean: 12.3 min, median: 12.2 min, range: [17.2-10.6] min, stdev: 1.2 min
Test[30], total:   741 jobs, miss    0 jobs, mean: 14.1 min, median: 13.4 min, range: [23.3-10.5] min, stdev: 2.8 min
Test[60], total:   371 jobs, miss    0 jobs, mean: 18.0 min, median: 16.7 min, range: [35.8-10.8] min, stdev: 6.0 min
```
