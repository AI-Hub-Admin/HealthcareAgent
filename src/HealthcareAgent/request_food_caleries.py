#coding=utf-8
#!/usr/bin/python

import requests
import sys
import os
import re
import bs4
from bs4 import BeautifulSoup
import json
import time
import codecs
import cachetools
from cachetools import cached, TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed

from .data_util import Trie

PATTERN_REPLACE_TOKEN = "$$"

def read_data(data_file):
    file = codecs.open(data_file, "r", "utf-8")
    l = []
    for line in file:
        line = line.replace("\n", "")
        l.append(line)
    return l

def save_data(data_file, l):
    file = codecs.open(data_file, "w", "utf-8")
    for line in l:
        file.write(line + "\n")
    file.close()

def fetch_food_brand_usda_by_sug(brand_owner, if_return_list=False):
    """
        ["STARBUCKS","STARBUCKS VIA INSTANT","STARBUCKS, INC","Starbucks Coffee Company"]
    """
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8;",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }
    url = "https://fdc.nal.usda.gov/portal-data/external/suggestBrandOwners"
    data = '{"includeDataTypes":{"Branded":true},"referenceFoodsCheckBox":true,"requireAllWords":true,"sortField":"brandName.keyword","sortDirection":"asc","pageNumber":1,"exactBrandOwner":null,"currentPage":1,"brandOwner":"%s"}' % brand_owner
    
    res = requests.post(url, headers=headers, data=data)
    result_brand = ""
    result_brand_list = []
    if res.status_code == 200:
        result_brand_list = res.json()
        result_brand = result_brand_list[0] if len(result_brand_list) > 0 else ""
    else:
        result_brand_list = []
        result_brand = ""

    if if_return_list:
        return result_brand_list
    else:
        return result_brand

def fetch_food_usda_by_brand(brand_name):
    """
        Args: 
            brand_name in usda.gov United States Department of Agriculture
            e.g. brand_name = "STARBUCKS"

        Return:
            result_json_list: 
                list of items
            result_json_dict:
                K1: Item
                V1: list of json
    """
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8;",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }

    page_max = 100
    house = 'https://fdc.nal.usda.gov/portal-data/external/search'
    data = '{"includeDataTypes":{"Branded":true},"referenceFoodsCheckBox":true,"requireAllWords":true,"sortField":"","sortDirection":null,"pageNumber":1,"exactBrandOwner":"%s","currentPage":1,"brandOwner":"%s","exactFoodCategory":null}' % (brand_name, brand_name)

    res = requests.post(house, headers=headers, data=data)
    soup = BeautifulSoup(res.text, 'html.parser')
    result_json = json.loads(soup.text)
    aggregations = result_json['aggregations'] if 'aggregations' in result_json else []
    foods = result_json['foods'] if 'foods' in result_json else []

    result_json_list = []
    result_json_dict = {} 
    # K1: name, V1: list
    for item in foods:
        description = item["description"] if "description" in item else ""
        brand_owner = item["brandOwner"] if "brandOwner" in item else ""
        food_nutrients_list = item["foodNutrients"] if "foodNutrients" in item else []
        item_result_json = {}
        for sub_item in food_nutrients_list:
            nutrient_id = sub_item["nutrientId"] if "nutrientId" in sub_item else "" 
            nutrientName = sub_item["nutrientName"] if "nutrientName" in sub_item else ""   # Energy
            unit_name = sub_item["unitName"] if "unitName" in sub_item else ""   # KCAL
            value = sub_item["value"] if "value" in sub_item else ""   # KCAL
            value_full = str(value) +  "" + unit_name  ## 100KCAL
            item_result_json[nutrientName] = value_full

        result_json_list.append(item_result_json)

        if description in result_json:
            # v1: list of json            
            result_list = result_json[description]
            result_list.append(item_result_json)
            result_json_dict[description] = result_list
        else:
            # v1: list of json
            result_json_dict[description] = [item_result_json]
    return result_json_list, result_json_dict

