import time

import requests
import random
from bs4 import BeautifulSoup
import re
import pandas as pd
from requests.adapters import HTTPAdapter
import warnings
warnings.filterwarnings(action='ignore')
import itertools
from tqdm.notebook import tqdm_notebook

user_agent_list = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
]

# ??? ????????????
wiki_rule=pd.read_excel("wiki_rule.xlsx")
cate_rule=list(wiki_rule[wiki_rule['col']=='category']['item'])
cate_rules=('|').join(cate_rule)
title_rule=list(wiki_rule[wiki_rule['col']=='title']['item'])
title_rules=('|').join(title_rule)
c_rule=re.compile(cate_rules)
t_rule=re.compile(title_rules)

def text_pre(text):
    text = text.replace('[[', '')
    text = text.replace(']]', '')
    text = text.replace('{{', '')
    text = text.replace('}}', '')
    if "|" in text:
        text = re.sub(".+\|", "", text)
    return text


def wiki_rule_crawler(seed_list):
    item_list = []
    sa_list = []
    err_list = []

    for seed in tqdm_notebook(seed_list):
        S = requests.Session()
        Max_retries = 30

        base_url = 'https://en.wikipedia.org'
        URL = "https://en.wikipedia.org/w/api.php"

        # api ???????????? ============================
        PARAMS = {
            "action": "parse",
            "format": "json",
            'prop': 'sections',
            'page': seed}

        user_agent = random.choice(user_agent_list)
        S.mount("https://", HTTPAdapter(max_retries=Max_retries))
        R = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent}, verify=False)
        DATA = R.json()
        time.sleep(0.5)
        #print(DATA)
        try:
            sections = DATA['parse']['sections']
            section_num = 0
            for section in sections:
                #print(section)
                if section['line'] == 'See also':
                    section_num = section['index']
                    break
            if section_num == 0:  # ????????? ?????? ??????
                print('{} ??? see also X'.format(seed))
                err_list.append(seed)
                continue
            else:  # ????????? ??????

                # ????????? ?????? ????????????=========================
                PARAMS = {
                    "action": "parse",
                    "format": "json",
                    'prop': 'wikitext|text',
                    'section': section_num,
                    'page': seed}

                user_agent = random.choice(user_agent_list)
                S.mount("https://", HTTPAdapter(max_retries=Max_retries))
                R = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent}, verify=False)
                DATA = R.json()
                time.sleep(0.5)
                #print(DATA)
                try:
                    see_also = DATA['parse']['wikitext']['*']  # wikitext : see also ?????? ????????????
                    see_also = see_also[see_also.find('*'):]
                    print(see_also)
                    print(type(see_also))
                    #p = re.compile('\[\[.+\]\]|\{\{.+\}\}')
                    p = re.compile('\[\[.+\]\]')
                    see_also = p.findall(see_also)
                    see_also = list(map(text_pre, see_also))
                    print(see_also)
                    #print(type(see_also))
                except Exception as ex:
                    print('parse ??? ??????')
                    continue

                #see_also = see_also.replace('[[', '"')
                #see_also = see_also.replace(']]', '"')
                #see_also = re.findall(r'"([^"]*)"', see_also)
                print(see_also)
                #print(type(see_also))
                #==============???????????? ????????? ???????????? ??????????????? ????????? ??? ????????? ??????

                tmp_see_also = []
                for sa in see_also:
                    if 'Category:' in sa:
                        continue
                    if 'div col end' in sa:
                        continue
                    if 'Div col end' in sa:
                        continue
                    #sa = re.split('??', sa)
                    #sa = [t.lstrip() for t in sa]
                    #sa = [t.rstrip() for t in sa]
                    #for s in sa:
                    #if t_rule.search(sa.lower()) is None:
                    #    tmp_see_also.append(sa)
                    tmp_see_also.append(sa)


                #see_also_list = list(set(list(itertools.chain(*tmp_see_also))))
                see_also_list=tmp_see_also

                see_also_html = DATA['parse']['text']['*']
                sa_a_soup = BeautifulSoup(see_also_html, "lxml")

                del_index_list=[]
                for see_also_title in see_also_list:
                    print(see_also_title)
                    try:
                        see_also_a = sa_a_soup.find('a', string=see_also_title)
                        if not see_also_a:
                            see_also_a = sa_a_soup.find('a', string=re.compile(see_also_title))
                        if not see_also_a:
                            see_also_a = sa_a_soup.find('a', title=re.compile(see_also_title))
                        if not see_also_a:
                            print('see also {} ??? a ?????? ?????? ??????'.format(see_also_title))
                            #del_index = see_also_list.index(see_also_title)
                            del_index_list.append(see_also_title)
                            continue
                    except Exception as ex:
                        print('????????? ?????? ??????')


                    see_also_url = base_url + see_also_a['href']  # ????????? ??????
                    print(see_also_url)
                    html = S.get(see_also_url, headers={'User-Agent': user_agent}).text
                    sa_title_url_soup = BeautifulSoup(html, "lxml")
                    sa_original_title = sa_title_url_soup.select_one(
                        'h1[id="firstHeading"]').get_text()  # ????????? ?????? ????????? ????????????

                    sa_original_title = str(sa_original_title)  # ?????? ?????? ?????????(????????? ???)
                    #print(sa_original_title)
                    PARAMS = {
                        "action": "query",
                        "format": "json",
                        'prop': 'categories|extracts',
                        'clshow': '!hidden',
                        'titles': sa_original_title}

                    user_agent = random.choice(user_agent_list)
                    R_c_t = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent})
                    DATA = R_c_t.json()
                    time.sleep(0.5)
                    ct_and_content = list(DATA['query']['pages'].values())[0]

                    cate_list = [k['title'].replace("Category:", "").lower() for k in ct_and_content['categories']]
                    for c in cate_list:
                        if c_rule.search(c) is not None:
                            print("{}??? ????????? ?????? ???????????????".format(see_also_title), c)
                            #del_index = see_also_list.index(see_also_title)
                            del_index_list.append(see_also_title)
                            #del see_also_list[del_index]
                            break

                print(del_index_list)
                see_also_list = [i for i in see_also_list if i not in del_index_list]

                for sa in see_also_list:
                    if len(sa) == 1:
                        continue

                    else:
                        item_list.append(seed)
                        sa_list.append(sa)
                print(see_also_list)
        except Exception as ex:
            print('{} ??? ??????'.format(seed), ex)
            err_list.append(seed)

    wiki_df = pd.DataFrame(columns=['from', 'to'])
    wiki_df['from'] = item_list
    wiki_df['to'] = sa_list

    return item_list, sa_list, err_list, wiki_df

def n_char_crawler(seed_list, n):
    df_seed_items = pd.DataFrame(columns=['from', 'to'])
    i = 1
    while True:
        n-=1
        print(n)
        item_list, seed_list, err_list, wiki_df = wiki_rule_crawler(seed_list)
        print("{}?????? ????????? ?????? ????????? seed_list??? {}".format(i, seed_list))
        wiki_df.to_csv("{}_char_crawling.csv".format(i))
        i+=1
        print(i)
        df_seed_items = pd.concat([df_seed_items, wiki_df])

        if n==0:
            break
    return df_seed_items

