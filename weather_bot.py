import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_weather():
    """오늘 하루 날씨 정보"""
    try:
        lat, lon = 37.5665, 126.9780
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
            'hourly': 'temperature_2m,precipitation_probability,weather_code,precipitation',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset',
            'timezone': 'Asia/Seoul',
            'forecast_days': 2
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        weather_codes = {
            0: '☀️ 맑음', 1: '🌤 대체로 맑음', 2: '⛅️ 구름 조금', 3: '☁️ 흐림',
            45: '🌫 안개', 48: '🌫 안개',
            51: '🌦 이슬비', 53: '🌦 이슬비', 55: '🌧 이슬비',
            61: '🌧 비', 63: '🌧 비', 65: '🌧 강한 비',
            71: '🌨 눈', 73: '❄️ 눈', 75: '❄️ 폭설',
            80: '🌦 소나기', 81: '🌦 소나기', 82: '⛈ 강한 소나기',
            95: '⛈ 뇌우', 96: '⛈ 우박', 99: '⛈ 우박'
        }
        
        current = data['current']
        temp_now = current['temperature_2m']
        feels = current['apparent_temperature']
        humidity = current['relative_humidity_2m']
        wind = current['wind_speed_10m']
        weather_now = weather_codes.get(current['weather_code'], '알 수 없음')
        
        # 현재 시간 확인
        now = datetime.now()
        current_hour = now.hour
        
        # 오전 7시 이전이면 오늘(0), 이후면 내일(1) 날씨 표시
        day_index = 0 if current_hour < 7 else 0
        day_label = "오늘"
        
        daily = data['daily']
        temp_max = daily['temperature_2m_max'][day_index]
        temp_min = daily['temperature_2m_min'][day_index]
        rain_prob = daily['precipitation_probability_max'][day_index]
        rain_sum = daily['precipitation_sum'][day_index]
        
        sunrise = datetime.fromisoformat(daily['sunrise'][day_index]).strftime('%H:%M')
        sunset = datetime.fromisoformat(daily['sunset'][day_index]).strftime('%H:%M')
        
        # 표시할 날짜
        if day_index == 0:
            display_date = now.strftime('%Y년 %m월 %d일 (%A)')
        else:
            from datetime import timedelta
            tomorrow = now + timedelta(days=1)
            display_date = tomorrow.strftime('%Y년 %m월 %d일 (%A)')
        
        message = f"""🌤 {day_label}의 서울 날씨
{display_date}

━━━━━━━━━━━━━━━
📍 현재 날씨
{weather_now}
🌡 기온: {temp_now}°C (체감 {feels}°C)
💧 습도: {humidity}%
💨 바람: {wind} km/h

━━━━━━━━━━━━━━━
📊 {day_label} 예상
🔺 최고: {temp_max}°C
🔻 최저: {temp_min}°C
☔️ 강수확률: {rain_prob}%"""

        if rain_sum > 0:
            message += f"\n🌧 예상 강수량: {rain_sum}mm"
        
        message += f"""

🌅 일출: {sunrise}
🌆 일몰: {sunset}

━━━━━━━━━━━━━━━
⏰ 시간대별 날씨 (3시간 간격)
"""
        
        # 시간대별 날씨
        hourly = data['hourly']
        target_hours = [7, 10, 13, 16, 19, 22]
        
        # 오늘 날짜 구하기
        target_date = now.date()
        
        displayed_count = 0
        for i in range(len(hourly['time'])):
            time_str = datetime.fromisoformat(hourly['time'][i])
            
            # 오늘 날짜의 시간대만 표시
            if time_str.date() == target_date and time_str.hour in target_hours:
                time_display = time_str.strftime('%H시')
                temp_h = hourly['temperature_2m'][i]
                rain_h = hourly['precipitation_probability'][i]
                precip_h = hourly['precipitation'][i]
                weather_h = weather_codes.get(hourly['weather_code'][i], '')
                
                message += f"\n{time_display}: {temp_h}°C {weather_h}"
                
                if rain_h > 30:
                    message += f" ☔️{rain_h}%"
                if precip_h > 0:
                    message += f" ({precip_h}mm)"
                
                displayed_count += 1
        
        # 만약 표시된 시간대가 없으면 (저녁에 실행한 경우)
        if displayed_count == 0:
            message += "\n(오늘의 예보 시간대가 지나갔습니다)"
        
        message += "\n\n━━━━━━━━━━━━━━━"
        
        if rain_prob > 70:
            message += "\n☂️ 우산 꼭 챙기세요!"
        elif rain_prob > 30:
            message += "\n🌂 우산을 준비하는 게 좋겠어요"
        
        if temp_max > 28:
            message += "\n🥵 더운 날씨! 수분 섭취 충분히 하세요"
        elif temp_min < 5:
            message += "\n🥶 추운 날씨! 따뜻하게 입으세요"
        
        if wind > 30:
            message += "\n💨 바람이 강해요!"
        
        return message, None
        
    except Exception as e:
        return None, f"날씨 정보 가져오기 실패: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    weather, error = get_weather()
    
    if error:
        send_telegram(f"❌ {error}")
        print(error)
    else:
        send_telegram(weather)
        print("날씨 전송 완료!")
