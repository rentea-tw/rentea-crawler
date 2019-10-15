#!/bin/bash -e

if [ "$#" -ne 1 ]; then
  >&2 echo "usage: $0 <minuteago>"
  exit 1
fi

cd `dirname $0`

ip_def='ip-list.json'
minute_ago="$1"
ip=''

## Get binding addr if specified
if [ -e $ip_def ]; then
  ip=`cat $ip_def | jq .[\"$minute_ago\"]`
fi

cmd="scrapy crawl periodic591 -a minuteago=$minute_ago -s JOBDIR=data/minuteago-$minute_ago"

if [ "$ip" != "null" ] && [ "$ip" != "" ]; then
  cmd="$cmd -a bind=$ip"
fi

## Check if test is running
ps_count=`ps ax | grep "$cmd" | wc -l`

if [ "$ps_count" -gt 1 ]; then
  >&2 echo "test with the same minuteago($minute_ago) is running, skip test"
  exit 2
fi

## Run test
log_path=data/`date '+%Y%m%d-%H%M%S'`-minuteago-$minute_ago.log

echo `date '+%Y-%m-%d %H:%M:%S'` Start testing, minute ago = $minute_ago, ip = $ip

$cmd >$log_path 2>&1
