import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


data = []

def scraping(target_url, count):
  r = requests.get(target_url)
  c = r.content

  soup = BeautifulSoup(c, "html.parser")
  pages = soup.find_all("a")
  for page in pages:
    if page.text == "次へ":
      next_url_local = page.get("href")

  spots = soup.find_all('div',attrs={'class':'item-info'})
  for spot in spots:
    spot_name = spot.find('p',attrs={'class':'item-name'})
    try:
      spot_name.find('span').extract()
    except:
      print(spot_name)
    spot_name = spot_name.text.replace('\n','')
    spot_detail_url_all = spot.find_all('a')
    for url in spot_detail_url_all:
      if url.getText() == spot_name:
        count += 1
        detail_url = "https:" + url.get("href")
        r = requests.get(detail_url)
        c = r.content

        soup = BeautifulSoup(c, "html.parser")
        detail_info = soup.find('div',attrs={'class':'container'}) #情報の読み取り

        spot_name = detail_info.find('h1',attrs={'class':'detailTitle'}) #観光名称
        spot_name = spot_name.text.replace('\n','')

        eval_num = detail_info.find('span',attrs={'class':'reviewPoint'}).text #
        eval_num = eval_num.replace('\n','')

        basic_info = detail_info.find_all('td') #基本情報を配列で受け取った
        basic_info_item = detail_info.find_all('th') #基本情報を配列で受け取った

        for info_item, info in zip(basic_info_item, basic_info):
          # print(info.text.replace('\n',''))
          txt = info_item.text.replace('\n','')
          # print(info_item, " : ", info)
          if txt == "名称":
            spot_name = info.text.replace('\n','')
            spot_name = spot_name.replace('\t', '')
          if txt == "所在地" and info.find('a') != None:
            info.find('a').extract()
            spot_place = info.text.replace('\n', '')
            spot_place = spot_place.replace('\t', '')
          if txt == "料金":
            fee = info.text.replace('\n','')
            fee = fee.replace('\t', '')
          if txt == "交通アクセス":
            route = info.text.replace('\n','')
            route = route.replace('\t', '')
          if txt == "営業期間":
            open_time = info.text.replace('\n','')
            open_time = open_time.replace('\t', '')

        # print("name: ", spot_name)
        # print("place: ", spot_place)
        # print("star: ", eval_num)
        # print("open: ",open_time)
        # print("route", route)
        # print("fee: ", fee)

        datum = {}
        datum['観光地名'] = spot_name
        datum['評点'] = eval_num
        datum['所在地'] = spot_place
        try:
          datum['営業期間'] = open_time
        except:
          datum['営業期間'] = None
        try:
          datum['アクセス'] = route
        except:
          datum['アクセス'] = None
        try:
          datum['料金'] = fee
        except:
          datum['料金'] = None

        data.append(datum)
        print(count, spot_name, "complete")
        time.sleep(0.5)

  return next_url_local, count


# next_url = f"https://www.jalan.net/kankou/kw_%2588%25A4%2595Q/?rootCd=7741&exLrgGenreCd=01"
next_url = "https://www.jalan.net/kankou/pro_008/"
count = 0
for i in range(5):
  execution = scraping(next_url, count)
  next_url = execution[0]
  count = execution[1]


df = pd.DataFrame(data)

df.to_csv('test3.csv', encoding='utf_8_sig', index=False)






  # l=[]
  # for item in all:
  #     d={}
  #     d["クチコミ"]=item.text
  #     l.append(d)

  # import pandas
  # df=pandas.DataFrame(l)
  # df.to_csv("じゃらん.csv", encoding='utf_8_sig')
  # df

