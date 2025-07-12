import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import hmac
import hashlib
from urllib.parse import urlencode

class BinanceTradingSignals:
    """Binance API를 사용한 기술적 지표 기반 매매 신호 생성"""
    
    def __init__(self, api_key=None, api_secret=None):
        self.base_url = "https://api.binance.com"
        # 환경 변수에서 API 키 로드 (파라미터가 없을 경우)
        if api_key is None:
            from config import Config
            self.api_key = Config.BINANCE_API_KEY
        else:
            self.api_key = api_key
            
        if api_secret is None:
            from config import Config
            self.api_secret = Config.BINANCE_API_SECRET
        else:
            self.api_secret = api_secret
        
        # 거래할 코인 심볼들
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
    def get_klines(self, symbol, interval='1m', limit=100):
        """Binance에서 캔들스틱 데이터 가져오기"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # DataFrame으로 변환
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # 숫자형으로 변환
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"❌ {symbol} 데이터 가져오기 실패: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """RSI 계산"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            print(f"❌ RSI 계산 오류: {e}")
            return None
    
    def calculate_ema(self, prices, period=20):
        """EMA 계산"""
        try:
            ema = prices.ewm(span=period, adjust=False).mean()
            return ema
        except Exception as e:
            print(f"❌ EMA 계산 오류: {e}")
            return None
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD 계산"""
        try:
            ema_fast = prices.ewm(span=fast, adjust=False).mean()
            ema_slow = prices.ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            return macd_line, signal_line
        except Exception as e:
            print(f"❌ MACD 계산 오류: {e}")
            return None, None
    
    def generate_signal(self, df):
        """매매 신호 생성"""
        try:
            if len(df) < 50:  # 충분한 데이터가 없으면
                return "hold", "데이터 부족"
            
            # 기술적 지표 계산
            rsi = self.calculate_rsi(df['close'], 14)
            ema20 = self.calculate_ema(df['close'], 20)
            macd_line, signal_line = self.calculate_macd(df['close'])
            
            if rsi is None or ema20 is None or macd_line is None or signal_line is None:
                return "hold", "지표 계산 실패"
            
            # 최신 값들
            current_rsi = rsi.iloc[-1]
            current_close = df['close'].iloc[-1]
            current_ema = ema20.iloc[-1]
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            
            # 매매 신호 조건 확인
            if (current_rsi < 30 and 
                current_macd > current_signal and 
                current_close > current_ema):
                return "buy", f"RSI: {current_rsi:.2f}, MACD > Signal, Close > EMA20"
            
            elif (current_rsi > 70 and 
                  current_macd < current_signal and 
                  current_close < current_ema):
                return "sell", f"RSI: {current_rsi:.2f}, MACD < Signal, Close < EMA20"
            
            else:
                return "hold", f"RSI: {current_rsi:.2f}, MACD: {current_macd:.6f}, Signal: {current_signal:.6f}"
                
        except Exception as e:
            print(f"❌ 신호 생성 오류: {e}")
            return "hold", f"오류: {e}"
    
    def print_signal(self, symbol, signal, reason, current_price):
        """신호 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 신호별 이모지
        signal_emoji = {
            "buy": "🟢",
            "sell": "🔴", 
            "hold": "🟡"
        }
        
        emoji = signal_emoji.get(signal, "⚪")
        
        print(f"{emoji} {timestamp} | {symbol:>10} | {signal.upper():>4} | ${current_price:>10.4f} | {reason}")
    
    def run_trading_signals(self):
        """매매 신호 루프 실행"""
        print("🚀 Binance 기술적 지표 기반 매매 신호 시스템 시작")
        print("=" * 80)
        print(f"{'시간':<20} {'심볼':<12} {'신호':<6} {'현재가':<12} {'근거'}")
        print("=" * 80)
        
        while True:
            try:
                for symbol in self.symbols:
                    # 1분봉 데이터 가져오기
                    df = self.get_klines(symbol, '1m', 100)
                    
                    if df is not None and len(df) > 0:
                        # 현재가
                        current_price = float(df['close'].iloc[-1])
                        
                        # 매매 신호 생성
                        signal, reason = self.generate_signal(df)
                        
                        # 신호 출력
                        self.print_signal(symbol, signal, reason, current_price)
                    
                    # API 호출 제한을 위한 짧은 대기
                    time.sleep(0.1)
                
                print("-" * 80)
                
                # 1분 대기
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n👋 프로그램이 사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                print(f"❌ 예상치 못한 오류: {e}")
                time.sleep(60)  # 오류 발생시 1분 대기

def main():
    """메인 실행 함수"""
    print("🤖 Binance 기술적 지표 매매 신호 시스템")
    print("=" * 50)
    print("지원 코인: BTCUSDT, ETHUSDT, ADAUSDT")
    print("기술적 지표: RSI(14), EMA(20), MACD")
    print("매매 조건:")
    print("  🟢 BUY: RSI < 30 and MACD > Signal and Close > EMA20")
    print("  🔴 SELL: RSI > 70 and MACD < Signal and Close < EMA20")
    print("  🟡 HOLD: 그 외의 경우")
    print("=" * 50)
    
    # API 키 입력 (선택사항)
    api_key = input("Binance API Key (선택사항, Enter로 건너뛰기): ").strip()
    api_secret = input("Binance API Secret (선택사항, Enter로 건너뛰기): ").strip()
    
    if not api_key:
        api_key = None
    if not api_secret:
        api_secret = None
    
    # 트레이딩 신호 시스템 초기화
    trading_signals = BinanceTradingSignals(api_key, api_secret)
    
    try:
        # 매매 신호 루프 시작
        trading_signals.run_trading_signals()
    except Exception as e:
        print(f"❌ 시스템 실행 오류: {e}")

if __name__ == "__main__":
    main() 