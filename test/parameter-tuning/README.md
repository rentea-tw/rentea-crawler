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

To run analysis without waiting for data collection, please download [2 weeks sample data](https://drive.google.com/open?id=1RJy5dmZKKRg0Ztwkr49U1O_3SNQzh-G6) and restore it by

```bash
unzip 1019-1104.sql.zip
cd test/parameter-tuning
cat 1019.1104.sql | sqlite3 data/db.sqlite
```

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

### Duplication Detection

```bash
python -m analytic.dupdetect
```

Example result:

```
=== Overall Stats ===
Test[05], get   3102 houses during   137 jobs.  22.6 houses per job. 1575 dup houses. Dup stats: mean/median/stdev [ 20.9/ 13/ 25.7], range [  134-2]
Test[15], get  46037 houses during  1469 jobs.  31.3 houses per job. 2142 dup houses. Dup stats: mean/median/stdev [169.6/ 99/266.8], range [ 1468-2]
Test[30], get  48221 houses during   741 jobs.  65.1 houses per job. 1934 dup houses. Dup stats: mean/median/stdev [ 97.3/ 66/138.6], range [  740-2]
Test[60], get  48458 houses during   371 jobs. 130.6 houses per job. 1770 dup houses. Dup stats: mean/median/stdev [ 57.9/ 44/ 70.7], range [  371-2]

=== Consecutive Job Stats ===
Test[05], mean/stdev [ 47.9% /  2.8%], man/min [ 55.5% - 41.6%]
Test[15], mean/stdev [ 45.4% /  4.1%], man/min [ 56.0% - 32.8%]
Test[30], mean/stdev [ 41.4% /  6.2%], man/min [ 55.3% - 28.5%]
Test[60], mean/stdev [ 37.1% /  7.6%], man/min [ 53.2% - 20.7%]
```

### Equivalency Analysis

```bash
python -m analytic.crosscomparison
```

Example result:

```
=== Number of (duplicated) house crawled per test ===
Test[15] avg:  277.3
Test[30] avg:  316.8
Test[60] avg:  402.1

=== Overall Coverage ===
Test[15] coverage avg:  80.4%, std:   5.7%
Test[30] coverage avg:  62.0%, std:   5.9%
Test[60] coverage avg:  48.8%, std:   9.3%
Overall  coverage avg:  64.8%, std:  28.2%
```
