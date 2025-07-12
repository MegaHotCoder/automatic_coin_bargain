import time
import threading
from datetime import datetime
from typing import Optional
import a_base
import requests
import pandas as pd
import numpy as np


# Binance API 기반 기술적 지표 매매 신호 생성
class BinanceTechnicalSignals:
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
        
        # 거래할 코인 심볼들 (Korbit 심볼과 매핑)
        self.symbol_mapping = {
            'btc_krw': 'BTCUSDT',
            'eth_krw': 'ETHUSDT', 
            'usdt_krw': 'ADAUSDT'  # USDT 대신 ADA 사용
        }
        
    def get_klines(self, symbol, interval='1m', limit=100):
        """Binance에서 캔들스틱 데이터 가져오기"""
        try:
            # Korbit 심볼을 Binance 심볼로 변환
            binance_symbol = self.symbol_mapping.get(symbol, symbol)
            
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': binance_symbol,
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
    
    def get_trading_signal(self, symbol: str, current_price: float, portfolio_data: dict) -> dict:
        """
        기술적 지표 기반 매매 신호 생성

        Args:
            symbol: 거래쌍 (예: 'btc_krw')
            current_price: 현재가
            portfolio_data: 포트폴리오 정보 (현재는 사용하지 않음)

        Returns:
            {
                'action': 'buy' | 'sell' | 'hold',
                'confidence': 0.0-1.0,
                'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                'reason': '매매 근거',
                'risk_level': 'low' | 'medium' | 'high'
            }
        """
        try:
            # 1분봉 데이터 가져오기
            df = self.get_klines(symbol, '1m', 100)
            
            if df is None or len(df) < 50:
                return {
                    'action': 'hold',
                    'confidence': 0.0,
                    'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                    'reason': '데이터 부족',
                    'risk_level': 'high',
                    'timestamp': int(time.time() * 1000)
                }
            
            # 기술적 지표 계산
            rsi = self.calculate_rsi(df['close'], 14)
            ema20 = self.calculate_ema(df['close'], 20)
            macd_line, signal_line = self.calculate_macd(df['close'])
            
            if rsi is None or ema20 is None or macd_line is None or signal_line is None:
                return {
                    'action': 'hold',
                    'confidence': 0.0,
                    'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                    'reason': '지표 계산 실패',
                    'risk_level': 'high',
                    'timestamp': int(time.time() * 1000)
                }
            
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
                return {
                    'action': 'buy',
                    'confidence': 0.85,
                    'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                    'reason': f"RSI: {current_rsi:.2f} (과매도), MACD > Signal, Close > EMA20",
                    'risk_level': 'low',
                    'timestamp': int(time.time() * 1000)
                }
            
            elif (current_rsi > 70 and 
                  current_macd < current_signal and 
                  current_close < current_ema):
                return {
                    'action': 'sell',
                    'confidence': 0.85,
                    'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                    'reason': f"RSI: {current_rsi:.2f} (과매수), MACD < Signal, Close < EMA20",
                    'risk_level': 'low',
                    'timestamp': int(time.time() * 1000)
                }
            
            else:
                return {
                    'action': 'hold',
                    'confidence': 0.6,
                    'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                    'reason': f"RSI: {current_rsi:.2f}, MACD: {current_macd:.6f}, Signal: {current_signal:.6f}",
                    'risk_level': 'medium',
                    'timestamp': int(time.time() * 1000)
                }
                
        except Exception as e:
            print(f"❌ 신호 생성 오류: {e}")
            return {
                'action': 'hold',
                'confidence': 0.0,
                'target_ratio': {'cash': 0.4, 'crypto': 0.6},
                'reason': f"오류: {e}",
                'risk_level': 'high',
                'timestamp': int(time.time() * 1000)
            }


