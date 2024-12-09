# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import requests
import json
from bs4 import BeautifulSoup

import time
import datetime

import cachetools
from cachetools import cached, TTLCache
import func_timeout
from func_timeout import func_set_timeout
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import re

from .request_food_caleries import api_generate_food_calories_result_wrapper
from .request_constants import *

class BaseAPI(object):
    """docstring for ClassName"""
    def __init__(self, configs):
        self.configs = configs
        
    def api(self, kwargs):
        """
            Args:
                kwargs: dict, 
            Return:
                res_dict: dict
        """
        # input
        query = kwargs["query"]
        # output
        res_dict={}
        return res_dict

class FoodCaloriesUsdaAPI(BaseAPI):
    """
        Args:
            kwargs key value params

            symbol_list: list of str, e.g. ["TSLA", "MSFT", "GOOG"]
            market: str, e.g. US
            sub_market: str, NYSE, NASDAQ, etc.
            data_source_list: list of websites for data sources, e.g. hkex.com, zacks.com, morningstar.com
            token: API calling token
        Output:
            res_dict
                item_list
                item_dict
    """
    def __init__(self, configs):
        super(FoodCaloriesUsdaAPI, self).__init__(configs)
        self.name = API_NAME_FOOD_CALORIES_USDA

    def api(self, kwargs):
        result_dict = {}
        try:
            result_dict = api_generate_food_calories_result_wrapper(kwargs)
        except Exception as e:
            print (e)
        return result_dict
