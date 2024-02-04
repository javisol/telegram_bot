import openmeteo_requests

import requests_cache
#import pandas as pd
from retry_requests import retry

def get_weather_report():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 42.8169,
        "longitude": -1.6432,
        "current": "temperature_2m",
        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "precipitation_hours", "precipitation_probability_max"],
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = int(daily.Variables(0).ValuesAsNumpy()[0])
    daily_temperature_2m_min = int(daily.Variables(1).ValuesAsNumpy()[0])
    daily_apparent_temperature_max = int(daily.Variables(2).ValuesAsNumpy()[0])
    daily_apparent_temperature_min = int(daily.Variables(3).ValuesAsNumpy()[0])
    daily_precipitation_sum = int(daily.Variables(4).ValuesAsNumpy()[0])
    daily_precipitation_hours = int(daily.Variables(5).ValuesAsNumpy()[0])
    daily_precipitation_probability_max = int(daily.Variables(6).ValuesAsNumpy()[0])

    return(f"La temperatura actual es {current_temperature_2m} grados.  La máxima del día será de {daily_temperature_2m_max} y la mínima de {daily_temperature_2m_min} grados. La sensación térmica será de {daily_apparent_temperature_max} de máxima y de {daily_apparent_temperature_min} de mínima. La probabilidad de lluvia es de {daily_precipitation_probability_max}")


if __name__ == "__main__":
    print(get_weather_report())