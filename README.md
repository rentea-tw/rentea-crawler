# Rentea House Crawler

A crawler that provides timely response to data change on public rental house platform.

## Main Feature

1. [ ] Partial update on newly created house by given timestamp.
2. [ ] Full status check on entire dataset.
3. [ ] Publish house data to `rentea-db`

## System Requirement

1. Docker 18+ && docker-compose 1.18.0+, when using Docker as development environment.
2. Python 3.7, when using host environment.

## Setup

### Using Docker Env (Recommended)

1. Install [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)
2. Build development image and update python package
   > docker-compose build crawler
3. Execute docker image
   > docker-compose up crawler

### Using virtualenv

1. Initialize a virtualenv
   > virtualenv -p <python3.7 bin path> .venv
   > . .venv/bin/activate
2. Install required package
   > pip install -r requirements.txt

## Testing

TBD

## Todo

1. Integrate with VSCode [remote development](https://code.visualstudio.com/blogs/2019/05/02/remote-development)
