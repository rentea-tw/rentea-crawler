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
import socket
from datetime import datetime, timedelta
from scrapy import Request
from scrapy_twrh.spiders.enums import DealStatusType
from scrapy_twrh.spiders.rental591 import Rental591Spider, util
from scrapy_twrh.spiders.rental591.all_591_cities import all_591_cities
from scrapy_twrh.spiders.util import clean_number
from scrapy_twrh.items import GenericHouseItem

DEFAULT_MINUTEAGO = 60

class Periodic591Spider(Rental591Spider):
    name = 'periodic591'

    def __init__(self, minuteago, **kwargs):
        try:
            minuteago = int(minuteago)
        except ValueError:
            minuteago = DEFAULT_MINUTEAGO

        if 'target_cities' in kwargs and isinstance(kwargs['target_cities'], str):
            kwargs['target_cities'] = kwargs['target_cities'].split(',')

        super().__init__(
            **kwargs,
            start_list=self.periodic_start_list,
            parse_list=self.periodic_parse_list
        )

        time_ago = datetime.now() - timedelta(minutes=minuteago)
        self.minute_ago = minuteago
        self.epoch_ago = time_ago.timestamp()
        self.count_per_city = {}

        for city in all_591_cities:
            self.count_per_city[city['city']] = 0

    def periodic_start_list(self):
        for item in super().default_start_list():
            yield item

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
                # send non-gps request first at it may be closed soon
                request = self.gen_detail_request(util.DetailRequestMeta(
                    house_item['vendor_house_id'],
                    False
                ))
                yield request
                if meta.name in self.count_per_city:
                    self.count_per_city[meta.name] += 1

        if data['data']['data'] and not has_outdated:
            # only goto next page when there's response and not outdated
            request = self.gen_list_request(util.ListRequestMeta(
                meta.id,
                meta.name,
                meta.page + 1
            ))

            yield request
        else:
            logging.info(f'[{meta.name}] total {self.count_per_city[meta.name]} house to crawl!')

    def parse_main_response(self, response):
        for item in super().parse_main_response(response):
            if not isinstance(item, GenericHouseItem):
                # Skip original logic about GPS request generation
                continue
            if item['deal_status'] == DealStatusType.NOT_FOUND:
                yield item
            else:
                # Got an item that contains GPS!
                gps_arg = {
                    'callback': self.parse_detail,
                    **self.gen_detail_request_args(util.DetailRequestMeta(
                        item['vendor_house_id'],
                        True
                    ))
                }

                gps_arg['meta']['main_item'] = item

                yield Request(**gps_arg)

    def parse_gps_response(self, response):
        for item in super().parse_gps_response(response):
            # combine info from main and gps pages
            item = GenericHouseItem(
                **response.meta['main_item'],
                rough_coordinate=item['rough_coordinate']
            )
            yield item

    def gen_list_request_args(self, rental_meta: util.ListRequestMeta):
        """add order and orderType, so to get latest created house"""
        url = "{}&region={}&firstRow={}&order=posttime&orderType=desc".format(
            util.LIST_ENDPOINT,
            rental_meta.id,
            rental_meta.page * self.N_PAGE
        )
        
        return {
            **super().gen_list_request_args(rental_meta),
            'url': url
        }