class AITradingStrategy:
    """기술적 지표 기반 자동 매매 전략"""

    def __init__(self, trading_bot, technical_signals):
        self.bot = trading_bot
        self.technical_signals = technical_signals
        self.is_running = False
        self.trading_thread = None
        self.target_ratios = {'cash': 0.4, 'crypto': 0.6}  # 현금 4: 코인 6
        self.min_trade_amount = 10000  # 최소 거래 금액 (KRW)
        self.check_interval = 30  # 30초마다 체크

    def start_auto_trading(self, symbol: str = 'btc_krw'):
        """자동 매매 시작"""
        if self.is_running:
            print("⚠️ 이미 자동 매매가 실행 중입니다.")
            return

        self.is_running = True
        self.trading_thread = threading.Thread(
            target=self._trading_loop,
            args=(symbol,),
            daemon=True
        )
        self.trading_thread.start()
        print(f"🤖 AI 자동 매매가 시작되었습니다! (거래쌍: {symbol})")
        print(f"📊 목표 비율: 현금 {self.target_ratios['cash']*100}% : 코인 {self.target_ratios['crypto']*100}%")
        print("⏰ 30초마다 AI 분석을 수행합니다.")
        print("🛑 중지하려면 '0'을 입력하세요.")

    def stop_auto_trading(self):
        """자동 매매 중지"""
        if not self.is_running:
            print("⚠️ 자동 매매가 실행되고 있지 않습니다.")
            return

        self.is_running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        print("🛑 AI 자동 매매가 중지되었습니다.")

    def _trading_loop(self, symbol: str):
        """매매 루프 (별도 스레드에서 실행)"""
        print(f"🔄 AI 매매 루프 시작 (거래쌍: {symbol})")

        while self.is_running:
            try:
                # 1. 현재 포트폴리오 상태 조회
                portfolio = self._get_portfolio_status(symbol)
                if not portfolio:
                    print("❌ 포트폴리오 조회 실패, 30초 후 재시도...")
                    time.sleep(self.check_interval)
                    continue

                # 2. 현재가 조회
                price_info = self.bot.get_current_price(symbol)
                if not price_info:
                    print("❌ 현재가 조회 실패, 30초 후 재시도...")
                    time.sleep(self.check_interval)
                    continue

                current_price = price_info['close']

                # 3. 기술적 지표에서 매매 신호 받기
                signal = self.technical_signals.get_trading_signal(symbol, current_price, portfolio)

                # 4. 매매 신호 출력
                self._print_trading_status(symbol, current_price, portfolio, signal)

                # 5. 매매 실행
                if signal['action'] != 'hold' and signal['confidence'] > 0.7:
                    self._execute_trade(symbol, signal, portfolio, current_price)

                # 6. 다음 체크까지 대기
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"❌ 매매 루프 오류: {e}")
                time.sleep(self.check_interval)

        print("🔄 AI 매매 루프 종료")

    def _get_portfolio_status(self, symbol: str) -> Optional[dict]:
        """포트폴리오 상태 조회"""
        try:
            # 잔고 조회 (d_wallet.py의 로직 활용)
            timestamp = int(time.time() * 1000)
            params = {"timestamp": timestamp}

            from urllib.parse import urlencode
            query_string = urlencode(params)
            signature = a_base.create_signature(a_base.api_secret, query_string)
            params["signature"] = signature

            headers = {"X-KAPI-KEY": a_base.api_key}
            url = f"{a_base.base_url}/v2/balance"

            response = a_base.requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            if not data.get('success'):
                return None

            balances = data.get('data', [])

            # KRW와 암호화폐 잔고 추출
            krw_balance = 0
            crypto_balance = 0
            crypto_symbol = symbol.split('_')[0]  # 'btc_krw' -> 'btc'

            for balance in balances:
                currency = balance.get('currency', '').lower()
                available = float(balance.get('available', 0))

                if currency == 'krw':
                    krw_balance = available
                elif currency == crypto_symbol:
                    crypto_balance = available

            # 현재가로 총 자산 가치 계산
            price_info = self.bot.get_current_price(symbol)
            current_price = price_info['close'] if price_info else 0

            crypto_krw_value = crypto_balance * current_price
            total_krw_value = krw_balance + crypto_krw_value

            return {
                'krw_balance': krw_balance,
                'crypto_balance': crypto_balance,
                'crypto_krw_value': crypto_krw_value,
                'total_krw_value': total_krw_value,
                'current_cash_ratio': krw_balance / total_krw_value if total_krw_value > 0 else 0,
                'current_crypto_ratio': crypto_krw_value / total_krw_value if total_krw_value > 0 else 0
            }

        except Exception as e:
            print(f"❌ 포트폴리오 조회 오류: {e}")
            return None

    def _print_trading_status(self, symbol: str, current_price: float, portfolio: dict, signal: dict):
        """현재 매매 상태 출력"""
        print(f"\n{'='*60}")
        print(f"🤖 AI 매매 분석 결과 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"📈 {symbol.upper()}: {current_price:,.0f} KRW")
        print(f"💰 총 자산: {portfolio['total_krw_value']:,.0f} KRW")
        print(f"💵 현금: {portfolio['krw_balance']:,.0f} KRW ({portfolio['current_cash_ratio']*100:.1f}%)")
        print(f"🪙 코인: {portfolio['crypto_balance']:.6f} ({portfolio['current_crypto_ratio']*100:.1f}%)")
        print(f"🎯 목표 비율: 현금 {self.target_ratios['cash']*100}% : 코인 {self.target_ratios['crypto']*100}%")
        print(f"🧠 AI 판단: {signal['action'].upper()} (신뢰도: {signal['confidence']*100:.1f}%)")
        print(f"📝 근거: {signal['reason']}")
        print(f"{'='*60}")

    def _execute_trade(self, symbol: str, signal: dict, portfolio: dict, current_price: float):
        """매매 실행"""
        try:
            action = signal['action']
            confidence = signal['confidence']

            if action == 'buy':
                self._execute_buy(symbol, portfolio, current_price, confidence)
            elif action == 'sell':
                self._execute_sell(symbol, portfolio, current_price, confidence)

        except Exception as e:
            print(f"❌ 매매 실행 오류: {e}")

    def _execute_buy(self, symbol: str, portfolio: dict, current_price: float, confidence: float):
        """매수 실행"""
        krw_balance = portfolio['krw_balance']
        current_cash_ratio = portfolio['current_cash_ratio']
        target_cash_ratio = self.target_ratios['cash']

        # 현금 비율이 목표보다 높을 때만 매수
        if current_cash_ratio <= target_cash_ratio:
            print(f"⏭️ 매수 스킵: 현금 비율이 목표 이하 ({current_cash_ratio*100:.1f}% <= {target_cash_ratio*100}%)")
            return

        # 매수 금액 계산 (신뢰도와 비율 차이에 따라 조정)
        ratio_diff = current_cash_ratio - target_cash_ratio
        buy_ratio = min(ratio_diff * confidence, 0.1)  # 최대 10%씩 매수
        buy_amount = krw_balance * buy_ratio

        if buy_amount < self.min_trade_amount:
            print(f"⏭️ 매수 스킵: 거래 금액이 최소 금액 미만 ({buy_amount:,.0f} < {self.min_trade_amount:,.0f})")
            return

        print(f"🟢 AI 매수 실행: {buy_amount:,.0f} KRW")

        # 시장가 매수 주문
        result = self.bot.place_order(
            symbol=symbol,
            side='buy',
            amt=str(int(buy_amount)),
            order_type='market'
        )

        if result and result.get('success'):
            print(f"✅ 매수 주문 성공!")
        else:
            print(f"❌ 매수 주문 실패")

    def _execute_sell(self, symbol: str, portfolio: dict, current_price: float, confidence: float):
        """매도 실행"""
        crypto_balance = portfolio['crypto_balance']
        current_crypto_ratio = portfolio['current_crypto_ratio']
        target_crypto_ratio = self.target_ratios['crypto']

        # 코인 비율이 목표보다 높을 때만 매도
        if current_crypto_ratio <= target_crypto_ratio:
            print(f"⏭️ 매도 스킵: 코인 비율이 목표 이하 ({current_crypto_ratio*100:.1f}% <= {target_crypto_ratio*100}%)")
            return

        # 매도 수량 계산
        ratio_diff = current_crypto_ratio - target_crypto_ratio
        sell_ratio = min(ratio_diff * confidence, 0.1)  # 최대 10%씩 매도
        sell_quantity = crypto_balance * sell_ratio

        # 최소 거래 금액 체크
        sell_value = sell_quantity * current_price
        if sell_value < self.min_trade_amount:
            print(f"⏭️ 매도 스킵: 거래 금액이 최소 금액 미만 ({sell_value:,.0f} < {self.min_trade_amount:,.0f})")
            return

        print(f"🔴 AI 매도 실행: {sell_quantity:.6f} (약 {sell_value:,.0f} KRW)")

        # 시장가 매도 주문
        result = self.bot.place_order(
            symbol=symbol,
            side='sell',
            qty=f"{sell_quantity:.6f}",
            order_type='market'
        )

        if result and result.get('success'):
            print(f"✅ 매도 주문 성공!")
        else:
            print(f"❌ 매도 주문 실패")