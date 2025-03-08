import a_base
import pandas as pd
import mplfinance as mpf
import seaborn as sns
import matplotlib.pyplot as plt
import json

url = 'https://api.korbit.co.kr/v2/tickers?symbol='

def check_correct_price(url,symbol):

    if symbol == 1:
        symbol = 'btc_krw'
    elif symbol == 2:
        symbol = 'eth_krw'
    elif symbol == 3:
        symbol = 'usdt_krw'

    url = f'{url}{symbol}'
    try:
        response = a_base.requests.get(url)
        response.raise_for_status()  # 응답 코드가 200이 아닐 경우 예외 발생
        data = response.json()  # JSON 데이터를 파싱
        
        ticker_info = data.get('data', [])[0]  # 'data' 리스트의 첫 번째 항목 가져오기
        print("\n--- 가격 정보 ---")
        print(f"종목: {ticker_info['symbol']}")
        print(f"시가: {ticker_info['open']}")
        print(f"고가: {ticker_info['high']}")
        print(f"저가: {ticker_info['low']}")
        print(f"종가: {ticker_info['close']}")
        print(f"전일 종가: {ticker_info['prevClose']}")
        print(f"변동 폭: {ticker_info['priceChange']}")
        print(f"변동률: {ticker_info['priceChangePercent']}%")
        print(f"거래량: {ticker_info['volume']}")
        print(f"매수 호가: {ticker_info['bestBidPrice']}")
        print(f"매도 호가: {ticker_info['bestAskPrice']}")
        print('----------------------------------')

    except a_base.requests.exceptions.RequestException as e:
        print("Error fetching data:", e)

def view_candlestick(url, symbol):
    if symbol == 1:
        symbol = 'btc_krw'
    elif symbol == 2:
        symbol = 'eth_krw'
    elif symbol == 3:
        symbol = 'usdt_krw'

    correct_time = int(a_base.time.time() * 1000)  # 현재 시간 (밀리초)
    start_time = correct_time - (40 * 60 * 60 * 1000)  # 40시간 전 (밀리초)

    url = f'https://api.korbit.co.kr/v2/candles?symbol={symbol}&interval=240&limit=10&start={start_time}&end={correct_time}'

    try:
        response = a_base.requests.get(url)
        response.raise_for_status()  # 응답 코드가 200이 아닐 경우 예외 발생
        raw_data = response.json()

        for candle_info in raw_data:  # 여러 개의 캔들 데이터 순회
            print(f"시간: {candle_info[0]}")
            print(f"open: {candle_info['open']}")
            print(f"high: {candle_info['high']}")
            print(f"low: {candle_info['low']}")
            print(f"close: {candle_info['close']}")
            print(f"volume: {candle_info['volume']}")
            print("-" * 30)  # 구분선

    except a_base.requests.exceptions.RequestException as e:
        print("Error fetching data:", e)

# python b_view_nowprice.py
symbol = 1
pick = 0
while symbol != 0:

    symbol = int(input('''  1: 비트코인
                        2: 이더리움
                        3: 테더코인
                        작성: '''))
    
    if symbol == 0:
        print('중단되었습니다')
    else:
        check_correct_price(url,symbol)
        pick = int(input('차트를 보고싶습니까? yes: 1, no: 0'))
        if pick == 0:
            continue
        else:
            view_candlestick(url,symbol)


