import requests
import os
from datetime import datetime
import pytz

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
        
        # 한국 시간대로 현재 시간 가져오기
        kst = pytz.timezone('Asia/Seoul')
        now_kst = datetime.now(kst)
        today_kst = now_kst.date()
        
        print(f"현재 한국 시간: {now_kst}")
        print(f"현재 한국 날짜: {today_kst}")
        
        daily = data['daily']
        temp_max = daily['temperature_2m_max'][0]
        temp_min = daily['temperature_2m_min'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        rain_sum = daily['precipitation_sum'][0]
        
        sunrise = daily['sunrise'][0].split('T')[1]  # 시간만 추출
        sunset = daily['sunset'][0].split('T')[1]
        
        display_date = now_kst.strftime('%Y년 %m월 %d일 (%A)')
        
        message = f"""🌤 오늘의 서울 날씨
{display_date}

━━━━━━━━━━━━━━━
📍 현재 날씨
{weather_now}
🌡 기온: {temp_now}°C (체감 {feels}°C)
💧 습도: {humidity}%
💨 바람: {wind} km/h

━━━━━━━━━━━━━━━
📊 오늘 예상
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
        
        displayed_count = 0
        for i in range(len(hourly['time'])):
            # API는 이미 Asia/Seoul 기준으로 반환됨
            time_str = hourly['time'][i]  # 예: "2025-10-20T07:00"
            hour_date = time_str.split('T')[0]  # 날짜 부분
            hour_time = int(time_str.split('T')[1].split(':')[0])  # 시간 부분
            
            # 오늘 날짜인지 확인
            if hour_date == str(today_kst) and hour_time in target_hours:
                temp_h = hourly['temperature_2m'][i]
                rain_h = hourly['precipitation_probability'][i]
                precip_h = hourly['precipitation'][i]
                weather_h = weather_codes.get(hourly['weather_code'][i], '')
                
                message += f"\n{hour_time:02d}시: {temp_h}°C {weather_h}"
                
                if rain_h > 30:
                    message += f" ☔️{rain_h}%"
                if precip_h > 0:
                    message += f" ({precip_h}mm)"
                
                displayed_count += 1
        
        if displayed_count == 0:
            message += "\n(표시할 시간대가 없습니다)"
        
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
        import traceback
        error_detail = traceback.format_exc()
        return None, f"날씨 정보 가져오기 실패:\n{str(e)}\n{error_detail}"

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
