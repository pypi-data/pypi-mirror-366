import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import requests
import pandas as pd


# year 年
#  quarter 季度
# month 月度
# week 周
# day 日
def get_xue_qiu_k_line(symbol, period, cookie, end_time, hq):
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"

    params = {
        "symbol": symbol,
        "begin": end_time,
        "period": period,
        "type": hq,
        "count": "-120084",
        "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://xueqiu.com",
        "priority": "u=1, i",
        "referer": "https://xueqiu.com/S/SZ300879?md5__1038=n4%2BxgDniDQeWqxYwq0y%2BbDyG%2BYDtODuD7q%2BqRYID",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "cookie": cookie
    }

    response = requests.get(
        url=url,
        params=params,
        headers=headers
    )

    if response.status_code == 200:
        response_data = response.json()
        df = pd.DataFrame(
            data=response_data['data']['item'],
            columns=response_data['data']['column']
        )

        # 1. 转换为 datetime（自动处理毫秒级时间戳）
        df["beijing_time"] = pd.to_datetime(df["timestamp"], unit="ms")

        # 2. 设置 UTC 时区
        df["beijing_time"] = df["beijing_time"].dt.tz_localize("UTC")

        # 3. 转换为北京时间（UTC+8）
        df["beijing_time"] = df["beijing_time"].dt.tz_convert("Asia/Shanghai")

        # 4. 提取年月日（格式：YYYY-MM-DD）
        df["str_day"] = df["beijing_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        del df["beijing_time"]

        return df
    else:
        # 直接抛出带有明确信息的异常
        raise ValueError("调用雪球接口失败")


if __name__ == '__main__':
    number = 1
    cookies ='cookiesu=431747207996803; device_id=e7bd664c2ad4091241066c3a2ddbd736; xq_is_login=1; u=9627701445; s=ck12tdw0na; bid=7a2d53b7ab3873ab7ec53349413f0a21_mb9aqxtx; xq_a_token=287767c9ca1fce01ce3022eceec5e0ce14f77840; xqat=287767c9ca1fce01ce3022eceec5e0ce14f77840; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjk2Mjc3MDE0NDUsImlzcyI6InVjIiwiZXhwIjoxNzU0NzkxNTExLCJjdG0iOjE3NTIxOTk1MTE2OTYsImNpZCI6ImQ5ZDBuNEFadXAifQ.lAu_FRmvtIgHoK08PJo-a2RPBXiEd7mYp_Iw6S18CIciREuHnGsGkSRz64ZziGD4HRH3_tu8I24DZ1zFHTujFD2t6MBVVFGdN7JV6mhw0JJos2sgIAr6ykm3KJ9rNqiBeSQ1OGBm-5NC5kV3CJNZJj7YICJLJIjKx7940T1TFa3q5gxdDsg2UaRuWprW7cwLp3wtF7NUZ6Kv-OE9C-VaeNlosIFrs5fv1Egp5C5v4INGEK2WwKrhI7GBqfUvWSXXAw4Y-i1UiDVA2L1P_jJgLxvD-ObwgaB40H9hEXd9GpioObTeL1fVylZUpCBO3U03kMBoWj3IBIalEv4jwMIY7Q; xq_r_token=46ef264c7236f56849c570ed35df3f676411df2e; is_overseas=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1752678044,1752761137,1752849755,1752932654; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1752932654; HMACCOUNT=16733F9B51C8BBB0; ssxmod_itna=QqjOAKYIwGkYDQG0bGCYG2DmxewDAo40QDXDUqAQtGgnDFqAPDODCOGKD5=RmIqg3qmrBG03oBpBqNDl6GeDZDGKQDqx0ob0/Gq4N5iWA0EjK5ooq4HvdmgeHpNQN4hg5yRbGkDunLTjGCFDrPjouxli4DHxi8DBIiAgPDx1PD5xDTDWeDGDD3HxGaDmeDe=SmD04v+83fC8o3D7eDXxGC7G4jDiPD72O4hxxvMRBviDDzijQeoWPtRDi3CF3w9+4KDiyDp4YvD7y3Dlcx+NQD0=zgij8ECq7nQOo6n40OD0IUwSYKnlOLv8brq=RrKd2dRD5mBDtODSotiADdgt=AO=YhsAxm0ha7Y32DY4ozOmmDDi2wIpebBpNmD4i+gOXl2EZcNbAiO0vh00e0mdReeEDYW2hKQbjmzlwGQmdfmGFhdm2qowa+I3YD; ssxmod_itna2=QqjOAKYIwGkYDQG0bGCYG2DmxewDAo40QDXDUqAQtGgnDFqAPDODCOGKD5=RmIqg3qmrBG03oBpBqoDi2MrbKDFr9xYbVhwDD/Uz1i4U0e+aSDYkhpYjW9qKmzrqfshLF9aysbTz/k/6oaPAxux6OB5Mxqt6owO3tH4q7IQEZhW/OH4b1gD3zgIBni8Q9ohL2EO0gBHiQSWHZxCdCp8NUc4HfF1B/r6olczq3PQeA3UttTkiGKLdv0Fzbj246aqovDwV1Dwfcgz1MB4iuF0koTRtFZieygxBSpOmM3vsY/xVnP2tbiPE=H2mHCQI8nKhY0IGhXQuAGrPQm8A9MW7iYKt3acIr63apIhU7e/+TPIKvewm8vOIB4iO+bqea5nWuYaFYKY35DtjmWU+Q0h+9nHW+dvO9BneZo2WR2UT6i5FIYxSF4W5h/DrEfpnpbNwp/PF5T4vfDc7bV8+9yHMOb=aC9Hke30+cOFF/Kwk658nPcfmbypO8IFhgg9Bsy+UDpqbTRAKHfPkaAkg3mHnbvocYm8ZFh5udkp+qypgqD2g750QV27Mx2Yq7nOedZ1Z5tI4mr08Co9CWq/ot4pWYG7mhj9OwetU+0f1yFU7O24ntCk8=xcw/3YpDepZmLcFQpfSSYDcI1nk31ook=QDYVeuQV8yUn5+EUCma11vKDoj54bRkgKaj+GBNDuXZx8wNGoCPfD4KAhjKXuCrdWazQaNBIehVazl5upQG3PG90hge7iP17Whoiqe4472KtaChYKKHbrCPa0AQG=ix0iKqqn8A+=b=NGWAPmDoDxqOrUeZ0Neeq2cAe5irbm=i/2q4D'
    while True:
        test_df = get_xue_qiu_k_line('IBM', 'day', cookies, '1753019072159', '')
        print(number)
        number = number + 1
