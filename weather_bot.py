import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_naver_weather():
    """네이버 날씨 가져오기 (간단 버전)"""
    try:
        url = "https://search.naver.com/search.naver?query=서울날씨"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        # BeautifulSoup 없이 간단하게 텍스트 파싱
        html = response.text
        
        # 현재 온도 찾기
        if '현재 온도' in html:
            temp_start = html.find('현재 온도')
            temp_section = html[temp_start:temp_start+200]
            
        # 간단한 방법: 정규표현식 사용
        import re
        
        # 온도 찾기 (예: 15°, 15도)
        temps = re.findall(r'(\d+)°', html)
        
        if temps:
            current_temp = temps[0]
            message = f"""🌤 서울 날씨 ({datetime.now().strftime('%Y-%m-%d %H:%M')})

현재 기온: {current_temp}°C

자세한 정보: https://search.naver.com/search.naver?query=서울날씨
"""
            return message, None
        else:
            return None, "온도 정보를 찾을 수 없습니다"
            
    except Exception as e:
        return None, f"에러: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    weather, error = get_naver_weather()
    
    if error:
        send_telegram(f"❌ {error}\n\n네이버 날씨: https://search.naver.com/search.naver?query=서울날씨")
        print(error)
    else:
        send_telegram(weather)
        print("날씨 전송 완료!")
