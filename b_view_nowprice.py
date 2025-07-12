import a_base
import pandas as pd
import mplfinance as mpf
import seaborn as sns
import matplotlib.pyplot as plt
import json

#가격 확인 및 그래프 보여주기

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
        symbol_name = 'BTC/KRW'
        symbol = 'btc_krw'
    elif symbol == 2:
        symbol_name = 'ETH/KRW'
        symbol = 'eth_krw'
    elif symbol == 3:
        symbol_name = 'USDT/KRW'
        symbol = 'usdt_krw'

    # 캔들 데이터 요청 URL 수정
    candle_url = f'https://api.korbit.co.kr/v2/candles?symbol={symbol}&interval=1D&limit=10'

    try:
        response = a_base.requests.get(candle_url)
        response.raise_for_status()
        raw_data = response.json()
        
        # 응답 데이터 구조 확인
        print(f"API 응답 데이터 타입: {type(raw_data)}")
        if isinstance(raw_data, dict):
            print(f"응답 키들: {raw_data.keys()}")
            # 'data' 키가 있는지 확인
            if 'data' in raw_data:
                candles = raw_data['data']
            else:
                print("응답 데이터에 'data' 키가 없습니다.")
                print("전체 응답:", raw_data)
                return
        elif isinstance(raw_data, list):
            candles = raw_data
        else:
            print("예상하지 못한 데이터 구조입니다.")
            print("응답 데이터:", raw_data)
            return

        if not candles:
            print("캔들 데이터가 비어있습니다.")
            return

        # 데이터를 pandas DataFrame으로 변환
        df_data = []
        for candle in candles:
            try:
                # 타임스탬프 처리 개선
                timestamp = candle.get('timestamp')
                if timestamp:
                    # 밀리초 단위인지 초 단위인지 확인
                    if timestamp > 1e12:  # 밀리초 단위
                        timestamp = timestamp / 1000
                    
                    # datetime 객체로 변환
                    date = pd.to_datetime(timestamp, unit='s')
                else:
                    print("타임스탬프 데이터가 없습니다.")
                    continue
                
                df_data.append({
                    'Date': date,
                    'Open': float(candle.get('open', 0)),
                    'High': float(candle.get('high', 0)),
                    'Low': float(candle.get('low', 0)),
                    'Close': float(candle.get('close', 0)),
                    'Volume': float(candle.get('volume', 0))
                })
            except (ValueError, TypeError) as e:
                print(f"캔들 데이터 처리 중 오류: {e}")
                print(f"문제 캔들 데이터: {candle}")
                continue

        if not df_data:
            print("처리 가능한 캔들 데이터가 없습니다.")
            return

        # DataFrame 생성 및 인덱스 설정
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)

        # 데이터 확인
        print(f"DataFrame 크기: {df.shape}")
        print(f"날짜 범위: {df.index.min()} ~ {df.index.max()}")

        # mplfinance를 사용해서 캔들스틱 차트 그리기
        mpf.plot(df, 
                type='candle',
                style='charles',
                title=f'{symbol_name} 일봉 차트 (최근 {len(df)}일)',
                ylabel='Price (KRW)',
                volume=True,
                figsize=(12, 8),
                show_nontrading=False)

        print(f"\n{symbol_name} 일봉 차트가 표시되었습니다.")

    except a_base.requests.exceptions.RequestException as e:
        print("API 요청 오류:", e)
    except Exception as e:
        print("차트 생성 오류:", e)
        import traceback
        traceback.print_exc()


# 메인 실행 부분
def main():
    symbol = 1
    pick = 0
    
    while symbol != 0:
        try:
            symbol = int(input('''  1: 비트코인
                        2: 이더리움
                        3: 테더코인
                        작성: '''))
            
            if symbol == 0:
                print('중단되었습니다')
                break
            elif symbol not in [1, 2, 3]:
                print('올바른 번호를 입력해주세요 (0, 1, 2, 3)')
                continue
            
            check_correct_price(url, symbol)
            
            pick = int(input('차트를 보고싶습니까? yes: 1, no: 0: '))
            if pick == 1:
                view_candlestick(url, symbol)
            elif pick != 0:
                print('0 또는 1을 입력해주세요.')
                
        except ValueError:
            print('숫자를 입력해주세요.')
        except KeyboardInterrupt:
            print('\n프로그램이 중단되었습니다.')
            break

if __name__ == "__main__":
    main()

