import requests

def register_user(ad: str, soyad: str, okul_no: str, tc_no: str) -> dict:
    """
    Kullanıcı bilgilerini Flask backend'e POST isteği ile gönderir.
    Backend başarılıysa success=True, hata varsa success=False döner.
    """

    url= "http://127.0.0.1:5001/register"

    payload = {
        "ad": ad,
        "soyad": soyad,
        "okul_no": okul_no,
        "tc_no": tc_no
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": data.get("message", "Kayıt başarılı.")
            }
        
        else:
            data = response.json()
            return {
                "success": False,
                "message": data.get("error", "Kayıt başarısız oldu.")
            }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API isteği başarısız oldu: {str(e)}"
        }