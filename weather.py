from creds import OPENWEATHERMAP_API_KEY
from pyowm.owm import OWM
from pyowm.commons.exceptions import PyOWMError
import logging
from datetime import datetime
import zoneinfo

weather_icons = {
    '01d': 'wi-day-sunny',
    '02d': 'wi-day-cloudy',
    '03d': 'wi-cloud',
    '04d': 'wi-cloudy-windy',
    '09d': 'wi-showers',
    '10d': 'wi-rain',
    '11d': 'wi-thunderstorm',
    '13d': 'wi-snow',
    '50d': 'wi-fog',
    '01n': 'wi-night-clear',
    '02n': 'wi-night-cloudy',
    '03n': 'wi-night-cloudy',
    '04n': 'wi-night-cloudy',
    '09n': 'wi-night-showers',
    '10n': 'wi-night-rain',
    '11n': 'wi-night-thunderstorm',
    '13n': 'wi-night-snow',
    '50n': 'wi-night-alt-cloudy-windy'
}

def download_weather():
    logging.info("downloading weather from openweathermap")
    owm = OWM(OPENWEATHERMAP_API_KEY)
    try:
        mgr = owm.weather_manager()
        forecast = mgr.forecast_at_place("Edinburgh, GB", '3h', limit=10).forecast
    except PyOWMError as e:
        logging.error(f"General PyOWM error: {e}")

    logging.info("processing weather")
    weather_to_display = []
    for weather in forecast:
        time = datetime.fromtimestamp(weather.reference_time(), zoneinfo.ZoneInfo('Europe/London'))
        if time.time().hour >= 6: # If the forcast is before 6am, don't show it.
            weather_to_display.append({
                'time': time.strftime('%H:%M'),
                'temperature': str(int(round(weather.temperature(unit='celsius')['temp']))),
                'icon': weather_icons[weather.weather_icon_name],
            })

    return weather_to_display


if __name__ == "__main__":
    weather = download_weather()
    print(weather)

# import openmeteo_requests
# from openmeteo_sdk.Variable import Variable
# def open_meteo_get_weather():
#     om = openmeteo_requests.Client()
#     params = {
#         "latitude": 55.95,
#         "longitude": -3.20,
#         "hourly": ["temperature_2m", "weather_code"],
#         "forecast_days": 1,
#     }
#     responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
#     response = responses[0]
#
#     hourly = response.Hourly()
#     print(hourly)
#     temps = hourly.Variables(0).ValuesAsNumpy()
#     weather_codes  = hourly.Variables(1).ValuesAsNumpy()
#     for r in zip(temps, weather_codes):
#         print(f"Temp: {r[0]}, Code: {r[1]},")
