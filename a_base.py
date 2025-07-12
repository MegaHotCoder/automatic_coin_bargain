import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from config import Config

# API 키 설정 (환경 변수에서 로드)
api_key = Config.KORBIT_API_KEY
api_secret = Config.KORBIT_API_SECRET
base_url = Config.KORBIT_BASE_URL

# Binance API 키 설정 (환경 변수에서 로드)
binance_api_key = Config.BINANCE_API_KEY
binance_api_secret = Config.BINANCE_API_SECRET

"""HMAC-SHA256 서명을 생성하는 함수"""
# key = api_secret, message = query_string = urllib.parse.urlencode(params) <- 이거 복붙
def create_signature(key, message):    
    key_bytes = key.encode()
    message_bytes = message.encode()
    hmac_hash = hmac.new(key_bytes, message_bytes, hashlib.sha256)
    return hmac_hash.hexdigest()

def check_orders():
    """Korbit 거래소의 주문 정보를 조회하는 함수"""
    timestamp = int(time.time() * 1000)  # 현재 시간 (밀리초 단위)
    
    params = {
        "timestamp": timestamp,  # 필수 파라미터
    }

    # HMAC-SHA256 서명 생성
    signature = create_signature(params, api_secret)
    params["signature"] = signature  # 서명을 추가

    headers = {
        "X-KAPI-KEY": api_key,  # API 키 추가
        "Content-Type": "application/x-www-form-urlencoded",
    }

    url = f"{base_url}/v2/orders"

    try:
        response = requests.post(url, headers=headers, data=params)  # POST 요청
        response.raise_for_status()  # HTTP 에러 체크
        print(response.json())  # 응답 출력
    except requests.exceptions.RequestException as e:
        print("Error fetching orders:", e)