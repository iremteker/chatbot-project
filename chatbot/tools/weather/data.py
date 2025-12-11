# Türkiye'deki bazı büyük şehirlerin koordinatları
# Kullanacağım API Open-Meteo şehir ismini değil, koordinatları kullandığı için bu veri kullanılıyor.
CITY_COORDINATES = {
    "istanbul": {"lat": 41.0082, "lon": 28.9784},
    "ankara": {"lat": 39.9208, "lon": 32.8541},
    "izmir": {"lat": 38.4237, "lon": 27.1428},
    "bursa": {"lat": 40.1950, "lon": 29.0600},
    "antalya": {"lat": 36.8969, "lon": 30.7133},
    "adana": {"lat": 36.9914, "lon": 35.3308},
}


WEATHER_CODES = {
    0: "Açık",
    1: "Genelde açık",
    2: "Parçalı bulutlu",
    3: "Bulutlu",
    45: "Sisli",
    48: "Buzlu sis",
    51: "Çiseleme",
    61: "Hafif yağmurlu",
    63: "Yağmurlu",
    65: "Şiddetli yağmur",
    71: "Kar yağışlı",
    80: "Hafif sağanak",
    95: "Gökgürültülü fırtına",
}