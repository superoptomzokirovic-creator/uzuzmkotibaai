import json
import base64
from typing import Dict, Any, Optional
from config import GOOGLE_API_KEY, GROQ_API_KEY, OPENAI_API_KEY
from validators.uzum_validator import UzumValidator
from services.secretary import SecretaryPersona

class CardGeneratorService:
    """
    Rasm, tavsif va narx asosida Uzum talablariga mos kartochka ma'lumotlarini yaratadi.
    OpenAI (GPT-4o), Google Gemini yoki Groq orqali navbatma-navbat ishlaydi.
    """

    @classmethod
    async def generate_card(cls, image_bytes: Optional[bytes], user_description: str, price: str) -> Dict[str, Any]:
        system_prompt = (
            "Siz Uzum Market (O'zbekiston) platformasi uchun professional seller yordamchisisiz. "
            "Sizga tovar rasmi (agar bo'lsa), foydalanuvchining qisqa tavsifi va narxi beriladi. "
            "Siz Uzum Market talablariga to'liq mos keluvchi quyidagi formatda JSON obyektini qaytarishingiz shart (faqat JSON, boshqa matn yozmang!):\n"
            "{\n"
            '  "title_uz": "Maksimal 90 belgili o\'zbekcha SEO sarlavha (Brend + Nomi + Asosiy xususiyati)",\n'
            '  "title_ru": "Maksimal 90 belgili ruscha SEO sarlavha",\n'
            '  "description_uz": "Kamida 400 belgili, xaridorlarni jalb qiluvchi, afzalliklari, o\'lchamlari va xususiyatlari yoritilgan to\'liq o\'zbekcha tavsif (emojilar bilan)",\n'
            '  "description_ru": "Ruscha to\'liq tavsif",\n'
            '  "attributes": {\n'
            '      "Rang": "...",\n'
            '      "Material": "...",\n'
            '      "Mavsum": "...",\n'
            '      "Ishlab chiqarilgan mamlakat": "Xitoy",\n'
            '      "O\'lchami": "Standard"\n'
            '  },\n'
            '  "category_suggestion": "Tavsiya etiladigan Uzum kategoriyasi",\n'
            '  "pricing_advice": "Narx bo\'yicha qisqa tavsiya"\n'
            "}\n"
            "Muhim qoidalar:\n"
            "1. JSON formatdan boshqa hech qanday tushuntirish yozmang.\n"
            "2. Telefon raqamlari, telegram linklar yozish mutlaqo taqiqlangan.\n"
            "3. O'zbekcha va ruscha sifatli, xatosiz bo'lsin."
        )

        user_content = f"Foydalanuvchi tavsifi: {user_description}\nSotuv narxi: {price}"

        result = None

        # 1. OpenAI (GPT-4o) orqali urinib ko'ramiz (Vision + Text eng yuqori sifat)
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
            try:
                result = await cls._call_openai(image_bytes, system_prompt, user_content)
            except Exception as e:
                print(f"OpenAI API xatoligi: {e}")

        # 2. Google Gemini orqali urinib ko'ramiz
        if not result and GOOGLE_API_KEY and GOOGLE_API_KEY != "AIzaSyB0wZ-XyS465n7r":
            try:
                result = await cls._call_gemini(image_bytes, system_prompt, user_content)
            except Exception as e:
                print(f"Gemini API xatoligi: {e}")

        # 3. Groq orqali urinib ko'ramiz
        if not result and GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"):
            try:
                result = await cls._call_groq(system_prompt, user_content)
            except Exception as e:
                print(f"Groq API xatoligi: {e}")

        # 4. Agar hech biri ishlamasa, fallback shablon
        if not result:
            result = cls._fallback_card(user_description, price)

        # Uzum qat'iy validatorlaridan o'tkazish
        result["title_uz"] = UzumValidator.validate_and_fix_title(result.get("title_uz", ""))
        result["title_ru"] = UzumValidator.validate_and_fix_title(result.get("title_ru", ""))
        result["description_uz"] = UzumValidator.validate_and_fix_description(result.get("description_uz", ""))
        result["description_ru"] = UzumValidator.validate_and_fix_description(result.get("description_ru", ""))
        result["disclaimer"] = SecretaryPersona.get_ai_disclaimer()

        return result

    @classmethod
    async def _call_openai(cls, image_bytes: Optional[bytes], system_prompt: str, user_content: str) -> Dict[str, Any]:
        import httpx
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": system_prompt}]
        user_msg_content = []
        if image_bytes:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            user_msg_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
            })
        user_msg_content.append({"type": "text", "text": user_content})
        messages.append({"role": "user", "content": user_msg_content})

        body = {
            "model": "gpt-4o",
            "response_format": {"type": "json_object"},
            "messages": messages
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return json.loads(text)
            else:
                raise Exception(f"OpenAI error status: {resp.status_code}, {resp.text}")

    @classmethod
    async def _call_gemini(cls, image_bytes: Optional[bytes], system_prompt: str, user_content: str) -> Dict[str, Any]:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)

        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        contents = [user_content]
        if image_bytes:
            contents.append({'mime_type': 'image/jpeg', 'data': image_bytes})

        response = model.generate_content(contents)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    @classmethod
    async def _call_groq(cls, system_prompt: str, user_content: str) -> Dict[str, Any]:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    @classmethod
    def _fallback_card(cls, description: str, price: str) -> Dict[str, Any]:
        clean_desc = description.strip()
        title = f"{clean_desc[:70]}" if clean_desc else "Mahsulot"
        return {
            "title_uz": title,
            "title_ru": title,
            "description_uz": (
                f"Sifatli va qulay mahsulot: {clean_desc}.\n\n"
                "Asosiy afzalliklari:\n"
                "• Yuqori sifatli va chidamli materiallardan tayyorlangan\n"
                "• Foydalanish uchun juda qulay va zamonaviy dizayn\n"
                "• Kundalik ehtiyojlar uchun ajoyib tanlov\n\n"
                "Ushbu tovar o'zining mustahkamligi va uzoq vaqt xizmat qilishi bilan ajralib turadi. "
                "Barcha sifat standartlariga to'liq javob beradi."
            ),
            "description_ru": (
                f"Качественный и надежный товар: {clean_desc}.\n\n"
                "Преимущества:\n"
                "• Изготовлен из качественных и долговечных материалов\n"
                "• Удобный и современный дизайн\n"
                "• Отличный выбор на каждый день"
            ),
            "attributes": {
                "Ishlab chiqaruvchi": "Xitoy",
                "Holati": "Yangi",
                "Kafolat": "Tekshirish uchun 14 kun"
            },
            "category_suggestion": "Bozor / Umumiy",
            "pricing_advice": f"Belgilangan narx: {price}. Uzum komissiyasini inobatga oling."
        }
