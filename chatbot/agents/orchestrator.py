import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from chatbot.tools.weather.weather_tool import get_weather
from chatbot.tools.register.register_tool import register_user
from chatbot.tools.weather.data import CITY_COORDINATES
from chatbot.agents.register_graph import RegisterGraph


class OrchestratorAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

        # REGISTER STATE
        self.register_active = False
        self.register_graph = RegisterGraph()
        self.register_state = {
            "step": "ask_name",
            "ad": None,
            "soyad": None,
            "okul_no": None,
            "tc_no": None,
        }


    def llm_route(self, message: str) -> dict:
        """
        LLM decides intent.
        NO keyword routing.
        """

        prompt = f"""
        Kullanıcı mesajını analiz et.

        Intent kategorilerinden SADECE birini seç:
        - register → kullanıcı KAYIT OLMAK İSTİYORSA
  (örn: "kayıt olmak istiyorum", "beni kaydet")

        - weather → hava durumu soruyorsa

        - date → bugünün tarihi / gün soruyorsa

        - chat → genel bilgi, açıklama, soru
        (örn: "kayıt işlemini ne için yapıyoruz?")

        - support → yardım / destek soruları

        Kurallar:
        - Bilgi alma amaçlı sorular ASLA register değildir
        - Cevabı JSON döndür
        - Açıklama yazma

        JSON formatı:
        {{
          "intent": "..."
        }}

        Mesaj:
        "{message}"
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an intent router."},
                {"role": "user", "content": prompt},
            ],
        )

        return json.loads(response.choices[0].message.content)


    def handle_weather(self, message: str):
        city = None
        for c in CITY_COORDINATES:
            if c in message.lower():
                city = c
                break

        if not city:
            return "Mesajdan şehir bilgisi çıkaramadım."

        weather_data = get_weather(city)

        # Tool çıktısını LLM'e açıklattır
        prompt = f"""
        Şehir: {city}
        Hava durumu verisi: {weather_data}

        Kullanıcıya kısa ve doğal Türkçe ile açıkla.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content


    def start_register(self):
        self.register_active = True
        self.register_state = {
            "step": "ask_name",
            "ad": None,
            "soyad": None,
            "okul_no": None,
            "tc_no": None,
        }
        return self.register_graph.ask_question("ask_name")

    def handle_register(self, message: str):
        step = self.register_state["step"]
        text = (message or "").strip()

        def only_digits(s: str) -> bool:
            return s.isdigit()
        

        if step == "ask_name":
            if not text:
                return "Ad alanı boş bırakılamaz. Lütfen adınızı girin."
            self.register_state["ad"] = text
            self.register_state["step"] = "ask_surname"
            return self.register_graph.ask_question("ask_surname")

        if step == "ask_surname":
            if not text:
                return "Soyad alanı boş bırakılamaz. Lütfen soyadınızı girin."
            self.register_state["soyad"] = text
            self.register_state["step"] = "ask_school_no"
            return self.register_graph.ask_question("ask_school_no")

        if step == "ask_school_no":
            if not only_digits(text):
                return "Okul numarası sadece rakamlardan oluşmalıdır. Lütfen geçerli bir okul numarası girin."
            self.register_state["okul_no"] = int(text)
            self.register_state["step"] = "ask_tc"
            return self.register_graph.ask_question("ask_tc")

        if step == "ask_tc":
            if not only_digits(text):
                return "TC kimlik numarası sadece rakamlardan oluşmalıdır. Lütfen geçerli bir TC kimlik numarası girin."
            if len(text) != 11:
                return "TC kimlik numarası 11 haneli olmalıdır. Lütfen geçerli bir TC kimlik numarası girin."
            self.register_state["tc_no"] = int(text)

        # Submit
            response = register_user(
                self.register_state["ad"],
                self.register_state["soyad"],
                str(self.register_state["okul_no"]),
                str(self.register_state["tc_no"]),
            )
            self.register_active = False
            return f"Kayıt tamamlandı: {response}"

        return self.register_graph.ask_question(self.register_state["step"])


    def chat(self, message: str):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
        )
        return response.choices[0].message.content


    def run(self, message: str):
        # Register aktifse LLM router'a SORMA
        if self.register_active:
            desicion = self.llm_route(message)
            if desicion["intent"] == "register":
                return self.chat(message)
            return self.handle_register(message)

        # LLM routing
        decision = self.llm_route(message)
        intent = decision["intent"]

        if intent == "register":
            return self.start_register()

        if intent == "weather":
            return self.handle_weather(message)

        if intent == "date":
            today = datetime.now().strftime("%d %B %Y")
            return f"Bugünün tarihi {today}."

        if intent == "support":
            return "Destek için lütfen e-posta ile iletişime geçin."

        # chat
        return self.chat(message)
