import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_naver_weather():
    """네이버 날씨 가져오기"""
    try:
        # 네이버 날씨 페이지 (서울 기준)
        url = "https://search.naver.com/search.naver?query=날씨"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 현재 날씨 정보
        location = soup.select_one('.title_area._area_panel h2.title').text.strip()
        current_temp = soup.select_one('.temperature_text strong').text.strip()
        
        # 날씨 상태
        weather_state = soup.select_one('.weather.before_slash').text.strip()
        
        # 미세먼지
        dust_info = soup.select('.today_chart_list li')
        dust_text = ""
        for dust in dust_info:
            dust_text += dust.text.strip() + "\n"
        
        # 시간대별 날씨 (오늘)
        hourly = soup.select('.hourly_box._hourly_weather .item_time')
        hourly_text = "\n⏰ 시간대별 날씨:\n"
        
        for i, hour in enumerate(hourly[:8]):  # 8시간치만
            time = hour.select_one('.time').text.strip()
            temp = hour.select_one('.temperature').text.strip()
            weather = hour.select_one('.weather_icon').get('alt', '')
            rain = hour.select_one('.rainfall')
            rain_text = rain.text.strip() if rain else ""
            
            hourly_text += f"\n{time} | {temp} | {weather}"
            if rain_text and rain_text != "-":
                hourly_text += f" ({rain_text})"
        
        # 주간 날씨
        weekly = soup.select('.week_box .week_item')
        weekly_text = "\n\n📅 주간 날씨:\n"
        
        for day in weekly[:5]:  # 5일치
            date = day.select_one('.date').text.strip()
            day_name = day.select_one('.day').text.strip()
            weather = day.select_one('.weather_icon').get('alt', '')
            temp_high = day.select_one('.temperature.high').text.strip()
            temp_low = day.select_one('.temperature.low').text.strip()
            
            weekly_text += f"\n{date} ({day_name}) | {weather} | {temp_high}/{temp_low}"
        
        message = f"""🌤 {location} 날씨 ({datetime.now().strftime('%Y-%m-%d %H:%M')})

현재: {current_temp} | {weather_state}

{dust_text}
{hourly_text}
{weekly_text}

출처: 네이버 날씨
"""
        
        return message, None
        
    except Exception as e:
        return None, f"네이버 날씨 가져오기 실패: {str(e)}"

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
        send_telegram(f"❌ 에러:\n{error}")
        print(error)
    else:
        send_telegram(weather)
        print("날씨 전송 완료!")
