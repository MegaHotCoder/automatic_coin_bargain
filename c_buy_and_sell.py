import a_base
import time
from urllib.parse import urlencode
from datetime import datetime
from impo_algo import AITradingStrategy, BinanceTechnicalSignals

# 매매하는 코드

class TradingBot:
    """Korbit 거래소 매매 봇 클래스"""

    def __init__(self):
        self.base_url = a_base.base_url
        self.api_key = a_base.api_key
        self.api_secret = a_base.api_secret

        # 지원하는 거래쌍
        self.supported_symbols = {
            1: 'btc_krw',
            2: 'eth_krw',
            3: 'usdt_krw'
        }

        # 주문 타입
        self.order_types = {
            'limit': 'limit',      # 지정가
            'market': 'market',    # 시장가
            'best': 'best'         # BBO (Best-Bid-Offer)
        }

        # Time in Force 옵션
        self.time_in_force_options = {
            'gtc': 'gtc',  # Good-Till-Canceled
            'ioc': 'ioc',  # Immediate-Or-Cancel
            'fok': 'fok',  # Fill-Or-Kill
            'po': 'po'     # Post-Only
        }

    def create_signature(self, query_string):
        """HMAC-SHA256 서명 생성"""
        return a_base.create_signature(self.api_secret, query_string)

    def place_order(self, symbol, side, price=None, qty=None, amt=None, order_type='limit', time_in_force='gtc', client_order_id=None):
        """
        주문 접수 함수

        Args:
            symbol (str): 거래쌍 (예: 'btc_krw')
            side (str): 'buy' 또는 'sell'
            price (str): 주문 가격 (지정가 주문시 필수)
            qty (str): 주문 수량 (가상자산 단위)
            amt (str): 주문 대금 (KRW 단위, 시장가 매수시 사용)
            order_type (str): 주문 타입 ('limit', 'market', 'best')
            time_in_force (str): 주문 취소 조건
            client_order_id (str): 사용자 지정 주문 ID (선택사항)
        """
        timestamp = int(time.time() * 1000)

        # 기본 파라미터
        params = {
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "timestamp": timestamp,
        }

        # 주문 타입별 파라미터 설정
        if order_type == 'limit':
            if not price:
                raise ValueError("지정가 주문에는 price가 필요합니다.")
            params["price"] = str(price)
            params["timeInForce"] = time_in_force

        elif order_type == 'market':
            params["timeInForce"] = 'ioc'  # 시장가는 항상 ioc

        elif order_type == 'best':
            if not time_in_force:
                raise ValueError("BBO 주문에는 timeInForce가 필요합니다.")
            params["timeInForce"] = time_in_force

        # 수량 또는 대금 설정
        if qty:
            params["qty"] = str(qty)
        elif amt:
            params["amt"] = str(amt)
        else:
            raise ValueError("qty 또는 amt 중 하나는 필수입니다.")

        # 사용자 지정 주문 ID
        if client_order_id:
            params["clientOrderId"] = client_order_id

        # 서명 생성
        query_string = urlencode(params)
        signature = self.create_signature(query_string)
        params["signature"] = signature

        # 헤더 설정
        headers = {
            "X-KAPI-KEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = f"{self.base_url}/v2/orders"

        try:
            response = a_base.requests.post(url, headers=headers, data=params)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                print(f"\n✅ 주문 성공!")
                order_data = result.get('data', {})
                print(f"주문 ID: {order_data.get('orderId')}")
                print(f"거래쌍: {order_data.get('symbol')}")
                print(f"주문 타입: {order_data.get('side')} / {order_data.get('orderType')}")
                print(f"가격: {order_data.get('price', 'N/A')}")
                print(f"수량: {order_data.get('qty', 'N/A')}")
                print(f"대금: {order_data.get('amt', 'N/A')}")
                print(f"상태: {order_data.get('status')}")
                return result
            else:
                error_msg = result.get('error', {}).get('message', '알 수 없는 오류')
                print(f"❌ 주문 실패: {error_msg}")
                return result

        except Exception as e:
            print(f"❌ 주문 요청 중 오류 발생: {e}")
            return None

    def cancel_order(self, symbol, order_id=None, client_order_id=None):
        """
        주문 취소 함수

        Args:
            symbol (str): 거래쌍
            order_id (int): 주문 ID
            client_order_id (str): 사용자 지정 주문 ID
        """
        if not order_id and not client_order_id:
            raise ValueError("order_id 또는 client_order_id 중 하나는 필수입니다.")

        timestamp = int(time.time() * 1000)

        params = {
            "symbol": symbol,
            "timestamp": timestamp,
        }

        if order_id:
            params["orderId"] = str(order_id)
        if client_order_id:
            params["clientOrderId"] = client_order_id

        # 서명 생성
        query_string = urlencode(params)
        signature = self.create_signature(query_string)
        params["signature"] = signature

        # 헤더 설정
        headers = {
            "X-KAPI-KEY": self.api_key,
        }

        url = f"{self.base_url}/v2/orders?{query_string}&signature={signature}"

        try:
            response = a_base.requests.delete(url, headers=headers)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                print(f"✅ 주문 취소 성공!")
                cancel_data = result.get('data', {})
                print(f"취소된 주문 ID: {cancel_data.get('orderId')}")
                return result
            else:
                error_msg = result.get('error', {}).get('message', '알 수 없는 오류')
                print(f"❌ 주문 취소 실패: {error_msg}")
                return result

        except Exception as e:
            print(f"❌ 주문 취소 요청 중 오류 발생: {e}")
            return None

    def get_order_status(self, symbol, order_id=None, client_order_id=None):
        """
        주문 상태 조회 함수

        Args:
            symbol (str): 거래쌍
            order_id (int): 주문 ID
            client_order_id (str): 사용자 지정 주문 ID
        """
        if not order_id and not client_order_id:
            raise ValueError("order_id 또는 client_order_id 중 하나는 필수입니다.")

        timestamp = int(time.time() * 1000)

        params = {
            "symbol": symbol,
            "timestamp": timestamp,
        }

        if order_id:
            params["orderId"] = str(order_id)
        if client_order_id:
            params["clientOrderId"] = client_order_id

        # 서명 생성
        query_string = urlencode(params)
        signature = self.create_signature(query_string)
        params["signature"] = signature

        # 헤더 설정
        headers = {
            "X-KAPI-KEY": self.api_key,
        }

        url = f"{self.base_url}/v2/orders"

        try:
            response = a_base.requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                order_data = result.get('data', {})
                print(f"\n📊 주문 상태 조회 결과:")
                print(f"주문 ID: {order_data.get('orderId')}")
                print(f"거래쌍: {order_data.get('symbol')}")
                print(f"주문 타입: {order_data.get('side')} / {order_data.get('orderType')}")
                print(f"가격: {order_data.get('price', 'N/A')}")
                print(f"수량: {order_data.get('qty', 'N/A')}")
                print(f"체결량: {order_data.get('filledQty', '0')}")
                print(f"체결금액: {order_data.get('filledAmt', '0')}")
                print(f"평균 체결가: {order_data.get('avgPrice', 'N/A')}")
                print(f"상태: {order_data.get('status')}")
                print(f"주문 시간: {datetime.fromtimestamp(order_data.get('createdAt', 0)/1000)}")
                return result
            else:
                error_msg = result.get('error', {}).get('message', '알 수 없는 오류')
                print(f"❌ 주문 조회 실패: {error_msg}")
                return result

        except Exception as e:
            print(f"❌ 주문 조회 요청 중 오류 발생: {e}")
            return None

    def get_open_orders(self, symbol, limit=100):
        """
        미체결 주문 목록 조회

        Args:
            symbol (str): 거래쌍
            limit (int): 최대 조회 건수
        """
        timestamp = int(time.time() * 1000)

        params = {
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
        }

        # 서명 생성
        query_string = urlencode(params)
        signature = self.create_signature(query_string)
        params["signature"] = signature

        # 헤더 설정
        headers = {
            "X-KAPI-KEY": self.api_key,
        }

        url = f"{self.base_url}/v2/openOrders"

        try:
            response = a_base.requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                orders = result.get('data', [])
                print(f"\n📋 미체결 주문 목록 ({len(orders)}건):")
                print("-" * 100)
                print(f"{'주문ID':<12} {'타입':<8} {'가격':<12} {'수량':<12} {'체결량':<12} {'상태':<15}")
                print("-" * 100)

                for order in orders:
                    print(f"{order.get('orderId', 'N/A'):<12} "
                          f"{order.get('side', 'N/A'):<8} "
                          f"{order.get('price', 'N/A'):<12} "
                          f"{order.get('qty', 'N/A'):<12} "
                          f"{order.get('filledQty', '0'):<12} "
                          f"{order.get('status', 'N/A'):<15}")

                print("-" * 100)
                return result
            else:
                error_msg = result.get('error', {}).get('message', '알 수 없는 오류')
                print(f"❌ 미체결 주문 조회 실패: {error_msg}")
                return result

        except Exception as e:
            print(f"❌ 미체결 주문 조회 요청 중 오류 발생: {e}")
            return None

    def get_current_price(self, symbol):
        """현재가 조회"""
        try:
            url = f"{self.base_url}/v2/tickers?symbol={symbol}"
            response = a_base.requests.get(url)
            response.raise_for_status()

            data = response.json()
            if data.get('success') and data.get('data'):
                ticker = data['data'][0]
                return {
                    'symbol': ticker.get('symbol'),
                    'close': float(ticker.get('close', 0)),
                    'bestBidPrice': float(ticker.get('bestBidPrice', 0)),
                    'bestAskPrice': float(ticker.get('bestAskPrice', 0))
                }
            return None
        except Exception as e:
            print(f"❌ 현재가 조회 오류: {e}")
            return None

# 매매 전략 기본 클래스 (나중에 알고리즘 추가용)
class TradingStrategy:
    """매매 전략 기본 클래스"""

    def __init__(self, trading_bot):
        self.bot = trading_bot

    def should_buy(self, symbol, current_price, **kwargs):
        """매수 신호 판단 (서브클래스에서 구현)"""
        raise NotImplementedError("서브클래스에서 구현해야 합니다.")

    def should_sell(self, symbol, current_price, **kwargs):
        """매도 신호 판단 (서브클래스에서 구현)"""
        raise NotImplementedError("서브클래스에서 구현해야 합니다.")

    def calculate_buy_amount(self, symbol, current_price, available_krw):
        """매수 수량 계산 (서브클래스에서 구현)"""
        raise NotImplementedError("서브클래스에서 구현해야 합니다.")

    def calculate_sell_amount(self, symbol, current_price, available_crypto):
        """매도 수량 계산 (서브클래스에서 구현)"""
        raise NotImplementedError("서브클래스에서 구현해야 합니다.")

# 간단한 수동 매매 전략 예시
class ManualTradingStrategy(TradingStrategy):
    """수동 매매 전략"""

    def should_buy(self, symbol, current_price, **kwargs):
        return True  # 수동이므로 항상 True

    def should_sell(self, symbol, current_price, **kwargs):
        return True  # 수동이므로 항상 True

    def calculate_buy_amount(self, symbol, current_price, available_krw):
        # 사용자가 직접 입력
        return None

    def calculate_sell_amount(self, symbol, current_price, available_crypto):
        # 사용자가 직접 입력
        return None

def get_symbol_from_choice(choice):
    """선택 번호를 거래쌍으로 변환"""
    symbol_map = {
        1: 'btc_krw',
        2: 'eth_krw',
        3: 'usdt_krw'
    }
    return symbol_map.get(choice)

def get_symbol_name(symbol):
    """거래쌍을 이름으로 변환"""
    name_map = {
        'btc_krw': 'Bitcoin (BTC/KRW)',
        'eth_krw': 'Ethereum (ETH/KRW)',
        'usdt_krw': 'Tether (USDT/KRW)'
    }
    return name_map.get(symbol, symbol)

def manual_buy_order(bot, symbol):
    """수동 매수 주문"""
    print(f"\n=== {get_symbol_name(symbol)} 매수 주문 ===")

    # 현재가 조회
    price_info = bot.get_current_price(symbol)
    if price_info:
        print(f"현재가: {price_info['close']:,} KRW")
        print(f"매수 1호가: {price_info['bestBidPrice']:,} KRW")
        print(f"매도 1호가: {price_info['bestAskPrice']:,} KRW")

    try:
        print("\n주문 타입을 선택하세요:")
        print("1: 지정가 주문")
        print("2: 시장가 주문")

        order_type_choice = int(input("선택: "))

        if order_type_choice == 1:
            # 지정가 주문
            price = input("매수 가격을 입력하세요 (KRW): ").strip()
            qty = input("매수 수량을 입력하세요: ").strip()

            if not price or not qty:
                print("❌ 가격과 수량을 모두 입력해주세요.")
                return

            result = bot.place_order(
                symbol=symbol,
                side='buy',
                price=price,
                qty=qty,
                order_type='limit'
            )

        elif order_type_choice == 2:
            # 시장가 주문
            amt = input("매수 금액을 입력하세요 (KRW): ").strip()

            if not amt:
                print("❌ 매수 금액을 입력해주세요.")
                return

            result = bot.place_order(
                symbol=symbol,
                side='buy',
                amt=amt,
                order_type='market'
            )

        else:
            print("❌ 올바른 선택지를 입력해주세요.")

    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
    except Exception as e:
        print(f"❌ 매수 주문 중 오류: {e}")

def manual_sell_order(bot, symbol):
    """수동 매도 주문"""
    print(f"\n=== {get_symbol_name(symbol)} 매도 주문 ===")

    # 현재가 조회
    price_info = bot.get_current_price(symbol)
    if price_info:
        print(f"현재가: {price_info['close']:,} KRW")
        print(f"매수 1호가: {price_info['bestBidPrice']:,} KRW")
        print(f"매도 1호가: {price_info['bestAskPrice']:,} KRW")

    try:
        print("\n주문 타입을 선택하세요:")
        print("1: 지정가 주문")
        print("2: 시장가 주문")

        order_type_choice = int(input("선택: "))

        if order_type_choice == 1:
            # 지정가 주문
            price = input("매도 가격을 입력하세요 (KRW): ").strip()
            qty = input("매도 수량을 입력하세요: ").strip()

            if not price or not qty:
                print("❌ 가격과 수량을 모두 입력해주세요.")
                return

            result = bot.place_order(
                symbol=symbol,
                side='sell',
                price=price,
                qty=qty,
                order_type='limit'
            )

        elif order_type_choice == 2:
            # 시장가 주문
            qty = input("매도 수량을 입력하세요: ").strip()

            if not qty:
                print("❌ 매도 수량을 입력해주세요.")
                return

            result = bot.place_order(
                symbol=symbol,
                side='sell',
                qty=qty,
                order_type='market'
            )

        else:
            print("❌ 올바른 선택지를 입력해주세요.")

    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
    except Exception as e:
        print(f"❌ 매도 주문 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 Korbit 매매 봇을 시작합니다!")

    # 매매 봇 초기화
    bot = TradingBot()

    # Binance API 키 자동 로드
    print("\n🔑 API 키 자동 로드 중...")
    try:
        binance_api_key = a_base.binance_api_key
        binance_api_secret = a_base.binance_api_secret
        
        # API 키가 기본값인지 확인
        if (binance_api_key == 'your_binance_api_key_here' or 
            binance_api_secret == 'your_binance_api_secret_here'):
            print("⚠️ Binance API 키가 설정되지 않았습니다. 기본값을 사용합니다.")
            binance_api_key = None
            binance_api_secret = None
        else:
            print("✅ Binance API 키가 성공적으로 로드되었습니다.")
            
    except AttributeError:
        print("⚠️ Binance API 키가 설정되지 않았습니다. 기본값을 사용합니다.")
        binance_api_key = None
        binance_api_secret = None

    # AI 매매 전략 초기화 (기술적 지표 사용)
    binance_signals = BinanceTechnicalSignals(binance_api_key, binance_api_secret)
    ai_strategy = AITradingStrategy(bot, binance_signals)

    while True:
        try:
            print("\n" + "="*60)
            print("🤖 Korbit + 기술적 지표 매매 시스템")
            print("="*60)
            print("🔥 AI 자동 매매 (RSI/EMA/MACD 기반):")
            print("  1: 🤖 AI 자동 매매 시작 (현금4:코인6 비율)")
            print("  0: 🛑 AI 자동 매매 중지")
            print("")
            print("📋 수동 매매:")
            print("  2: 💰 매수 주문")
            print("  3: 💸 매도 주문")
            print("  4: 📊 주문 상태 조회")
            print("  5: 📋 미체결 주문 조회")
            print("  6: ❌ 주문 취소")
            print("  7: 💹 현재가 조회")
            print("")
            print("  9: 🚪 프로그램 종료")
            print("-"*60)

            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":  # AI 자동 매매 시작
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                try:
                    symbol_choice = int(input("선택: "))
                    symbol = get_symbol_from_choice(symbol_choice)

                    if not symbol:
                        print("❌ 올바른 거래쌍을 선택해주세요.")
                        continue

                    ai_strategy.start_auto_trading(symbol)

                    # AI 매매가 실행 중일 때 사용자 입력 대기
                    while ai_strategy.is_running:
                        user_input = input("\n🛑 중지하려면 '0'을 입력하세요 (Enter로 상태 확인): ").strip()
                        if user_input == "0":
                            ai_strategy.stop_auto_trading()
                            break
                        elif user_input == "":
                            # 현재 상태만 표시하고 계속
                            continue
                        else:
                            print("⚠️ '0'을 입력하면 중지, Enter로 상태 확인")

                except ValueError:
                    print("❌ 올바른 숫자를 입력해주세요.")

            elif choice == "0":  # AI 자동 매매 중지
                ai_strategy.stop_auto_trading()

            elif choice == "9":  # 프로그램 종료
                ai_strategy.stop_auto_trading()  # AI 매매 중지
                print("👋 매매 봇을 종료합니다.")
                break

            elif choice in ["2", "3"]:  # 매수/매도
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                symbol_choice = int(input("선택: "))
                symbol = get_symbol_from_choice(symbol_choice)

                if not symbol:
                    print("❌ 올바른 거래쌍을 선택해주세요.")
                    continue

                if choice == "2":
                    manual_buy_order(bot, symbol)
                else:
                    manual_sell_order(bot, symbol)

            elif choice == "4":  # 주문 상태 조회
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                symbol_choice = int(input("선택: "))
                symbol = get_symbol_from_choice(symbol_choice)

                if not symbol:
                    print("❌ 올바른 거래쌍을 선택해주세요.")
                    continue

                order_id = input("주문 ID를 입력하세요: ").strip()
                if order_id:
                    bot.get_order_status(symbol, order_id=int(order_id))
                else:
                    print("❌ 주문 ID를 입력해주세요.")

            elif choice == "5":  # 미체결 주문 조회
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                symbol_choice = int(input("선택: "))
                symbol = get_symbol_from_choice(symbol_choice)

                if not symbol:
                    print("❌ 올바른 거래쌍을 선택해주세요.")
                    continue

                bot.get_open_orders(symbol)

            elif choice == "6":  # 주문 취소
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                symbol_choice = int(input("선택: "))
                symbol = get_symbol_from_choice(symbol_choice)

                if not symbol:
                    print("❌ 올바른 거래쌍을 선택해주세요.")
                    continue

                order_id = input("취소할 주문 ID를 입력하세요: ").strip()
                if order_id:
                    bot.cancel_order(symbol, order_id=int(order_id))
                else:
                    print("❌ 주문 ID를 입력해주세요.")

            elif choice == "7":  # 현재가 조회
                print("\n거래쌍을 선택하세요:")
                print("1: Bitcoin (BTC/KRW)")
                print("2: Ethereum (ETH/KRW)")
                print("3: Tether (USDT/KRW)")

                symbol_choice = int(input("선택: "))
                symbol = get_symbol_from_choice(symbol_choice)

                if not symbol:
                    print("❌ 올바른 거래쌍을 선택해주세요.")
                    continue

                price_info = bot.get_current_price(symbol)
                if price_info:
                    print(f"\n💰 {get_symbol_name(symbol)} 현재가 정보:")
                    print(f"현재가: {price_info['close']:,} KRW")
                    print(f"매수 1호가: {price_info['bestBidPrice']:,} KRW")
                    print(f"매도 1호가: {price_info['bestAskPrice']:,} KRW")
                else:
                    print("❌ 현재가 조회에 실패했습니다.")

            else:
                print("❌ 올바른 메뉴를 선택해주세요.")

        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n👋 사용자에 의해 프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()