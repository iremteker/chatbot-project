import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from chatbot.tools.weather.weather_tool import get_weather
from chatbot.tools.register.register_tool import register_user
from chatbot.tools.weather.data import CITY_COORDINATES


class OrchestratorAgent:
    """
    LLM-first Orchestrator Agent
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

        # REGISTER STATE
        self.register_state = {
            "active": False,
            "step": 0,
            "data": {
                "ad": None,
                "soyad": None,
                "okul_no": None,
                "tc_no": None,
            },
        }

    # ==========================================================
    # INTENT CLASSIFICATION
    # ==========================================================
    def classify_intent(self, message: str) -> str:
        if not self.client:
            return "chat"

        prompt = f"""
        Kullanıcı mesajını SADECE şu kategorilerden BİRİNE ayır:

        - register
        - weather
        - chat
        - support

        Kurallar:
        - Sadece kategori adını döndür
        - Açıklama yazma

        Mesaj:
        "{message}"
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You classify user intent."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip().lower()

    # ==========================================================
    # WEATHER
    # ==========================================================
    def extract_city_llm(self, message: str):
        supported = list(CITY_COORDINATES.keys())

        if not self.client:
            msg = message.lower()
            for city in supported:
                if city in msg:
                    return city
            return None

        prompt = f"""
        Kullanıcı mesajından şehir adını çıkar.

        Sadece şu şehirlerden birini döndürebilirsin:
        {supported}

        Kurallar:
        - Tek kelime döndür
        - Listede yoksa NONE döndür

        Mesaj:
        "{message}"
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract city names."},
                {"role": "user", "content": prompt},
            ],
        )

        city = response.choices[0].message.content.strip().lower()
        if city == "none":
            return None
        return city if city in CITY_COORDINATES else None

    def handle_weather(self, message: str):
        city = self.extract_city_llm(message)

        if not city:
            return {
                "error": "Mesajdan desteklenen bir şehir çıkaramadım.",
                "supported_cities": list(CITY_COORDINATES.keys()),
            }

        weather_data = get_weather(city)

        if isinstance(weather_data, dict) and weather_data.get("error"):
            return weather_data

        if not self.client:
            return weather_data

        prompt = f"""
        Şehir: {city}
        Hava durumu verisi: {weather_data}

        Bu bilgiyi kullanıcıya kısa ve doğal Türkçe ile açıkla.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You explain weather in Turkish."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip()

    # ==========================================================
    # REGISTER
    # ==========================================================
    def start_register_flow(self):
        self.register_state["active"] = True
        self.register_state["step"] = 1
        return self.generate_register_question()

    def handle_register_step(self, message: str):
        step = self.register_state["step"]
        data = self.register_state["data"]

        if step == 1:
            data["ad"] = message
            self.register_state["step"] = 2
            return self.generate_register_question()

        if step == 2:
            data["soyad"] = message
            self.register_state["step"] = 3
            return self.generate_register_question()

        if step == 3:
            data["okul_no"] = message
            self.register_state["step"] = 4
            return self.generate_register_question()

        if step == 4:
            data["tc_no"] = message

        response = register_user(
            data["ad"], data["soyad"], data["okul_no"], data["tc_no"]
        )

        self.reset_register_flow()
        return f"Kayıt tamamlandı: {response}"

    def generate_register_question(self):
        step = self.register_state["step"]

        fields = {
            1: ("ad", "Kayıt için önce adınızı yazar mısınız?"),
            2: ("soyad", "Teşekkürler. Soyadınızı yazar mısınız?"),
            3: ("okul_no", "Okul numaranızı paylaşır mısınız?"),
            4: ("tc_no", "Son olarak TC kimlik numaranızı yazar mısınız?"),
        }

        field, fallback = fields.get(step, (None, ""))

        if not self.client or not field:
            return fallback

        prompt = f"""
        Kullanıcıdan SADECE şu alanı iste: {field}

        Kurallar:
        - Başka alan sorma
        - Tek cümle
        - Kibar Türkçe

        Örnek ton:
        "{fallback}"
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You ask for one registration field."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip()

    def reset_register_flow(self):
        self.register_state = {
            "active": False,
            "step": 0,
            "data": {
                "ad": None,
                "soyad": None,
                "okul_no": None,
                "tc_no": None,
            },
        }

    # ==========================================================
    # SUPPORT & CHAT
    # ==========================================================
    def handle_support(self, message: str):
        if not self.client:
            return "Destek şu anda kullanılamıyor."

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful support assistant."},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content

    def chat(self, message: str):
        if not self.client:
            return "LLM etkin değil."

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
        )
        return response.choices[0].message.content

    # ==========================================================
    # MAIN LOOP
    # ==========================================================
    def run(self, message: str):
        # Register aktifse
        if self.register_state["active"]:
            intent = self.classify_intent(message)

            if any(k in message.lower() for k in ["iptal", "vazgeç", "cancel"]):
                self.reset_register_flow()
                return "Kayıt akışını iptal ettim. Nasıl yardımcı olabilirim?"

            if intent != "register":
                return (
                    "Şu an kayıt akışındayız. "
                    "Devam etmek için istenen bilgiyi gir veya çıkmak için 'iptal' yaz."
                )

            return self.handle_register_step(message)

        intent = self.classify_intent(message)

        if intent == "weather":
            return self.handle_weather(message)

        if intent == "register":
            return self.start_register_flow()

        if intent == "support":
            return self.handle_support(message)

        return self.chat(message)
