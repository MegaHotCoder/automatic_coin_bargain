import time
import hmac
import hashlib
import requests
import a_base
from urllib.parse import urlencode

# API 키 및 비밀 키
api_key = a_base.api_key
api_secret = a_base.api_secret

# 기본 URL
base_url = "https://api.korbit.co.kr"

# HMAC-SHA256 서명 생성 함수
def create_hmac_signature(query):
    return hmac.new(api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()

# 주문 접수 (POST 요청)
def place_order(symbol, side, price, qty, order_type, time_in_force):
    timestamp = int(time.time() * 1000)  # 현재 시각 타임스탬프(밀리세컨드)
    
    params = {
        "symbol": symbol,
        "side": side,
        "price": price,
        "qty": qty,
        "orderType": order_type,
        "timeInForce": time_in_force,
        "timestamp": timestamp,
    }
    
    query_string = urlencode(params)
    signature = create_hmac_signature(query_string)
    params["signature"] = signature
    
    url = f"{base_url}/v2/orders"
    headers = {
        "X-KAPI-KEY": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    try:
        response = requests.post(url, headers=headers, data=params)
        return response.json()
    except Exception as e:
        print("Error placing order:", e)
        return None

# 주문 취소 (DELETE 요청)
def cancel_order(symbol, order_id):
    timestamp = int(time.time() * 1000)
    
    params = {
        "symbol": symbol,
        "orderId": order_id,
        "timestamp": timestamp,
    }
    
    query_string = urlencode(params)
    signature = create_hmac_signature(query_string)
    params["signature"] = signature
    
    url = f"{base_url}/v2/orders?{query_string}&signature={signature}"
    headers = {
        "X-KAPI-KEY": api_key,
    }
    
    try:
        response = requests.delete(url, headers=headers)
        return response.json()
    except Exception as e:
        print("Error canceling order:", e)
        return None

# BTC 매수 주문 전송
order_response = place_order("btc_krw", "buy", "90000000", "0.5", "limit", "gtc")
print("Order Response:", order_response)

# BTC 주문 취소 (Order ID: 1000001234)
cancel_response = cancel_order("btc_krw", 1000001234)
print("Cancel Response:", cancel_response)