import requests
import os
from datetime import datetime

# 환경 변수에서 가져오기
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

def get_weather():
    city = "Seoul"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    
    response = requests.get(url)
    data = response.json()
    
    # 에러 확인
    if 'main' not in data:
        error_msg = f"날씨 API 에러: {data}"
        print(error_msg)
        send_telegram(f"❌ 에러 발생:\n{error_msg}")
        return None
    
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    desc = data['weather'][0]['description']
    humidity = data['main']['humidity']
    
    message = f"""
🌤 오늘의 서울 날씨 ({datetime.now().strftime('%Y-%m-%d')})

날씨: {desc}
기온: {temp}°C
체감온도: {feels_like}°C
습도: {humidity}%
"""
    return message

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    print(f"텔레그램 응답: {response.json()}")

if __name__ == "__main__":
    print(f"API 키 확인: {WEATHER_API_KEY[:10]}..." if WEATHER_API_KEY else "API 키 없음")
    weather = get_weather()
    if weather:
        send_telegram(weather)
        print("날씨 전송 완료!")
    else:
        print("날씨 가져오기 실패")