def parse_brandname_list_from_prefix(query, brandname_trie):
    """
    """
    query_clean = get_clean_lower_case_query(query)
    if query_clean == "":
        return ""
    brandname_list = brandname_trie.get_prefix_full_value(query_clean)
    print ("DEBUG: parse_brandname_list_from_prefix brandname_list %s" % str(brandname_list))
    top_brandname = None
    if brandname_list is not None and len(brandname_list) > 0:
        if query in set(brandname_list):
            top_brandname = query
        else:
            top_brandname = brandname_list[0]
    return top_brandname

def api_generate_food_calories_result(query, topk, brandname_trie = None):
    """ fetch food calories by query
        Args:
            query: str
            topk: int
            brandname_trie: use trie to fetch brand name or calling API

            Note: brand_name is case sensitive for input, check website for details: https://fdc.nal.usda.gov/food-search?type=Branded&query=
        Output:
            result_json_list: list of dict of food and calories
            result_json_dict: dict with key: item name, value: attributes of nutritions calories
            result_response_list: pretty print info
    """
    print ("DEBUG: Input query %s and brandname_trie is %s" % (query, brandname_trie))
    priority = 2
    try:
        brand_prefix = query
        if get_clean_lower_case_query(brand_prefix) == "":
            return [], priority
        brand_name = ""
        # get USDA standard brand name for query
        if brandname_trie is not None:
            brand_name = parse_brandname_list_from_prefix(brand_prefix, brandname_trie)
        else :
            brand_name = fetch_food_brand_usda_by_sug(query)
            # brand_name = query
        if brand_name is None or brand_name == "":
            brand_name = query
        print ("DEBUG: After processing brand_name is %s" % brand_name)
        # brand_name_upper = brand_name.upper()
        result_json_list, result_json_dict = fetch_food_usda_by_brand(brand_name)
        result_response_list = generate_topic(brand_name, result_json_dict, topk=topk, if_return_list=True)
        return result_json_list, result_json_dict, result_response_list
    except Exception as e:
        print (e)
        return "", priority

def api_generate_food_calories_result_wrapper(kwargs):
    """
        Args:
            kwargs: dict
                query: str
                topk: items
        Return:
            dict
                item_list: list of dict
                item_dict: dict
                item_list_pretty: list of str
    """
    result_dict = {}
    try:
        query = kwargs["query"] if "query" in kwargs else ""
        topk = kwargs["topk"] if "topk" in kwargs else ""        
        if query == "":
            print ("DEBUG: api_generate_food_calories_result_wrapper kwargs missing query, return empty dict...")
            return {}
        if topk == "" or not isinstance(topk, int):
            print ("DEBUG: api_generate_food_calories_result_wrapper kwargs input topk missing, setting to default %d" % topk)            
            topk = API_NAME_FOOD_CALORIES_TOP_K

        result_json_list, result_json_dict, result_response_pretty = api_generate_food_calories_result(query, topk)
        result_dict["item_list"] = result_json_list
        result_dict["item_dict"] = result_json_dict
        result_dict["item_list_pretty"]= result_response_pretty
        return result_dict
    except Exception as e:
        print (e)
        return result_dict

def init_health_dict():
    """
        ## USDA brand name is case sensitive
        return: brandname_trie, 
            brandname_trie["brand_name"]
    """
    health_brand_list = read_data("./health_brand_sug_dict.txt")
    ## convert to lower
    # health_brand_list_lower_case = [w.lower() for w in health_brand_list]

    ## Set Trie
    brandname_trie = Trie()    
    for w in health_brand_list:
        brandname_trie.__setitem__(w)
    return health_brand_list, brandname_trie

def get_ingredient_translation(result_json):
    item_key_list = []
    for result_key in result_json.keys():
        result = result_json[result_key]
        item_json = result[0] if len(result) >0 else {}
        for key in item_json:
            item_key_list.append(key)
    item_key_set = set(item_key_list)
    print ("DEBUG: item_key_list size %d item key set %d" % (len(item_key_list), len(item_key_set)))
    for key in item_key_set:
        print (key)

