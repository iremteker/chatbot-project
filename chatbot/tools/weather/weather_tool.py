import requests
from .data import CITY_COORDINATES, WEATHER_CODES
from .utils import normalize_city


def get_weather(city: str) -> dict:
    """
    Verilen şehir için hava durumu bilgisini Open-Meteo API'sinden çeker.
    Gelen veri: sıcaklık, rüzgar hızı ve açıklama (description).
    """

    normalized_city = normalize_city(city)

    if normalized_city not in CITY_COORDINATES:
        return {
            "error": f"'{city}' adlı şehir bulunamadı. Desteklenen şehirler: "
        }
    
    coords = CITY_COORDINATES[normalized_city]
    lat, lon = coords["lat"], coords["lon"]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "current_weather" not in data:
            return {"error": "Weather API beklenen formatta yanıt vermedi."}
        
        weather = data["current_weather"]

        temperature = weather.get("temperature")
        windspeed = weather.get("windspeed")
        weathercode = weather.get("weathercode")

        description = WEATHER_CODES.get(weathercode, "Bilinmeyen hava durumu")


        return {
            "temperature": temperature,
            "windspeed": windspeed,
            "description": description,
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": f"API isteği başarısız oldu: {str(e)}"}
    
    