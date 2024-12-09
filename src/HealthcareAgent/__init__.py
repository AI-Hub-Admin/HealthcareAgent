# -*- coding: utf-8 -*-
# @Time    : 2024/06/27
# @Author  : Derek

from .base import *
from .request_constants import *

SUPPORTED_APIS = {
}

SUPPORTED_APIS[FoodCaloriesUsdaAPI(None).name] = {KEY_IMPL: FoodCaloriesUsdaAPI}

def api(api_name, **kwargs):
    api_cls = BaseAPI(None)
    res_dict = {}
    try:
        if api_name in SUPPORTED_APIS:
            attrs = SUPPORTED_APIS[api_name]
            api_cls_name = attrs[KEY_IMPL] if KEY_IMPL in attrs else None
            if api_cls_name is not None:
                api_cls = api_cls_name(None)
                res_dict = api_cls.api(kwargs)
    except Exception as e:
        print (e)
    return res_dict
