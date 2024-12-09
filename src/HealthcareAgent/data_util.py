#coding=utf-8
#!/usr/bin/python

import requests
import datetime
import time
import re
import codecs

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

def replace_re():
    """
    """
    pattern = re.compile("|".join(words))
    print(pattern)
    r = re.sub(pattern, "", s)
    print(r)

    pattern = re.compile(",")
    query = " A,B and C,D"
    query_new = re.sub(pattern, " , ", query)
    print(query_new)


def replace_all_sub(query, sub, sub_new):
    """
    """
    pattern = re.compile(sub)
    query_new = re.sub(pattern, sub_new, query)
    return query_new

def normalize_input_query(query):
    """
        1. lower case query
        2. replace special marks
    """
    query_norm = lower_case(query)
    query_norm = replace_all_sub(query_norm, ",", " , ")
    query_norm = replace_all_sub(query_norm, "\\?", " ? ")
    query_norm = replace_all_sub(query_norm, "\\|", " | ")
    query_norm = replace_all_sub(query_norm, ":", " : ")
    query_norm = replace_all_sub(query_norm, "-", " - ")
    return query_norm

def format_number_str(float_str):
    float_clean_str = float_str.replace(",", "")    
    float_clean_str = float_clean_str.replace("−", "-")
    return float_clean_str

def number_to_float(float_str):
    """
    """
    float_value = 0.0
    try:
        float_clean = float_str.replace(",", "")    
        float_clean = float_clean.replace("−", "-")

        float_value = 0.0
        if "%" in float_str:
            float_clean = float_clean.replace("%", "")
            float_value = float(float_clean)/100.0
        elif "," in float_str:
            float_value = float(float_clean)
        else:
            float_value = float(float_clean)
        return float_value
    except Exception as e:
        print (e)
        return float_value

def convert_loc_time(update_time):
    """
    """
    return update_time

def lower_case(query):
    query_lower = query.lower()
    return query_lower

def first_letter_upper_case(query):
    query_normalize = " ".join([first_letter_upper_case_word(word) for word in query.split(" ")])
    return query_normalize

def first_letter_upper_case_word(word):
    w_list =[w.upper() if i == 0 else w.lower() for i, w in enumerate(word)]
    return "".join(w_list)

def pass_check_input_length(query, min_length, max_length):
    if len(query) <= min_length or len(query) >= max_length:
        return False
    else:
        return True

def check_contain_chinese(string):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    match = pattern.search(string)
    return match is not None


def check_contain_alphabet(string):
    pattern_upper = re.compile(r'[\u0041-\u005a]')
    match_upper_case = pattern_upper.search(string)

    pattern_lower = re.compile(r'[\u0061-\u007a]')
    match_lower_case = pattern_lower.search(string)

    if match_lower_case is not None or match_upper_case is not None:
        return True 
    else:
        return False

def split_alphabet_and_zh_words(string):
    """
    """
    en_words = split_alphabet_and_zh_words_detail(string, 0)

    zh_words_str = string
    for en_word in en_words:
        zh_words_str = zh_words_str.replace(en_word, "")
    zh_words_list= [ch for ch in zh_words_str]
    return en_words, zh_words_list

def split_alphabet_and_zh_words_detail(string, start):
    """
    """
    pattern_en = re.compile(r'[a-zA-Z0-9]+')
    if start < len(string):
        match_en = pattern_en.search(string, start)
        if match_en is None:
            return []
        else:
            matched_word_list = []
            match_word = match_en.group()
            start = match_en.start()
            end = match_en.end()

            start_new = end
            matched_word_list.extend([match_word])
            matched_word_list.extend(split_alphabet_and_zh_words_detail(string, start_new))
            return matched_word_list
    else:
        return []   

