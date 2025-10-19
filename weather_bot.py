import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_weather():
    """오전 7시에 오늘 하루 날씨 정보"""
    try:
        # 서울 좌표
        lat, lon = 37.5665, 126.9780
        
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
            'hourly': 'temperature_2m,precipitation_probability,weather_code,precipitation',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset',
            'timezone': 'Asia/Seoul',
            'forecast_days': 1
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # 날씨 코드 한글 변환
        weather_codes = {
            0: '☀️ 맑음', 1: '🌤 대체로 맑음', 2: '⛅️ 구름 조금', 3: '☁️ 흐림',
            45: '🌫 안개', 48: '🌫 안개',
            51: '🌦 이슬비', 53: '🌦 이슬비', 55: '🌧 이슬비',
            61: '🌧 비', 63: '🌧 비', 65: '🌧 강한 비',
            71: '🌨 눈', 73: '❄️ 눈', 75: '❄️ 폭설',
            80: '🌦 소나기', 81: '🌦 소나기', 82: '⛈ 강한 소나기',
            95: '⛈ 뇌우', 96: '⛈ 우박', 99: '⛈ 우박'
        }
        
        # 현재 날씨
        current = data['current']
        temp_now = current['temperature_2m']
        feels = current['apparent_temperature']
        humidity = current['relative_humidity_2m']
        wind = current['wind_speed_10m']
        weather_now = weather_codes.get(current['weather_code'], '알 수 없음')
        
        # 오늘의 최고/최저 기온
        daily = data['daily']
        temp_max = daily['temperature_2m_max'][0]
        temp_min = daily['temperature_2m_min'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        rain_sum = daily['precipitation_sum'][0]
        
        # 일출/일몰
        sunrise = datetime.fromisoformat(daily['sunrise'][0]).strftime('%H:%M')
        sunset = datetime.fromisoformat(daily['sunset'][0]).strftime('%H:%M')
        
        # 메시지 시작
        today = datetime.now().strftime('%Y년 %m월 %d일 (%A)')
        
        message = f"""🌤 오늘의 서울 날씨
{today}

━━━━━━━━━━━━━━━
📍 현재 (오전 7시 기준)
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
        
        # 오늘 시간대별 (오전 7시부터 24시간)
        hourly = data['hourly']
        current_hour = datetime.now().hour
        
        for i in range(len(hourly['time'])):
            time_str = datetime.fromisoformat(hourly['time'][i])
            hour = time_str.hour
            
            # 현재 시간 이후만 표시
            if hour >= current_hour:
                time_display = time_str.strftime('%H시')
                temp_h = hourly['temperature_2m'][i]
                rain_h = hourly['precipitation_probability'][i]
                precip_h = hourly['precipitation'][i]
                weather_h = weather_codes.get(hourly['weather_code'][i], '')
                
                message += f"\n{time_display}: {temp_h}°C {weather_h}"
                
                if rain_h > 30:  # 30% 이상일 때만 표시
                    message += f" ☔️{rain_h}%"
                if precip_h > 0:
                    message += f" ({precip_h}mm)"
        
        message += "\n\n━━━━━━━━━━━━━━━"
        
        # 날씨에 따른 코멘트
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
