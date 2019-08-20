""" Get 591's most recently created house

This module crawl 591 website with following criteria:

1. only crawl house that is created in last <minuteago> minutes
2. only yield DetailHouseItem once, which include location and entire meta dataset

Usage:

```
scrapy crawl periodic591 -a minuteago=<int>
```

"""

import json
import logging
from datetime import datetime, timedelta
from scrapy import Request
from scrapy_twrh.spiders.rental591 import Rental591Spider, util
from scrapy_twrh.spiders.rental591.all_591_cities import all_591_cities
from scrapy_twrh.spiders.util import clean_number

DEFAULT_MINUTEAGO = 60

class Periodic591Spider(Rental591Spider):
    name = 'periodic591'

    def __init__(self, minuteago, **kwargs):
        try:
            minuteago = int(minuteago)
        except ValueError:
            minuteago = DEFAULT_MINUTEAGO

        time_ago = datetime.now() - timedelta(minutes=minuteago)
        self.epoch_ago = time_ago.timestamp()
        self.count_per_city = {}

        for city in all_591_cities:
            self.count_per_city[city['city']] = 0

        super().__init__(
            **kwargs,
            parse_list=self.periodic_parse_list
        )

    def periodic_parse_list(self, response):
        data = json.loads(response.text)
        meta = response.meta['rental']

        houses = data['data']['topData'] + data['data']['data']
        has_outdated = False

        for house in houses:
            house['is_vip'] = 'id' not in house

            # updatetime == creation time in 591...
            if not house['is_vip'] and house['updatetime'] < self.epoch_ago:
                has_outdated = True
            else:
                house_item = self.gen_shared_attrs(house, meta)
                yield self.gen_detail_request(util.DetailRequestMeta(
                    house_item['vendor_house_id'], False))
                if meta.name in self.count_per_city:
                    self.count_per_city[meta.name] += 1

        if data['data']['data'] and not has_outdated:
            # only goto next page when there's response and not outdated
            yield self.gen_list_request(util.ListRequestMeta(
                meta.id,
                meta.name,
                meta.page + 1
            ))
        else:
            logging.info(f'[{meta.name}] total {self.count_per_city[meta.name]} house to crawl!')

    def gen_list_request_args(self, rental_meta: util.ListRequestMeta):
        # add order and orderType
        url = "{}&region={}&firstRow={}&order=posttime&orderType=desc".format(
            util.LIST_ENDPOINT,
            rental_meta.id,
            rental_meta.page * self.N_PAGE
        )
        
        return {
            **super().gen_list_request_args(rental_meta),
            'url': url
        }