def parse_digit_from_query(string, start):
    """
        float: - xx.xx
        float: -1,2312,323.039
    """
    pattern = re.compile(r'[-]*[0-9]+[,\d{3}]*[.]*[0-9]*')
    if start < len(string):
        match = pattern.search(string, start)
        if match is None:
            return []
        else:
            matched_word_list = []
            match_word = match.group()
            start = match.start()
            end = match.end()
            start_new = end
            ## 保存前把科学技术法的,去掉
            match_word = match_word.replace(",", "")
            matched_word_list.extend([match_word])
            matched_word_list.extend(parse_digit_from_query(string, start_new))
            return matched_word_list
    else:
        return []   

def normalize_query_clean_digit(string):
    """
    """
    string_clean = string.replace(",", "")
    return string_clean

def is_chinese(uchar):
    """"""
    if uchar >= u'u4e00' and uchar<=u'u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    """"""
    if uchar >= u'u0030' and uchar<=u'u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """"""
    if (uchar >= u'u0041' and uchar<=u'u005a') or (uchar >= u'u0061' and uchar<=u'u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def datetime_2_unixtimestamp(timestamp):
    """
        Input:
            timestamp = "2023-08-20 14:20:05"
        Return:
            unixtime_sec_int: in seconds
    """
    unixtime_sec_int = 0
    try:
        dtime = datetime.datetime.strptime(timestamp, '%Y-%m-%d  %H:%M:%S')
        unixtime_sec_int = int(time.mktime(dtime.timetuple()))
    except Exception as e:
        unixtime_sec_int = 0
        print (e)
    return unixtime_sec_int

def uniform(ustring):
    """"""
    return stringQ2B(ustring).lower()

def merge_dict(dict_a, dict_b):
    """
    """
    dict_merge = {}
    # keyset_merge = set(dict_a.keys() + dict_b.keys())
    keyset_merge = dict_a.keys() | dict_b.keys()
    for key in keyset_merge:
        list_a = dict_a[key] if key in dict_a else []
        list_b = dict_b[key] if key in dict_b else []
        list_merge = list(set(list_a + list_b))
        dict_merge[key] = list_merge
    return dict_merge 

def merge_dict_list(list_dict):
    """
        list of dict
        dict key: , value: items
    """
    dict_merge = {}
    keylist = []
    for dict_item in list_dict:
        keylist.extend(dict_item.keys())
    keyset_merge = set(keylist)

    # keyset_merge = set(dict_a.keys() + dict_b.keys())
    dict_merge = {}
    for key in keyset_merge:
        cur_list = []
        for dict_item in list_dict:
            if key in dict_item:
                items = dict_item[key]
                cur_list.extend(items)
            else:
                continue
        cur_list_unique =list(set(cur_list))
        dict_merge[key] = cur_list_unique
    return dict_merge 

class Node(object):
    def __init__(self, value):
        self._children = {}
        self._value = value
        self._terminal = False

    def _add_child(self, char, value, overwrite=False, if_terminal=False):
        child = self._children.get(char)
        if child is None:
            child = Node(value)
            if if_terminal:
                child._terminal = True
            self._children[char] = child

        if if_terminal:
            child._terminal = True
        if overwrite:
            child._value = value
        return child

def contain_ignore_case(str_a, str_b):
    """
    """
    if (str_a.lower() in str_b.lower()) or (str_b.lower() in str_a.lower()):
        return True
    else:
        return False


def get_jaccard_similarity_modified(set_a, set_b):
    """
    """
    if len(set_a) == 0 or len(set_b) == 0:
        return 0.0
    intersect = set_a.intersection(set_b)
    union = set_a.union(set_b)
    if len(set_a) == len(intersect) or len(set_b) == len(intersect):
        return 1.0
    else:
        return len(intersect)/max(len(union), 1.0)

def item_list_contain_key(item_list, key):
    """ 
    """
    match = False 
    for item in item_list:
        ## 包含关系
        if normalize_input_query(key) in normalize_input_query(item):
            match=True
    return match

def check_language(query):
    """
    """
    if check_contain_chinese(query):
        return LANG_ZH
    else:
        return LANG_EN

class Trie(Node):
    """ 
    """

    def __init__(self):
        super(Trie, self).__init__(None)

    def __contains__(self, key):
        return self[key] is not None

    def __getitem__(self, key):
        state = self
        for char in key:
            state = state._children.get(char)
            if state is None:
                return None
        return state._value

    def is_full_match(self, key):
        """
        """
        full_value_list = self.get_prefix_full_value(key)
        if full_value_list is None:
            return False
        if key in full_value_list:
            return True
        else:
            return False

    def get_prefix_full_value(self, key):
        full_value_list = []
        state = self
        for char in key:
            state = state._children.get(char)
            if state is None:
                break
        # print ("DEBUG: get_prefix_full_value state is:" + str(state))
        if state is None:
            return None
        else:
            if state._terminal:
                full_value_list.append(state._value)
            full_value_list.extend(self.traverse_childen(node=state))
            #print ("DEBUG: get_prefix_full_value state cur Node childern is:" + str(full_value_list))
        full_value_list_unique = list(set(full_value_list))
        full_value_list_sorted = sorted(full_value_list_unique, key=lambda x:len(x))
        return full_value_list_sorted

    def traverse_childen_all(self, node):
        """ 
        """
        state = node
        print ("DEBUG: traverse_childen cur State value|%s|terminal|%s" % (state._value, state._terminal))
        for (key, child) in state._children.items():
            if child is not None:
                ## child is not None and child is terminal child
                print ("DEBUG: traverse_childen child value|%s|terminal|%s" % (child._value, child._terminal))
                self.traverse_childen_all(node = child)

    def traverse_childen(self, node):
        """ 
        """
        full_value_list = []
        state = node
        if state._terminal and len(state._children) > 0:
            full_value_list.extend([state._value])
        for (key, child) in state._children.items():
            ## child is not None and child is terminal child
            if child is not None:
                # print ("DEBUG: traverse_childen child value|%s|terminal|%s" % (child._value, child._terminal))
                if child._terminal:
                    full_value_list.extend([child._value])
                full_value_list.extend(self.traverse_childen(node=child))
            else:
                print ("DEBUG: traverse_childen child is None child|%s" % str(child))
        return full_value_list

    def __setitem__(self, key):
        state = self
        for i, char in enumerate(key):
            if i < len(key) - 1:
                partial_key = key[0:i+1]
                state = state._add_child(char, partial_key, False, if_terminal = False)
            else:
                state = state._add_child(char, key, True, if_terminal = True)

def get_local_time_str():
    """
    """
    cur_time_local =time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    return cur_time_local


def test_trie_node():
    input_query_list = ["GOOG", "GOOGLE", "APPLE", "TESLA", "BOEING"]
    trie_tree = Trie()
    for query in input_query_list:
        trie_tree.__setitem__(query)
    ## 
    print ("DEBUG: Traverse G")    
    print (trie_tree["G"])
    print ("DEBUG: Traverse G")
    print (trie_tree.get_prefix_full_value("GOOG"))
    print ("DEBUG: Traverse A")
    print (trie_tree.get_prefix_full_value("A"))
    print ("DEBUG: Traverse TESLA")
    print (trie_tree.get_prefix_full_value("TES"))

def main():

    query = "TESLA and GOOGLE stock price"

    # Construct Trie Prefix
    input_stock_name_list = ["GOOG", "GOOGLE", "APPLE", "TESLA", "BOEING"]
    trie_tree = Trie()
    for name in input_stock_name_list:
        trie_tree.__setitem__(name)

    words = query.split(" ")
    parse_stock_name_list = []
    for word in words:
        if trie_tree.is_full_match(word):
            parse_stock_name_list.append(word)

    print ("DEBUG: Input Query|%s" % query)
    print ("DEBUG: Final Parsed Stock Quotes from Query|%s" % (str(parse_stock_name_list)))

if __name__ == '__main__':
    main()
