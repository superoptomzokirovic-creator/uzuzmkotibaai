import random

class SecretaryPersona:
    """
    Bobur Zokirovichga murojaat qiluvchi va har safar yangi qiz bola ismini ishlatuvchi
    sun'iy intellekt kotiba personasi.
    """

    SECRETARY_NAMES = [
        "Malika", "Zuxra", "Madina", "Sevara", "Jasmina",
        "Dilnura", "Shahzoda", "Robiya", "Farangiz", "Sabina",
        "Nozima", "Kumush", "Gulyora", "Ozoda", "Sitora"
    ]

    @classmethod
    def get_greeting(cls) -> str:
        name = random.choice(cls.SECRETARY_NAMES)
        return (
            f"🤖 *Kotiba {name}:* Assalomu alaykum, Bobur Zokirovich! "
            f"Buyrug'ingiz bajarildi, barcha ma'lumotlar tahlil qilindi."
        )

    @classmethod
    def get_ai_disclaimer(cls) -> str:
        name = random.choice(cls.SECRETARY_NAMES)
        return (
            f"⚠️ **Diqqat (Kotiba {name}ning AI maslahati):**\n"
            f"Ushbu matn/ma'lumot sun'iy intellekt tomonidan shakllantirildi. "
            f"Bobur Zokirovich, Uzum Seller'ga joylashdan oldin uni ko'zdan kechirib chiqsangiz yaxshi bo'lardi!"
        )
