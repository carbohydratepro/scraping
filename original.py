from __future__ import annotations
from contextlib import contextmanager
import csv
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
import re
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException


# ===== 検索ターゲットを指定 =====
TARGET_PREF = "青森県"  # 都道府県
TARGET_CITY = "八戸市"  # 市区町村
# TARGET_PREF = "神奈川県"  # 都道府県
# TARGET_CITY = "横浜市"  # 市区町村


# ===== 店舗データの入れ物作成 =====
column_name = lambda name: field(metadata={"name": name})


@dataclass
class ShopProps:
    name: str = column_name("店舗名")
    address: str = column_name("住所")
    tel: str = column_name("電話番号")
    business_hours: str = column_name("営業時間")
    holiday: str = column_name("定休日")
    # 追加項目の定義を追加


shops: list[ShopProps] = []


# ===== WebDriverの準備 =====
@contextmanager
def webdriver():
    # Chromeを起動
    options = Options()
    options.binary_location = "/home/intern_share/chrome-linux/chrome"
    options.add_argument("window-size=1280,720")
    service = Service(executable_path="/home/intern_share/chrome-linux/chromedriver")
    driver = WebDriver(service=service, options=options)
    try:
        yield driver
    finally:
        # Chromeを閉じる
        driver.close()
        driver.quit()
        service.stop()


with webdriver() as driver:
    # ===== 店舗検索の準備 =====
    # 店舗検索のURL
    SHOP_SEARCH_PAGE_URL = "https://www.au.com/aushop/"
    # 店舗検索ページを開く
    driver.get(SHOP_SEARCH_PAGE_URL)
    time.sleep(5)  # 読み終わるまで待機

    # ===== 都道府県・市区町村で絞り込み =====
    # DOMから検索ボックスを取得する
    search_box = driver.find_element(
        "class name", "cmp-au-com-store-search__searchtext"
    )
    # 都道府県・市区町村を入力する
    search_box.send_keys(TARGET_PREF + TARGET_CITY)
    # 検索ボタンを押クリックして検索を実行する
    search_button = driver.find_element("class name", "cmp-au-com-store-search__submit")
    search_button.click()
    time.sleep(5)  # 結果を読み終わるまで待機

    # ===== 店舗情報取得 =====
    while True:
        # 検索結果のもっと見るボタンを取得
        more_button = driver.find_elements(
            "css selector",
            'a[style="display: inline-block;"] > span.cmp-button__text',
        )
        if more_button:
            # もっと見るボタンが存在すればクリックして店舗情報を展開
            more_button[0].click()
            time.sleep(3)  # 間隔をあけてリクエスト
        else:
            break
    # DOMから店舗リストを取得する
    shop_links = driver.find_elements(
        "css selector",
        ".cmp-au-com-store-search__resultlist .cmp-au-com-store-search__npsstar + .cmp-au-com-link > .cmp-link__text",
    )
    # 店舗リストから各店舗のURLを抽出する
    shop_urls = [ele.get_attribute("href") for ele in shop_links]

    # 店舗の名称、住所、電話番号を取得
    for shop_url in shop_urls:
        # 店舗urlを開く
        error: WebDriverException | None = None
        for _ in range(10):
            try:
                driver.get(shop_url)
            except WebDriverException as e:
                error = e
            else:
                break
            finally:
                time.sleep(5)  # 間隔をあけてリクエスト
        else:
            if error:
                raise error

        # 住所を取得
        eles = driver.find_elements(
            "xpath",
            "//*[contains(@class,'store-detail')]/*/table/*/tr/td[text()='住所']/following-sibling::td",
        )
        shop_addr = eles[0].text.strip().replace("\n", "") if eles else ""

        # 電話番号を取得
        # ===== ↓ 電話番号を取得し `shop_tel` に代入 =====
        eles = driver.find_elements(
            "xpath",
            "//*[contains(@class,'store-detail')]/*/table/*/tr/td[text()='電話番号（有料）']/following-sibling::td/span",
        )
        shop_tel = eles[0].text.strip().replace("\n", "") if eles else ""

        # 店舗名を取得
        # ===== ↓ 店舗名を取得し `shop_name` に代入 =====
        eles = driver.find_elements(
            "css selector",
            ".shop-detail-heading h1",
        )
        shop_name = eles[0].text.strip().replace("\n", "") if eles else ""

        # 定休日を取得
        # ===== ↓ 定休日を取得し `shop_holiday` に代入 =====
        eles = driver.find_elements(
            "xpath",
            "//*[contains(@class,'store-detail')]/*/table/*/tr/td[text()='定休日']/following-sibling::td",
        )
        shop_holiday = eles[0].text.strip().replace("\n", "") if eles else ""

        # 営業時間を取得
        # ===== ↓ 営業時間を取得し `shop_business_hour` に代入 =====
        eles = driver.find_elements(
            "xpath",
            "//*[contains(@class,'store-detail')]/*/table/*/tr/td[text()='営業時間']/following-sibling::td",
        )
        shop_business_hour = eles[0].text.strip().replace("\n", "") if eles else ""


        # prog = re.compile(pattern)
        # pattern = r'\d\d:\d\d～\d\d:\d\d'
        # shop_business_hour = re.compile(pattern)

        # ===== ↓ ここに追加情報を取得するコードを追加 =====

        # 店舗情報を格納
        shop_props = ShopProps(
            name=shop_name,
            address=shop_addr,
            tel=shop_tel,
            business_hours=shop_business_hour,
            holiday=shop_holiday
            # 追加した項目を以下に追加
        )
        # ===== ↑ ここに追加情報を取得するコードを追加 =====

        shops.append(shop_props)
        print(shop_props)


# ===== 店舗情報をデータベース化 =====
# 店舗情報を書き込む（今回はCSVファイル化）
with open(
    f"au_shops_{datetime.now():%Y%m%d%H%M%S}.csv",
    "w",
    encoding="utf8",
) as f:
    fieldnames = {f.name: f.metadata.get("name", f.name) for f in fields(ShopProps)}
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(fieldnames)
    writer.writerows(asdict(shop) for shop in shops)
