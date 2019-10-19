#!/bin/bash -e

if [ "$#" -ne 1 ]; then
  >&2 echo "usage: $0 <minuteago>"
  exit 1
fi

cd `dirname $0`

minute_ago="$1"

cmd="scrapy crawl periodic591 -a minuteago=$minute_ago -s JOBDIR=data/minuteago-$minute_ago"

## Check if test is running
ps_count=`ps ax | grep "$cmd" | wc -l`

if [ "$ps_count" -gt 1 ]; then
  >&2 echo "test with the same minuteago($minute_ago) is running, skip test"
  exit 2
fi

## Run test
log_path=data/`date '+%Y%m%d-%H%M%S'`-minuteago-$minute_ago.log

echo `date '+%Y-%m-%d %H:%M:%S'` Start testing, minute ago = $minute_ago

$cmd >$log_path 2>&1
