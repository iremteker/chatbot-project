import unicodedata

def normalize_city(city_name: str) -> str:
    """
    Şehir adındaki Türkçe karakterleri normalize eder ve lowercase yapar.
    """

    if not isinstance(city_name, str):
        return ""
    
    normalized = unicodedata.normalize('NFKD', city_name).encode('ASCII', 'ignore').decode('ASCII')

    return normalized.lower().strip()