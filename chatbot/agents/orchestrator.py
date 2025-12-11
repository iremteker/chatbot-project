import os
from openai import OpenAI

from chatbot.tools.weather.weather_tool import get_weather
from chatbot.tools.register.register_tool import register_user


class OrchestratorAgent:
    """
    Basit düzeyde bir orcestrator ajanı.
    Görevleri:
    - Kullanıcı mesajını analiz etmek
    - Hangi tool'un kullanılacağını belirlemek (weather/register/none)
    - Gerekirse LLM'den normal chat yanıtı almak
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None



    def route(self, message: str):
        msg = message.lower()

        if any(k in msg for k in ["hava", "sıcaklık", "rüzgar", "hava durumu"]):
            return "weather"
        
        if any(k in msg for k in ["kayıt", "üye", "tc", "okul", "ad", "soyad"]):
            return "register"
        
        return "chat"
    


    def call_weather_tool(self, message: str):
        return get_weather(message)
    

    def call_register_tool(self, ad, soyad, okul_no, tc_no):
        return register_user(ad, soyad, okul_no, tc_no)
    

    def chat(self, message: str):
        if not self.client:
            return "LLM etkin değil. Şu an sadece tool fonksiyonları kullanılabilir."
        
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message["content"]
    


    def run(self, message: str):
        route = self.route(message)

        if route == "weather":
            return self.call_weather_tool(message)
        
        if route == "register":
            return {
                "info": "Kayıt akışı başlatıldı. Gerekli bilgileri adım adım almalıyız"
            }
        
        else:
            return self.chat(message)
