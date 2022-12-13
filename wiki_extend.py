from wiki_crawler import wiki_crawl
import pandas as pd

item_list=['Natural hydrogen']

n=3
df_seed_items=wiki_crawl.n_char_crawler(item_list, n)
print(df_seed_items)
print(len(df_seed_items))
#df_seed_items.to_csv("{} 차시 확장 최종_결과.csv".format(n))
#item_list, sa_list, err_list, wiki_df=wiki_crawl.wiki_rule_crawler(item_list)
#print(item_list)
#print(wiki_df)

'''
import re
test_str='*[[Anti-aging medicine]]*[[Artificial organ]]'
p=re.compile('\*\[\[.+\]\]')
result=p.findall(test_str)
print(result)
'''

'''
import re
test_str='[[Leather#Alternatives|Cultured leather]]'
def text_pre(text):
    text = text.replace('[[', '')
    text = text.replace(']]', '')
    if "|" in text:
        text = re.sub(".+\|", "", text)
    return text
print(text_pre(test_str))
'''