def generate_intel_word_image(word):
    return "$$%s(#image)$$" % word

def generate_topic(brand_name, result_json_dict, topk, if_return_list=False):
    """
        result_json: k1: food_name, k2: ingredient, V2: Cnt
    """
    # translation_dict = read_ingredient_translation()
    items = []
    PORTION = "Every 100g:"
    key_energy = "Energy"
    idx = 0
    for item_name in result_json_dict.keys():
        if idx >= topk:
            continue
        item_ingredient_json = result_json_dict[item_name][0]
        ingredient_list = []
        value_energy = item_ingredient_json[key_energy] if key_energy in item_ingredient_json else ""
        item_line = key_energy + str(value_energy)

        ingredient_list.append(item_line)
        for key in item_ingredient_json:
            if key != key_energy:
                unit = ""
                value = item_ingredient_json[key] if key in item_ingredient_json else ""
                item_line = key + str(value)  + unit + "\n"
                ingredient_list.append(item_line)
        idx += 1
        image_intel_word = generate_intel_word_image(brand_name + " " +item_name)
        item_total_line = str(idx) + ". " + item_name + "\n" + image_intel_word + "\n" + PORTION + "\n" + "".join(ingredient_list) + "\n"
        items.append(item_total_line)
    if if_return_list:
        return items
    else:
        return "".join(items)

def get_clean_lower_case_query(query):
    query_lower = query.lower()
    return query_lower.strip()

def normalize_query(query):
    token_list = query.split(" ")
    token_list_upper = [t.upper() for t in token_list]
    normalize_query = "+".join(token_list_upper)
    return normalize_query

def query_to_file_name(query):
    token_list = query.split(" ")
    token_list_lower = [t.lower() for t in token_list]
    normalize_query = "_".join(token_list_lower)
    return normalize_query

def extract_query_and_attributes(line):
    """
        output:
            query: str
            result_list:  ["#calories", "#stock_price"]
    """
    prefix_query_pattern = r".*(?=\()"
    query_list = re.findall(prefix_query_pattern, line)
    query = query_list[0] if len(query_list) > 0 else ""

    content_pattern = r'\((.*?)\)'
    content_attributes_list = re.findall(content_pattern, line)
    
    return query, content_attributes_list

def replace_all(line, str_replace, str_new):

    matched_position_index = []
    pos = -1
    while True:
        pos = line.find(str_replace, pos + 1)
        if pos == -1:
            break
        else:
            matched_position_index.append(pos)

    output_line_list = []
    start = -1
    end = -1
    for position in matched_position_index:
        start = end
        end = position
        start = max(start, 0)
        substr = line[start:end]
        substr_new = substr.replace(str_replace, str_new)
        output_line_list.append(substr_new)
    last_sub_str = line[end:]
    list_substr_new = last_sub_str.replace(str_replace, str_new)
    output_line_list.append(list_substr_new)
    output_line = "".join(output_line_list)
    return output_line

def fullfill_final_docs(input_docs, parsed_action, action_result_map):
    """
        input_docs: list[str]
        parsed_action: list[]
        action_result_map: key: action, value: generated_content
    """
    output_docs = []
    for line in input_docs:
        output_line = line
        for action in parsed_action:
            if action in output_line:
                action_wrapper = PATTERN_REPLACE_TOKEN + action + PATTERN_REPLACE_TOKEN
                action_result = action_result_map[action] if action in action_result_map else ""

                print ("DEBUG: fullfill_final_docs action %s, action_wrapper %s, action_result %s" % (action, action_wrapper, action_result))
                output_line =replace_all(output_line, action, action_result)
        output_docs.append(output_line)
    return output_docs

def generate_image_url_html(image_tuple):
    """
    """
    output_tag_list = []
    output_tag_list.append("<div class=download_image>")
    for (img_name, img_url) in image_tuple:
        img_tag = '<img src="%s" alt="%s" name="%s"/>' % (img_url, img_name, img_name)
        output_tag_list.append(img_tag)
    output_tag_list.append("</div>")
    output_tag_html = "".join(output_tag_list)
    return output_tag_html

