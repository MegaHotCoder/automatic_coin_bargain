import a_base

# url = "https://api.korbit.co.kr/v2/orders"

def check():
    url = "https://api.korbit.co.kr/v2/orders"
    response = a_base.requests.get(url)
    data = response.json()
    print(data)

def buy_bit():
    url = "https://api.korbit.co.kr/v2/orders?clientOrderId=20141231-155959-abcdef&symbol=btc_krw&timestamp=시각&signature=서명"

    
check()