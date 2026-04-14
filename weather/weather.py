import os
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Default coordinates - can be overridden via environment variables
DEFAULT_LAT = os.environ.get("DEFAULT_LAT", 42.8169)
DEFAULT_LON = os.environ.get("DEFAULT_LON", -1.6432)


def get_weather_report(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> str:
    """Get the current weather report for a specific location.
    
    Args:
        lat: Latitude of the location (default: 42.8169)
        lon: Longitude of the location (default: -1.6432)
        
    Returns:
        Formatted weather report string
        
    Raises:
        RuntimeError: If API request fails
    """
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", 
                  "apparent_temperature_min", "precipitation_sum", "precipitation_hours", 
                  "precipitation_probability_max"],
        "forecast_days": 1
    }
    
    try:
        responses = openmeteo.weather_api(url, params=params)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch weather data: {e}")

    # Process first location. Add a for-loop for multiple locations or weather models
    try:
        response = responses[0]
    except IndexError:
        raise RuntimeError("No weather data returned from API")

    # Current values. The order of variables needs to be the same as requested.
    try:
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
    except (IndexError, AttributeError) as e:
        raise RuntimeError(f"Failed to parse current weather data: {e}")

    # Process daily data. The order of variables needs to be the same as requested.
    try:
        daily = response.Daily()
        current_temperature = int(current_temperature_2m)
        daily_temperature_2m_max = int(daily.Variables(0).ValuesAsNumpy()[0])
        daily_temperature_2m_min = int(daily.Variables(1).ValuesAsNumpy()[0])
        daily_apparent_temperature_max = int(daily.Variables(2).ValuesAsNumpy()[0])
        daily_apparent_temperature_min = int(daily.Variables(3).ValuesAsNumpy()[0])
        daily_precipitation_sum = int(daily.Variables(4).ValuesAsNumpy()[0])
        daily_precipitation_hours = int(daily.Variables(5).ValuesAsNumpy()[0])
        daily_precipitation_probability_max = int(daily.Variables(6).ValuesAsNumpy()[0])
    except (IndexError, AttributeError) as e:
        raise RuntimeError(f"Failed to parse daily weather data: {e}")

    return(f"La temperatura actual es {current_temperature} grados.  La máxima del día será de {daily_temperature_2m_max} y la mínima de {daily_temperature_2m_min} grados. La sensación térmica será de {daily_apparent_temperature_max} de máxima y de {daily_apparent_temperature_min} de mínima. La probabilidad de lluvia es del {daily_precipitation_probability_max}%")


if __name__ == "__main__":
    print(get_weather_report())
