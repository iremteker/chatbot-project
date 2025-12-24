from typing import TypedDict, Optional
from openai import OpenAI
import os


class RegisterState(TypedDict):
    step: str
    ad: Optional[str]
    soyad: Optional[str]
    okul_no: Optional[str]
    tc_no: Optional[str]


class RegisterGraph:
    """
    LangGraph mantığını SADECE soru üretimi için kullanır.
    Akış orchestrator kontrolündedir.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def ask_question(self, step: str) -> str:
        questions = {
            "ask_name": "Kayıt için adınızı yazar mısınız?",
            "ask_surname": "Soyadınızı yazar mısınız?",
            "ask_school_no": "Okul numaranızı yazar mısınız?",
            "ask_tc": "TC kimlik numaranızı yazar mısınız?",
        }

        fallback = questions.get(step, "Devam edebilir miyiz?")

        if not self.client:
            return fallback

        prompt = f"""
        Kullanıcıdan SADECE şu bilgiyi iste: {step}

        Kurallar:
        - Tek cümle
        - Kibar Türkçe
        - Başka bilgi isteme

        Örnek:
        "{fallback}"
        """

        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You ask for one registration field in Turkish."},
                {"role": "user", "content": prompt},
            ],
        )

        return resp.choices[0].message.content.strip()
