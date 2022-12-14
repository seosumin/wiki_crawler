import requests
import random
from bs4 import BeautifulSoup
import re
import pandas as pd
from requests.adapters import HTTPAdapter
import csv
from multiprocessing import Pool, Manager, freeze_support
import time
import datetime

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



def crawl_wiki_by_section(row):
    S = requests.Session()
    Max_retries = 30
    base_url = 'https://en.wikipedia.org'

    URL = "https://en.wikipedia.org/w/api.php"

    content_dict = {}
    #No = row[0]
    Title = row
    #node_cnt = row[4]

    print('단어 수집 중....: {}'.format(Title))

    # api 받아오기 ============================
    PARAMS = {
        "action": "parse",
        "format": "json",
        'prop': 'sections',
        'page': Title}

    user_agent = random.choice(user_agent_list)
    S.mount("https://", HTTPAdapter(max_retries=Max_retries))
    R = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent}, verify=False)
    DATA = R.json()

    try:
        sections = DATA['parse']['sections']
    except Exception as ex:
        print('에러 발생', Title, ex)
    # for sec in sections:
    #     print(sec)

    sections = [sec['anchor'] for sec in sections if sec['toclevel'] == 1]
    # sections = [sec['line'] for sec in sections]
    # 섹션이 없을 때 바로 본문 수집
    if not sections:

        PARAMS = {
            "action": "query",
            "format": "json",
            'prop': 'extracts',
            # 'exintro': True,
            # 'explaintext': True,
            # 'exsectionformat': 'raw',
            'titles': Title}

        user_agent = random.choice(user_agent_list)
        R = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent}, verify=False)
        DATA = R.json()

        content = list(DATA['query']['pages'].values())[0]
        content = content['extract']
        content_soup = BeautifulSoup(content, 'lxml')

        # 시올소 위까지 자르기
        try:
            cut_tag = content_soup.select_one('span[id="See_also"]')
            if not cut_tag:
                cut_tag = content_soup.select_one('span[id="References"]')
            if not cut_tag:
                cut_tag = content_soup.select_one('span[id="External_links"]')
            if not cut_tag:
                cut_tag = content_soup.select_one('span[id="Further_reading"]')
            cut_tag = str(cut_tag.parent)
            content = content[:content.find(cut_tag)]
        except:
            pass

        summary_soup = BeautifulSoup(content, 'lxml')
        try:
            math_elements = summary_soup.select('math')
            for math in math_elements:
                math.decompose()  # 트리에서 완전히 삭제, extract는 따로 빼놓는 것
        except:
            pass
        summary_content = summary_soup.get_text()
        summary_content = summary_content.strip()

        sec_content_dict = {}
        sec_content_dict['Article_Summary'] = sec_content_dict.get('Article_Summary', summary_content)

        content_dict[Title] = content_dict.get(Title, sec_content_dict)
        print(Title, 'Article_Summary')
        return content_dict

    # 섹션이 있을 때
    else:
        sections.insert(0, 'Article_Summary')

        execpt_sec_list = ['See_also', 'References', 'External_links', 'Further_reading']
        ex_idx = []
        for ex_sec in execpt_sec_list:
            try:
                ex_idx.append(sections.index(ex_sec))
            except:
                pass

        if len(ex_idx) != 0:
            ex_idx = min(ex_idx)
            sections = sections[:ex_idx]

        PARAMS = {
            "action": "query",
            "format": "json",
            'prop': 'extracts',
            # 'exintro': True,
            # 'explaintext': True,
            # 'exsectionformat': 'raw',
            'titles': Title}

        user_agent = random.choice(user_agent_list)
        R = S.get(url=URL, params=PARAMS, headers={'User-Agent': user_agent}, verify=False)
        DATA = R.json()

        content = list(DATA['query']['pages'].values())[0]
        content = content['extract']

        content_soup = BeautifulSoup(content, 'lxml')

        # 시올소 위까지 자르기
        # try:
        #     cut_tag = content_soup.select_one('span[id="See_also"]')
        #     if not cut_tag:
        #         cut_tag = content_soup.select_one('span[id="References"]')
        #     if not cut_tag:
        #         cut_tag = content_soup.select_one('span[id="External_links"]')
        #     if not cut_tag:
        #         cut_tag = content_soup.select_one('span[id="Further_reading"]')
        #     cut_tag = str(cut_tag.parent)
        #     content = str(content_soup)
        #     content = content[:content.find(cut_tag)]
        # except:
        #     pass

        survive_sections = []
        for sec in sections:
            if sec == 'Article_Summary':
                survive_sections.append('Article_Summary')
                continue
            try:
                chk_sec = content_soup.find('span', id=sec)
                chk_sec.parent
                survive_sections.append(sec)
            except:
                print('섹션 없음', Title, sec)
                continue
        print(Title, survive_sections)
        sec_content_dict = {}
        for i, sec in enumerate(survive_sections):
            if i != len(survive_sections) - 1:  # 마지막 섹션이 아닐 때
                # 시올소나 레퍼런스 제거한 본문(없으면 처음 그대로)
                content_soup = BeautifulSoup(content, 'lxml')
                cut_tag_name = survive_sections[i + 1]
                # cut_tag = content_soup.select_one("span[id='" + cut_tag_name + "']")
                cut_tag = content_soup.find('span', id=cut_tag_name)
                # cut_tag = str(cut_tag.parent)
                try:
                    cut_tag = str(cut_tag.parent)
                except Exception as ex:
                    print('에러 발생', ex)
                    print(cut_tag_name)

                content_soup = str(content_soup)
                sec_content = content_soup[:content_soup.find(cut_tag)]
                sec_content_soup = BeautifulSoup(sec_content, 'lxml')

                # 시올소 위까지 자르기
                try:
                    sa_cut_tag = sec_content_soup.find('span', text='See also')
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="References")
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="External links")
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="Further reading")
                    sa_cut_tag = str(sa_cut_tag.parent)
                    sec_content = str(sec_content_soup)
                    sec_content = sec_content[:sec_content.find(sa_cut_tag)]
                except:
                    pass

                content = content_soup[content_soup.find(cut_tag):]
                content = content.replace(cut_tag, '')

                sec_content_soup = BeautifulSoup(sec_content, 'lxml')

                try:
                    math_elements = sec_content_soup.select('math')
                    for math in math_elements:
                        math.decompose()  # 트리에서 완전히 삭제, extract는 따로 빼놓는 것
                except:
                    pass
                # print(sec_content_soup)
                sec_content = sec_content_soup.get_text()
                sec_content = sec_content.strip()
                if not sec_content:
                    continue
                else:
                    sec_content_dict[sec] = sec_content_dict.get(sec, sec_content)

            else:  # 마지막 섹션일 때
                # print(sec)
                sec_content_soup = BeautifulSoup(content, 'lxml')
                # print(sec_content_soup)

                # 시올소 위까지 자르기
                try:
                    sa_cut_tag = sec_content_soup.find('span', text='See also')
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="References")
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="External links")
                    if not sa_cut_tag:
                        sa_cut_tag = sec_content_soup.find('span', text="Further reading")
                    sa_cut_tag = str(sa_cut_tag.parent)
                    content = str(sec_content_soup)
                    content = content[:content.find(sa_cut_tag)]
                except:
                    pass

                sec_content_soup = BeautifulSoup(content, 'lxml')

                try:
                    math_elements = sec_content_soup.select('math')
                    for math in math_elements:
                        math.decompose()  # 트리에서 완전히 삭제, extract는 따로 빼놓는 것
                except:
                    pass

                sec_content = sec_content_soup.get_text()
                sec_content = sec_content.strip()
                if not sec_content:
                    continue
                else:
                    sec_content_dict[sec] = sec_content_dict.get(sec, sec_content)

        content_dict[Title] = content_dict.get(Title, sec_content_dict)
        return content_dict
