import os
import sys
from openai import OpenAI


from chatbot.tools.weather.weather_tool import get_weather
from chatbot.tools.register.register_tool import register_user
from chatbot.tools.weather.data import CITY_COORDINATES


class OrchestratorAgent:
    """
    Basit bir orchestrator agent.
    - Kullanıcı mesajını analiz eder
    - Weather / Register / Normal chat olarak ayırır
    """


    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

        # REGISTER STATE
        self.register_state = {
            "active": False,
            "step": 0,
            "data": {
                "ad": None,
                "soyad": None,
                "okul_no": None,
                "tc_no": None
            }
        }


    def extract_city(self, message: str):
        msg = message.lower()

        for city in CITY_COORDINATES.keys():
            if city in msg.replace("ı", "i").replace("İ", "i").replace("I", "i"):
                return city

        return None


    def route(self, message: str):
        msg = message.lower()

        if any(k in msg for k in ["hava", "sıcaklık", "rüzgar", "hava durumu"]):
            return "weather"

        if any(k in msg for k in ["kayıt", "üye", "tc", "okul", "adım", "soyad"]):
            return "register"

        return "chat"


    def call_weather_tool(self, message: str):
        city = self.extract_city(message)

        if not city:
            return {"error": "Mesaj içinde tanınan bir şehir bulunamadı. Örn: istanbul, ankara"}

        return get_weather(city)


    def call_register_tool(self, ad, soyad, okul_no, tc_no):
        return register_user(ad, soyad, okul_no, tc_no)
    
    def start_register_flow(self):
        self.register_state["active"] = True
        self.register_state["step"] = 1
        return "Kayıt akışı başlatıldı. Önce adınızı alabilir miyim?"
    
    def handle_register_step(self, message: str):
        step = self.register_state["step"]
        data = self.register_state["data"]

        if step == 1:
            data["ad"] = message
            self.register_state["step"] = 2
            return "Soyadınızı alabilir miyim?"
        
        if step == 2:
            data["soyad"] = message
            self.register_state["step"] = 3
            return "Okul numaranız nedir?"
        
        if step == 3:
            data["okul_no"] = message
            self.register_state["step"] = 4
            return "TC kimlik numaranız nedir?"
        
        if step == 4:
            data["tc_no"] = message
        
        response = register_user(
            data["ad"],
            data["soyad"],
            data["okul_no"],
            data["tc_no"]
        )

        self.reset_register_flow()
        
        return f"Kayıt tamamlandı: {response}"
    
    def reset_register_flow(self):
        self.register_state = {
            "active": False,
            "step": 0,
            "data": {
                "ad": None,
                "soyad": None,
                "okul_no": None,
                "tc_no": None
            }
        }


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

        if self.register_state["active"]:
            return self.handle_register_step(message)

        if route == "weather":
            return self.call_weather_tool(message)

        elif route == "register":
            return self.start_register_flow()

        else:
            return self.chat(message)
