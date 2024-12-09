# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import HealthcareAgent as ha

def run_fetch_health_food_calories():

    ## group 1:
    print ("DEBUG: ### Food Nutritions for Brand Starbucks")
    result_dict = ha.api(api_name="food_calories_usda", query="Starbucks", topk=10)
    item_list = result_dict["item_list"]
    item_dict = result_dict["item_dict"]
    item_list_pretty = result_dict["item_list_pretty"]
    print ("DEBUG: ## Return Item List")
    print (item_list)
    print ("DEBUG: ## Return Item Dict")    
    print (item_dict)
    print ("DEBUG: ## Return Item Print Pretty")        
    [print (line) for line in item_list_pretty]


    ## group 2:
    print ("DEBUG: ### Food Nutritions for Peet's Coffee")
    result_dict = ha.api(api_name="food_calories_usda", query="peet", topk=10)
    item_list = result_dict["item_list"]
    item_dict = result_dict["item_dict"]
    item_list_pretty = result_dict["item_list_pretty"]
    print ("DEBUG: ## Return Item List")
    print (item_list)
    print ("DEBUG: ## Return Item Dict")    
    print (item_dict)
    print ("DEBUG: ## Return Item Print Pretty")        
    [print (line) for line in item_list_pretty]


def main():
	run_fetch_health_food_calories()

if __name__ == '__main__':
    main()
