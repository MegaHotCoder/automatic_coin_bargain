import a_base
import time
from datetime import datetime

# 기존 파일들 import
import b_view_nowprice
import c_buy_and_sell
import d_wallet

def print_banner():
    """시스템 배너 출력"""
    print("\n" + "="*70)
    print("🚀 Korbit + 기술적 지표 통합 암호화폐 거래 시스템")
    print("="*70)
    print("📊 가격 조회 | 💰 매매 거래 | 🏦 잔고 관리 | 🤖 AI 자동매매")
    print("="*70)

def print_menu():
    """메인 메뉴 출력"""
    print("\n📋 메인 메뉴")
    print("-" * 50)
    print("🔍 가격 조회:")
    print("  1: 💹 실시간 가격 조회")
    print("  2: 📈 캔들스틱 차트 보기")
    print("")
    print("💰 매매 거래:")
    print("  3: 🟢 매수 주문")
    print("  4: 🔴 매도 주문")
    print("  5: 📊 주문 상태 조회")
    print("  6: 📋 미체결 주문 조회")
    print("  7: ❌ 주문 취소")
    print("")
    print("🏦 잔고 관리:")
    print("  8: 💰 전체 잔고 확인")
    print("  9: 🎯 특정 자산 잔고 확인")
    print("")
    print("🤖 AI 자동매매 (기술적 지표 기반):")
    print("  10: 🚀 AI 자동매매 시작")
    print("  11: 🛑 AI 자동매매 중지")
    print("")
    print("  0: 🚪 프로그램 종료")
    print("-" * 50)

def get_symbol_choice():
    """거래쌍 선택"""
    print("\n거래쌍을 선택하세요:")
    print("1: Bitcoin (BTC/KRW)")
    print("2: Ethereum (ETH/KRW)")
    print("3: Tether (USDT/KRW)")
    
    try:
        symbol_choice = int(input("선택: "))
        symbol_map = {
            1: 'btc_krw',
            2: 'eth_krw',
            3: 'usdt_krw'
        }
        return symbol_map.get(symbol_choice)
    except ValueError:
        print("❌ 올바른 숫자를 입력해주세요.")
        return None

def get_symbol_name(symbol):
    """거래쌍을 이름으로 변환"""
    name_map = {
        'btc_krw': 'Bitcoin (BTC/KRW)',
        'eth_krw': 'Ethereum (ETH/KRW)',
        'usdt_krw': 'Tether (USDT/KRW)'
    }
    return name_map.get(symbol, symbol)

def main():
    """메인 실행 함수"""
    print_banner()
    
    # API 키 상태 확인
    from config import Config
    Config.print_api_status()
    
    # API 키 유효성 검사
    warnings = Config.validate_api_keys()
    if warnings:
        print("\n⚠️ API 키 설정 경고:")
        for warning in warnings:
            print(f"  {warning}")
        print("\n💡 해결 방법:")
        print("  1. env_example.txt 파일을 .env로 복사")
        print("  2. .env 파일에 실제 API 키 입력")
        print("  3. 프로그램 재시작")
    
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

    # AI 매매 전략 초기화
    from impo_algo import BinanceTechnicalSignals, AITradingStrategy
    binance_signals = BinanceTechnicalSignals(binance_api_key, binance_api_secret)
    trading_bot = c_buy_and_sell.TradingBot()
    ai_strategy = AITradingStrategy(trading_bot, binance_signals)

    while True:
        try:
            print_menu()
            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "0":  # 프로그램 종료
                ai_strategy.stop_auto_trading()
                print("👋 프로그램을 종료합니다.")
                break

            elif choice == "1":  # 실시간 가격 조회
                symbol = get_symbol_choice()
                if symbol:
                    print(f"\n=== {get_symbol_name(symbol)} 실시간 가격 ===")
                    b_view_nowprice.check_correct_price(b_view_nowprice.url, symbol)

            elif choice == "2":  # 캔들스틱 차트
                symbol = get_symbol_choice()
                if symbol:
                    print(f"\n=== {get_symbol_name(symbol)} 캔들스틱 차트 ===")
                    b_view_nowprice.view_candlestick(b_view_nowprice.url, symbol)

            elif choice == "3":  # 매수 주문
                symbol = get_symbol_choice()
                if symbol:
                    c_buy_and_sell.manual_buy_order(trading_bot, symbol)

            elif choice == "4":  # 매도 주문
                symbol = get_symbol_choice()
                if symbol:
                    c_buy_and_sell.manual_sell_order(trading_bot, symbol)

            elif choice == "5":  # 주문 상태 조회
                symbol = get_symbol_choice()
                if symbol:
                    order_id = input("주문 ID를 입력하세요: ").strip()
                    if order_id:
                        trading_bot.get_order_status(symbol, order_id=int(order_id))
                    else:
                        print("❌ 주문 ID를 입력해주세요.")

            elif choice == "6":  # 미체결 주문 조회
                symbol = get_symbol_choice()
                if symbol:
                    trading_bot.get_open_orders(symbol)

            elif choice == "7":  # 주문 취소
                symbol = get_symbol_choice()
                if symbol:
                    order_id = input("취소할 주문 ID를 입력하세요: ").strip()
                    if order_id:
                        trading_bot.cancel_order(symbol, order_id=int(order_id))
                    else:
                        print("❌ 주문 ID를 입력해주세요.")

            elif choice == "8":  # 전체 잔고 확인
                d_wallet.check_balance()

            elif choice == "9":  # 특정 자산 잔고 확인
                currency = input("확인할 자산을 입력하세요 (예: btc, eth, krw): ").strip()
                if currency:
                    d_wallet.get_specific_balance(currency)
                else:
                    print("올바른 자산명을 입력해주세요.")

            elif choice == "10":  # AI 자동매매 시작
                symbol = get_symbol_choice()
                if symbol:
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

            elif choice == "11":  # AI 자동매매 중지
                ai_strategy.stop_auto_trading()

            else:
                print("❌ 올바른 메뉴를 선택해주세요.")

        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n👋 사용자에 의해 프로그램이 중단되었습니다.")
            ai_strategy.stop_auto_trading()
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main() 