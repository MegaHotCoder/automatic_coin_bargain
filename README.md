# 🤖 Korbit + Binance 통합 암호화폐 거래 시스템

Korbit 거래소와 Binance API를 연동한 기술적 지표 기반 자동매매 시스템입니다.

## 📋 주요 기능

- **실시간 가격 조회**: Korbit API를 통한 실시간 가격 정보
- **캔들스틱 차트**: mplfinance를 사용한 시각적 차트
- **수동 매매**: 지정가/시장가 매수/매도 주문
- **자동매매**: AI 기반 기술적 지표 매매 신호
- **잔고 관리**: 포트폴리오 현황 및 특정 자산 조회
- **주문 관리**: 주문 상태 조회, 미체결 주문, 주문 취소

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정

#### 방법 1: 환경 변수 파일 사용 (권장)
```bash
# 1. env_example.txt를 .env로 복사
cp env_example.txt .env

# 2. .env 파일 편집하여 실제 API 키 입력
KORBIT_API_KEY=your_actual_korbit_api_key
KORBIT_API_SECRET=your_actual_korbit_api_secret
BINANCE_API_KEY=your_actual_binance_api_key
BINANCE_API_SECRET=your_actual_binance_api_secret
```

#### 방법 2: 시스템 환경 변수 설정
```bash
# Windows
set KORBIT_API_KEY=your_api_key
set KORBIT_API_SECRET=your_api_secret

# macOS/Linux
export KORBIT_API_KEY=your_api_key
export KORBIT_API_SECRET=your_api_secret
```

### 3. API 키 발급

#### Korbit API 키
1. [Korbit](https://www.korbit.co.kr) 계정 생성
2. API 키 발급 (거래 권한 필요)
3. API 키와 Secret 복사

#### Binance API 키 (선택사항)
1. [Binance](https://www.binance.com) 계정 생성
2. API 키 발급 (읽기 권한만 필요)
3. API 키와 Secret 복사

## 🎯 사용 방법

### 메인 시스템 실행
```bash
python ab_all.py
```

### 개별 모듈 실행
```bash
# 가격 조회
python b_view_nowprice.py

# 매매 거래
python c_buy_and_sell.py

# 잔고 확인
python d_wallet.py

# Binance 매매 신호
python binance_trading_signals.py
```

## 📊 시스템 구조

```
coinbase/
├── ab_all.py              # 통합 메인 시스템
├── a_base.py              # 기본 설정 및 API 인증
├── b_view_nowprice.py     # 가격 조회 및 차트
├── c_buy_and_sell.py      # 매매 거래 실행
├── d_wallet.py            # 잔고 관리
├── impo_algo.py           # AI 자동매매 알고리즘
├── binance_trading_signals.py  # Binance 매매 신호
├── config.py              # 환경 변수 설정
├── env_example.txt        # 환경 변수 예시
├── requirements.txt       # 의존성 목록
└── README.md             # 프로젝트 문서
```

## 🔧 주요 클래스

### TradingBot (c_buy_and_sell.py)
- Korbit 거래소 API 연동
- 주문 접수, 취소, 상태 조회
- 지정가/시장가/BBO 주문 지원

### AITradingStrategy (impo_algo.py)
- 기술적 지표 기반 자동매매
- 포트폴리오 밸런싱 (현금 40% : 코인 60%)
- 30초마다 자동 분석 및 거래

### BinanceTechnicalSignals (impo_algo.py)
- Binance API 기반 기술적 지표 계산
- RSI, EMA, MACD 지표 활용
- 매매 신호 생성

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일을 절대 GitHub에 업로드하지 마세요
2. **실제 거래**: 이 시스템은 실제 거래를 실행합니다. 충분한 테스트 후 사용하세요
3. **리스크 관리**: 자동매매 사용 시 손실 위험을 고려하세요
4. **API 제한**: 거래소별 API 호출 제한을 확인하세요

## 🛠️ 문제 해결

### API 키 오류
- `.env` 파일이 올바른 위치에 있는지 확인
- API 키 형식이 정확한지 확인
- 거래소에서 API 키 권한 확인

### 모듈 오류
```bash
# 의존성 재설치
pip install -r requirements.txt --upgrade
```

### 권한 오류
- API 키에 적절한 권한이 있는지 확인
- IP 화이트리스트 설정 확인

## 📈 기술적 지표

### 매수 조건 (BUY)
- RSI < 30 (과매도)
- MACD > Signal (상승 모멘텀)
- Close > EMA20 (상승 추세)

### 매도 조건 (SELL)
- RSI > 70 (과매수)
- MACD < Signal (하락 모멘텀)
- Close < EMA20 (하락 추세)

## 🔄 업데이트 내역

- v1.0: 기본 매매 시스템 구현
- v1.1: AI 자동매매 추가
- v1.2: 환경 변수 보안 강화
- v1.3: 포트폴리오 밸런싱 개선

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 실제 거래 시 발생하는 손실에 대해 책임지지 않습니다. 