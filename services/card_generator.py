import json
import asyncio
from typing import Dict, Any, Optional
from config import GOOGLE_API_KEY, GROQ_API_KEY
from validators.uzum_validator import UzumValidator
from services.secretary import SecretaryPersona

class CardGeneratorService:
    """
    Rasm, tavsif va narx asosida Uzum talablariga mos kartochka yaratadi.
    Bepul va barqaror modellardan (Groq Llama 3, Google Gemini 1.5 Flash) foydalanadi.
    """

    @classmethod
    async def generate_images(cls, user_description: str, dalle_prompt: Optional[str] = None, count: int = 6) -> list:
        """
        DALL-E 3 o'rniga hozircha bepul image generation xizmati bo'lmagani uchun
        foydalanuvchi yuklagan rasmni o'zini qaytaradi (bepul variant).
        """
        # Hozircha bepul rasm generatsiyasi uchun OpenAI DALL-E 3 talab qilinadi.
        # Agar bepul kerak bo'lsa, bu yerda HUGGING FACE API (Stable Diffusion) ishlatishimiz kerak.
        return []

    @classmethod
    async def generate_card(cls, image_bytes: Optional[bytes], user_description: str, price: str) -> Dict[str, Any]:
        system_prompt = (
            "Siz Uzum Market uchun professional yordamchisiz. Quyidagi JSON formatda javob bering (faqat JSON):\n"
            '{"title_uz": "...", "title_ru": "...", "description_uz": "...", "description_ru": "...", '
            '"attributes": {"Rang": "...", "Material": "..."}, "category_suggestion": "...", "pricing_advice": "...", '
            '"dalle_prompt": "..."}'
        )
        user_content = f"Tavsif: {user_description}\nNarx: {price}"

        # 1. Groq (Llama-3-8b) - Bepul va juda tez
        try:
            return await cls._call_groq(system_prompt, user_content)
        except Exception as e:
            print(f"Groq xatoligi: {e}")

        # 2. Gemini (1.5 Flash) - Bepul
        try:
            return await cls._call_gemini(system_prompt, user_content)
        except Exception as e:
            print(f"Gemini xatoligi: {e}")

        return cls._fallback_card(user_description, price)

    @classmethod
    async def _call_groq(cls, system_prompt: str, user_content: str) -> Dict[str, Any]:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    @classmethod
    async def _call_gemini(cls, system_prompt: str, user_content: str) -> Dict[str, Any]:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(system_prompt + "\n" + user_content)
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())

    @classmethod
    def _fallback_card(cls, description: str, price: str) -> Dict[str, Any]:
        return {
            "title_uz": description[:70],
            "title_ru": description[:70],
            "description_uz": description,
            "description_ru": description,
            "attributes": {"Holati": "Yangi"},
            "category_suggestion": "Bozor",
            "pricing_advice": price,
            "dalle_prompt": description
        }
