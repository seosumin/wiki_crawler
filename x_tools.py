from urllib.parse import quote_plus
import requests
import lxml.html
import pandas as pd
import random
import datetime
import time
from requests.adapters import HTTPAdapter
from multiprocessing import Pool, Manager, freeze_support
from bs4 import BeautifulSoup as bs
import sys

pd.set_option('expand_frame_repr', False)

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
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0']



# for idx, node in enumerate(node_list):
#     try:
#         new_url = base_url + node + sub_url
#         user_agent = random.choice(user_agent_list)
#         S = requests.Session()
#         Max_retries = 30
#         S.mount("https://", HTTPAdapter(max_retries=Max_retries))
#         tables = pd.read_html(S.get(url=new_url, headers={'User-Agent': user_agent}).text)
#         # print(tables)
#         print(len(tables))
#         print(idx, node)
#     except Exception as ex:
#         print('{} 에서 에러발생 : {}'.format(node, ex))


def wiki_info_crawl(row):
    #idx = row[0]
    node = row
    #all_node_cnt = row[2]
    print(' 단어 수집 중....: {} '.format(node))
    base_url = 'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/'
    sub_url = '/2001-01-01'

    new_url = base_url + node + sub_url
    user_agent = random.choice(user_agent_list)
    S = requests.Session()
    Max_retries = 30
    S.mount("https://", HTTPAdapter(max_retries=Max_retries))
    try:
        tables = pd.read_html(S.get(url=new_url, headers={'User-Agent': user_agent}, verify=False).text)

        # table가져오기
        tables[0] = tables[0].T
        tables[0].columns = tables[0].iloc[0]
        tables[0] = tables[0][1:2]
        tables[0] = tables[0][['ID', 'Wikidata ID', 'Page size', 'Total edits', 'Editors', 'Pageviews']]

        tables[1] = tables[1].T
        tables[1].columns = tables[1].iloc[0]
        tables[1] = tables[1][1:2]
        tables[1] = tables[1][
            ['Minor edits', 'IP edits', 'Bot edits', '(Semi-)automated edits', 'Reverted edits', 'First edit',
             'Latest edit', 'Max. text added', 'Max. text deleted']]

        tables[2] = tables[2].T
        tables[2].columns = tables[2].iloc[0]
        tables[2] = tables[2][1:2]
        tables[2] = tables[2][
            ['Average time between edits (days)', 'Average edits per user', 'Average edits per day',
             'Average edits per month', 'Average edits per year', 'Edits made by the top 10% of editors']]

        tables[3] = tables[3].T
        tables[3].columns = tables[3].iloc[0]
        tables[3] = tables[3][1:2]
        tables[3] = tables[3][['Links to this page', 'Redirects']]

        tables[4] = tables[4].T
        tables[4].columns = tables[4].iloc[0]
        tables[4] = tables[4][1:2]
        tables[4] = tables[4][['Characters', 'Words', 'Sections', 'References', 'Unique references']]

        # table 합
        result = pd.concat([tables[0], tables[1], tables[2], tables[3], tables[4]], axis=1)
        result.insert(loc=0, column='Title', value=node)
        # print(result)
        return result

    except Exception as ex:
        error_dir = './'
        error_file = 'error_log.txt'
        print('{} 에서 에러 발생 : {} '.format(node, ex))
        with open(error_dir + error_file, 'a', encoding='utf-8-sig') as f:
            f.write('{} || {}\n'.format(node, ex))
        return None
