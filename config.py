import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """API 키 및 설정 관리 클래스"""
    
    # Korbit API 설정
    KORBIT_API_KEY = os.getenv('KORBIT_API_KEY', 'your_korbit_api_key_here')
    KORBIT_API_SECRET = os.getenv('KORBIT_API_SECRET', 'your_korbit_api_secret_here')
    KORBIT_BASE_URL = "https://api.korbit.co.kr"
    
    # Binance API 설정
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_binance_api_key_here')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', 'your_binance_api_secret_here')
    BINANCE_BASE_URL = "https://api.binance.com"
    
    @classmethod
    def validate_api_keys(cls):
        """API 키 유효성 검사"""
        warnings = []
        
        if cls.KORBIT_API_KEY == 'your_korbit_api_key_here':
            warnings.append("⚠️ Korbit API 키가 설정되지 않았습니다.")
        if cls.KORBIT_API_SECRET == 'your_korbit_api_secret_here':
            warnings.append("⚠️ Korbit API Secret이 설정되지 않았습니다.")
        if cls.BINANCE_API_KEY == 'your_binance_api_key_here':
            warnings.append("⚠️ Binance API 키가 설정되지 않았습니다.")
        if cls.BINANCE_API_SECRET == 'your_binance_api_secret_here':
            warnings.append("⚠️ Binance API Secret이 설정되지 않았습니다.")
            
        return warnings
    
    @classmethod
    def print_api_status(cls):
        """API 키 상태 출력"""
        print("\n🔑 API 키 상태 확인")
        print("-" * 40)
        
        korbit_status = "✅ 설정됨" if cls.KORBIT_API_KEY != 'your_korbit_api_key_here' else "❌ 설정되지 않음"
        binance_status = "✅ 설정됨" if cls.BINANCE_API_KEY != 'your_binance_api_key_here' else "❌ 설정되지 않음"
        
        print(f"Korbit API: {korbit_status}")
        print(f"Binance API: {binance_status}")
        print("-" * 40) 