def generate_sug_list():
    sug_result_json = {}
    # prefix_code_list = [chr(i) for i in range(65,91)]   # A-Z
    prefix_code_list = [chr(i) for i in range(97,123)]  # a-z
    prefix_list = []

    for code_1 in prefix_code_list:
        for code_2 in prefix_code_list:
            for code_3 in prefix_code_list:
                for code_4 in prefix_code_list:
                    prefix_list.append(code_1+code_2+code_3+code_4)

    for prefix in prefix_list:
        time.sleep(0.1)
        brand_name_list = fetch_food_brand_usda_by_sug(prefix, if_return_list=True)
        print ("DEBUG: Prefix %s Brand_name_list %s" % (prefix, str(brand_name_list)))
        sug_result_json[prefix] = brand_name_list
    print (sug_result_json)
    # print ("DEBUG: Processing query %sand return list %s" % (query, str(brand_name_list)))
    print ("DEBUG: sug_result_json %s" % str(sug_result_json))

    json_str = json.dumps(sug_result_json, ensure_ascii=False)
    print ("DEBUG: READ stock json_str size %d" % len(json_str))
    output_file = "./health_brand_sug.json"
    file = codecs.open(output_file, "w", "utf-8")
    file.write(json_str + "\n")
    file.close()

def init_health_dict():
    """
        @return: brandname_trie, 
            brandname_trie["brand_name"]
    """
    health_brand_list = read_data("./health_brand_sug_dict.txt")
    ## convert to lower
    health_brand_list_lower_case = [w.lower() for w in health_brand_list]

    ## Set Trie
    brandname_trie = Trie()    
    for w in health_brand_list_lower_case:
        brandname_trie.__setitem__(w)

    return health_brand_list_lower_case, brandname_trie

def test_fetch_food(brand_name):
    brand_name = "STARBUCKS"
    result_json =fetch_food_usda_by_brand(brand_name)
    print (result_json)

    brand_name = "Dunkin' Donuts Inc"
    result_json =fetch_food_usda_by_brand(brand_name)
    print (result_json)

    brand_name = "Peet's Coffee and Tea, Inc."
    result_json =fetch_food_usda_by_brand(brand_name)
    print (result_json)

    brand_prefix = "peet"
    brand_name = fetch_food_brand_usda_by_sug(brand_prefix)
    result_json =fetch_food_usda_by_brand(brand_name)
    print ("DEBUG: Generating brand_name:%s, for prefix:%s") % (brand_name, brand_prefix)
    print (result_json)

def test_replace_all_line():
    line = "output #starbucks #Haha #starbucks"
    str_replace = "#starbucks"
    str_new = "[final_document]"
    line_new = replace_all(line, str_replace, str_new)

def run_api_generate_food_calories_result():

    query = "starbucks"
    # health_brand_list, brandname_trie = init_health_dict()
    result_json, result_list, result_response = api_generate_food_calories_result(query, topk = 10)
    # print ("DEBUG: test_api_generate_food_calories_result final_topic_result %s|" % result_json)
    for result in result_list:
        print (result)

def run_api_generate_food_calories_prefix():

    query = "peet"
    health_brand_list, brandname_trie = init_health_dict()
    brand_name = fetch_food_brand_usda_by_sug(query)
    print ("DEBUG: brand_name is %s" % brand_name)

    # brand_name = "Peet's Coffee and Tea, Inc."
    result_json, result_list, result_response = api_generate_food_calories_result(query, topk = 10, brandname_trie=None)
    print ("DEBUG: test_api_generate_food_calories_result final_topic_result %s|%s|%s" % (str(result_json), str(result_list), str(result_response)))
    for result in result_list:
        print (result)

def main():
    
    # run_api_generate_food_calories_result()
    run_api_generate_food_calories_prefix()

if __name__ == '__main__':
    main()
