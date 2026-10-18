from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "✈️ Kargo tekshiruvi")
async def cmd_cargo_check(message: Message):
    text = (
        "✈️ **Xitoydan Kargo Xavfsizlik Tekshiruvi (Havo vs Avto)**\n\n"
        "Havo kargosida quyidagi tovarlarni tashish **QAT'IYAN TAQIQLANGAN**:\n"
        "1. 🔋 Batareya va akkumulyatorlar (Powerbank, telefon batareyalari)\n"
        "2. liq Suyuqliklar va kosmetika (Atir, shampun, gel)\n"
        "3. 🧲 Kuchli magnitlar va motorlar\n"
        "4. 🧨 Kukunsimon va portlovchi moddalar\n"
        "5. 🔪 O'tkir kesuvchi qurollar\n\n"
        "💡 *Agar tovaringizda yuqoridagilar bo'lsa, uni faqat **AVTO kargo** orqali yuboring! Havo kargosida bojxonada musodara qilinishi mumkin.*\n\n"
        "Tekshirish uchun buyruq: `/kargo [tovar nomi]`\n"
        "Masalan: `/kargo powerbank`"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.startswith("/kargo "))
async def process_cargo_item(message: Message):
    item = message.text.replace("/kargo", "").strip().lower()

    banned_air_keywords = ["batareya", "powerbank", "akkumulyator", "suyuqlik", "atir", "parfyum", "magnit", "kukun", "poroshok", "pichoq"]

    is_banned_air = any(keyword in item for keyword in banned_air_keywords)

    if is_banned_air:
        text = (
            f"❌ **DIQQAT! '{item}' havo kargosi (Air) uchun XAVFSIZ EMAS!**\n\n"
            "Sabab: Tarkibida taqiqlangan elementlar bo'lishi mumkin (batareya, suyuqlik yoki magnit).\n"
            "✅ **Tavsiya:** Ushbu tovarni faqat **AVTO kargo** orqali olib keling!"
        )
    else:
        text = (
            f"✅ **'{item}' havo kargosi (Air) uchun ruxsat etilgan ko'rinadi.**\n\n"
            "Lekin jo'natishdan oldin kargo kompaniyangiz bilan maslahatlashishni unutmang."
        )
    await message.answer(text, parse_mode="Markdown")
