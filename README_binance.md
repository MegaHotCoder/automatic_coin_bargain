# 🤖 Binance 기술적 지표 매매 신호 시스템

Binance API를 사용하여 RSI, EMA, MACD 기술적 지표 기반으로 매매 신호를 생성하는 시스템입니다.

## 📋 기능

- **실시간 데이터**: Binance API를 통한 1분봉 실시간 데이터 수집
- **기술적 지표**: RSI(14), EMA(20), MACD 계산
- **매매 신호**: 조건에 따른 buy/sell/hold 신호 생성
- **다중 코인**: BTCUSDT, ETHUSDT, ADAUSDT 지원
- **자동 루프**: 1분마다 자동으로 신호 업데이트

## 🎯 매매 조건

### 🟢 BUY 신호
- RSI < 30 (과매도)
- MACD > Signal (상승 모멘텀)
- Close > EMA20 (상승 추세)

### 🔴 SELL 신호
- RSI > 70 (과매수)
- MACD < Signal (하락 모멘텀)
- Close < EMA20 (하락 추세)

### 🟡 HOLD 신호
- 위 조건에 해당하지 않는 경우

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Binance API 키 설정 (선택사항)
- Binance 계정에서 API 키 생성
- 읽기 권한만 필요 (거래 권한 불필요)
- API 키와 Secret 입력 (또는 Enter로 건너뛰기)

### 3. 실행
```bash
python binance_trading_signals.py
```

## 📊 출력 예시

```
🚀 Binance 기술적 지표 기반 매매 신호 시스템 시작
================================================================================
시간                 심볼           신호   현재가        근거
================================================================================
🟡 2024-01-15 14:30:00 |    BTCUSDT | HOLD | $  43250.5000 | RSI: 45.23, MACD: 0.001234, Signal: 0.001200
🟢 2024-01-15 14:30:00 |    ETHUSDT |  BUY | $   2580.7500 | RSI: 28.45, MACD > Signal, Close > EMA20
🔴 2024-01-15 14:30:00 |    ADAUSDT | SELL | $      0.4850 | RSI: 72.18, MACD < Signal, Close < EMA20
--------------------------------------------------------------------------------
```

## ⚙️ 설정 옵션

### 코인 심볼 변경
`binance_trading_signals.py` 파일의 `self.symbols` 리스트를 수정:

```python
self.symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']  # 원하는 심볼로 변경
```

### 기술적 지표 파라미터 조정
- RSI 기간: `calculate_rsi(prices, period=14)`
- EMA 기간: `calculate_ema(prices, period=20)`
- MACD 파라미터: `calculate_macd(prices, fast=12, slow=26, signal=9)`

### 매매 조건 조정
`generate_signal` 메서드에서 RSI 임계값 변경:
```python
if (current_rsi < 30 and ...):  # 30을 원하는 값으로 변경
elif (current_rsi > 70 and ...):  # 70을 원하는 값으로 변경
```

## 🔧 주요 클래스 및 메서드

### BinanceTradingSignals 클래스

- `get_klines()`: Binance에서 캔들스틱 데이터 가져오기
- `calculate_rsi()`: RSI 지표 계산
- `calculate_ema()`: EMA 지표 계산
- `calculate_macd()`: MACD 지표 계산
- `generate_signal()`: 매매 신호 생성
- `run_trading_signals()`: 메인 루프 실행

## ⚠️ 주의사항

1. **API 제한**: Binance API 호출 제한을 고려하여 적절한 대기 시간 설정
2. **실시간 거래**: 이 시스템은 신호 생성만 하며, 실제 거래는 실행하지 않음
3. **리스크 관리**: 실제 거래 시에는 추가적인 리스크 관리 로직 필요
4. **백테스팅**: 실제 거래 전에 과거 데이터로 백테스팅 권장

## 🛠️ 문제 해결

### API 연결 오류
- 인터넷 연결 확인
- Binance API 서버 상태 확인
- API 키 권한 확인

### 데이터 부족 오류
- 충분한 과거 데이터 확보 필요 (최소 50개 캔들)
- API 호출 제한 확인

### 지표 계산 오류
- pandas, numpy 버전 확인
- 데이터 형식 확인

## 📈 향후 개선 사항

- [ ] 실제 거래 실행 기능 추가
- [ ] 더 많은 기술적 지표 추가
- [ ] 웹 인터페이스 추가
- [ ] 알림 기능 추가
- [ ] 백테스팅 기능 추가
- [ ] 포트폴리오 관리 기능 추가 