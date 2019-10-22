# Rentea House Crawler

A crawler that provides timely response to data change on public rental house platform.

## Main Feature

1. [x] Partial update on newly created house by given timestamp.
2. [ ] Full status check on entire dataset.
3. [ ] Publish house data to `rentea-db`

## System Requirement

1. Docker environment (recommended) - [Docker 18+](https://docs.docker.com/install/) and [docker-compose 1.18.0+](https://docs.docker.com/compose/install/), or
2. Host environment - Python 3.7.

## Setup

choose one of the options below (Docker or virtualenv) 

#### If you're gonna work in `Docker` Env

Build development image and update python package

```bash
docker-compose build crawler
```

#### Or, if you're gonna work in `virtualenv` 

1. Initialize a virtualenv

   ```bash
   virtualenv -p <python3.7 bin path> .venv
   . .venv/bin/activate
   ```

2. Install required package

   ```bash
   pip install -r requirements.txt
   ```

## Run Spider

This package now support only one crawler: `periodic591`, which is designed to perform partial update on 591 website.

In addition, it's recommended to enable persistent job queue to 
[control memory usage of request data](https://docs.scrapy.org/en/latest/topics/leaks.html#too-many-requests).

Supported parameter:

- `minuteago`: time range to look ahead
- `target_cities`: comma seperated list of city, use `台` instead of `臺`

To get new houses created in 591 in last 15 minutes:

```bash
scrapy crawl periodic591 -a minuteago=15 -s JOBDIR=data/spider-1
```

To get new houses created in an hour in 台南市 and 屏東縣:

```bash
scrapy crawl periodic591 -a minuteago=60 -a target_cities='台南市,屏東縣' -s JOBDIR=data/spider-1
```

To run crawler in docker, add `docker-compose run crawler` in beginning of command

```bash
docker-compose run crawler scrapy crawl periodic591 -a minuteago=15 -s JOBDIR=data/spider-1
```

## Testing

**Help Wanted!**

## Todo

1. Integrate with VSCode [remote development](https://code.visualstudio.com/blogs/2019/05/02/remote-development)
   - please install virtualenv in host for autocomplete for VSCode for now.
