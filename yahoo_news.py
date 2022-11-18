import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer

# ヤフーニュースのトップページ情報を取得する
URL = "https://www.yahoo.co.jp/"
rest = requests.get(URL)

# BeautifulSoupにヤフーニュースのページ内容を読み込ませる
soup = BeautifulSoup(rest.text, "html.parser")

# ヤフーニュースの見出しとURLの情報を取得して出力する
news_title = []
syntax_analysis = []
syntax_analysis_str = []

data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup"))
for data in data_list:
    news_title.append(data.text)
    print(data.text)

    # #構文解析
    t = Tokenizer()
    s = data.text
    syntax_analysis.append([token.base_form for token in t.tokenize(s)])
    syntax_analysis_str.append([token.part_of_speech.split(',')[0] for token in t.tokenize(s)])

    time.sleep(0.5)


df = pd.DataFrame(zip(news_title, syntax_analysis, syntax_analysis_str))

df.to_csv('yahoo_news.csv', encoding='utf_8_sig', index=False)

