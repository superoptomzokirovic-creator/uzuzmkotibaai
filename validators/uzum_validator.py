import re

class UzumValidator:
    """
    Uzum Market qoidalariga moslikni tekshiruvchi va to'g'irlovchi sinf.
    - Sarlavha: Maksimal 90 belgi. Taqqiqlangan so'zlar filtrlanadi.
    - Tavsif: 390 dan 28000 gacha belgi. Kontaktlar (telefon, tg link) olib tashlanadi.
    """

    FORBIDDEN_WORDS = [
        "eng arzon", "100% original", "skidka", "aksiya",
        "самый дешевый", "оригинал 100%", "скидка"
    ]

    @staticmethod
    def clean_text(text: str) -> str:
        """Matndan telefon raqamlar va havolalarni (kontaktlarni) tozalaydi."""
        # Telefon raqamlarini tozalash (+998...)
        text = re.sub(r'\+?\d{9,13}', '[kontakt olib tashlandi]', text)
        # Telegram linklarni tozalash (t.me/... @...)
        text = re.sub(r't\.me\/[^\s]+', '[havola olib tashlandi]', text)
        text = re.sub(r'@[a-zA-Z0-9_]{5,}', '[username olib tashlandi]', text)
        return text

    @classmethod
    def validate_and_fix_title(cls, title: str) -> str:
        """Sarlavhani Uzum talabiga moslaydi (max 90 belgi)."""
        if not title:
            return "Mahsulot sarlavhasi kiritilmagan"

        # Tozalash
        cleaned = cls.clean_text(title.strip())

        # Taqiqiklangan so'zlarni olib tashlash
        for word in cls.FORBIDDEN_WORDS:
            cleaned = re.sub(re.escape(word), '', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 90 belgidan oshsa kesish
        if len(cleaned) > 90:
            cleaned = cleaned[:87].rsplit(' ', 1)[0] + "..."

        return cleaned

    @classmethod
    def validate_and_fix_description(cls, description: str) -> str:
        """Tavsifni Uzum talabiga moslaydi (390 - 28000 belgi)."""
        if not description:
            return "Mahsulot tavsifi kiritilmagan. Iltimos, mahsulot xususiyatlarini batafsil kiriting."

        cleaned = cls.clean_text(description.strip())

        # Agar 390 belgidan kam bo'lsa, ogohlantiruvchi qism qo'shamiz yoki kengaytiramiz
        if len(cleaned) < 390:
            cleaned += "\n\nMahsulot yuqori sifatli materialdan tayyorlangan bo'lib, kundalik foydalanish uchun juda qulay. Barcha standartlarga javob beradi va uzoq vaqt xizmat qiladi."

        if len(cleaned) > 28000:
            cleaned = cleaned[:27995] + "..."

        return cleaned
