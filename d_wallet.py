import a_base
import time
from urllib.parse import urlencode

#잔고 확인

def check_balance():
    """Korbit 거래소의 잔고 정보를 조회하는 함수"""
    timestamp = int(time.time() * 1000)  # 현재 시간 (밀리초 단위)

    params = {
        "timestamp": timestamp,  # 필수 파라미터
    }

    # URL 쿼리 스트링 생성
    query_string = urlencode(params)

    # HMAC-SHA256 서명 생성
    signature = a_base.create_signature(a_base.api_secret, query_string)
    params["signature"] = signature  # 서명을 추가

    headers = {
        "X-KAPI-KEY": a_base.api_key,  # API 키 추가
    }

    url = f"{a_base.base_url}/v2/balance"

    try:
        response = a_base.requests.get(url, headers=headers, params=params)  # GET 요청
        response.raise_for_status()  # HTTP 에러 체크

        data = response.json()

        if data.get('success'):
            balances = data.get('data', [])
            print("\n=== 잔고 현황 ===")
            print(f"{'자산':<10} {'보유량':<15} {'사용가능':<15} {'거래중':<15} {'출금중':<15}")
            print("-" * 75)

            for balance in balances:
                currency = balance.get('currency', 'N/A')
                total = balance.get('balance', '0')
                available = balance.get('available', '0')
                trade_in_use = balance.get('tradeInUse', '0')
                withdrawal_in_use = balance.get('withdrawalInUse', '0')

                # 잔고가 0이 아닌 경우만 출력
                if float(total) > 0:
                    print(f"{currency:<10} {total:<15} {available:<15} {trade_in_use:<15} {withdrawal_in_use:<15}")

            print("-" * 75)
            print("* 보유량 = 사용가능 + 거래중 + 출금중")

        else:
            print("잔고 조회 실패:", data.get('error', {}).get('message', '알 수 없는 오류'))

    except a_base.requests.exceptions.RequestException as e:
        print("Error fetching balance:", e)
    except Exception as e:
        print("예상치 못한 오류:", e)

def get_specific_balance(currency):
    """특정 자산의 잔고만 조회하는 함수"""
    timestamp = int(time.time() * 1000)

    params = {
        "timestamp": timestamp,
    }

    query_string = urlencode(params)
    signature = a_base.create_signature(a_base.api_secret, query_string)
    params["signature"] = signature

    headers = {
        "X-KAPI-KEY": a_base.api_key,
    }

    url = f"{a_base.base_url}/v2/balance"

    try:
        response = a_base.requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get('success'):
            balances = data.get('data', [])

            for balance in balances:
                if balance.get('currency', '').lower() == currency.lower():
                    print(f"\n=== {currency.upper()} 잔고 ===")
                    print(f"보유량: {balance.get('balance', '0')}")
                    print(f"사용가능: {balance.get('available', '0')}")
                    print(f"거래중: {balance.get('tradeInUse', '0')}")
                    print(f"출금중: {balance.get('withdrawalInUse', '0')}")
                    return balance

            print(f"{currency.upper()} 잔고를 찾을 수 없습니다.")
            return None

        else:
            print("잔고 조회 실패:", data.get('error', {}).get('message', '알 수 없는 오류'))
            return None

    except Exception as e:
        print("Error fetching specific balance:", e)
        return None

def main():
    """메인 실행 함수"""
    while True:
        try:
            print("\n=== Korbit 지갑 잔고 확인 ===")
            print("1: 전체 잔고 확인")
            print("2: 특정 자산 잔고 확인")
            print("0: 종료")

            choice = input("선택하세요: ").strip()

            if choice == "0":
                print("프로그램을 종료합니다.")
                break
            elif choice == "1":
                check_balance()
            elif choice == "2":
                currency = input("확인할 자산을 입력하세요 (예: btc, eth, krw): ").strip()
                if currency:
                    get_specific_balance(currency)
                else:
                    print("올바른 자산명을 입력해주세요.")
            else:
                print("올바른 선택지를 입력해주세요 (0, 1, 2)")

        except KeyboardInterrupt:
            print("\n프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()

