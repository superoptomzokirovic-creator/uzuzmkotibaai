import asyncio
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from services.calculator_service import CurrencyService, CostCalculator
from services.secretary import SecretaryPersona

router = Router()

@router.message(F.text == "🧮 Kurs va Kalkulyator")
async def cmd_calculator(message: Message):
    greeting = SecretaryPersona.get_greeting()
    rates = await CurrencyService.get_rates()
    usd = rates.get("USD", 12800.0)
    cny = rates.get("CNY", 1780.0)

    text = (
        f"{greeting}\n\n"
        "🧮 **Markaziy Bank Valyuta Kurslari (Bugungi):**\n"
        f"🇺🇸 1 USD = **{usd:,.2f} so'm**\n"
        f"🇨🇳 1 CNY (Yuan) = **{cny:,.2f} so'm**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Tannarx va kargo hisoblash uchun namunaviy buyruq:*\n"
        "`/hisob [yuan_narxi] [soni] [ogirligi_kg] [kargo_narxi_dollarda]`\n"
        "Masalan: `/hisob 15 100 0.5 4.5`\n"
        "(Ya'ni: 15 yuanlik tovar, 100 dona, har biri 0.5 kg, 1 kg kargo 4.5$)"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.startswith("/hisob"))
async def cmd_compute_cost(message: Message):
    parts = message.text.split()
    if len(parts) < 5:
        await message.answer(
            "⚠️ Noto'g'ri format!\n"
            "To'g'ri ishlatish: `/hisob [yuan] [soni] [ogirlik_kg] [kargo_1kg_$]`\n"
            "Misol: `/hisob 15 100 0.5 4.5`",
            parse_mode="Markdown"
        )
        return

    try:
        unit_cny = float(parts[1])
        qty = int(parts[2])
        weight = float(parts[3])
        cargo_usd_per_kg = float(parts[4])
    except ValueError:
        await message.answer("⚠️ Iltimos, raqamlarni to'g'ri formatda kiriting!")
        return

    rates = await CurrencyService.get_rates()
    cny_rate = rates.get("CNY", 1780.0)
    usd_rate = rates.get("USD", 12800.0)
    cargo_rate_uzs = cargo_usd_per_kg * usd_rate

    res = CostCalculator.calculate_item_cost(
        unit_price_cny=unit_cny,
        quantity=qty,
        weight_kg=weight,
        cargo_rate_per_kg=cargo_rate_uzs,
        cny_rate=cny_rate,
        uzum_commission_percent=20.0
    )

    secretary_intro = SecretaryPersona.get_greeting()

    text = (
        f"{secretary_intro}\n\n"
        "📊 **TANNARX VA XARAJATLAR HISOBI (100% Aniq Python Math)**\n\n"
        f"• Tovar narxi (Yuan): **{unit_cny} ¥** x {qty} dona\n"
        f"• So'mdagi tovar summasi: **{res['total_item_uzs']:,.2f} so'm**\n"
        f"• Kargo xarajati ({weight} kg x {qty} dona = {weight*qty} kg): **{res['total_cargo_uzs']:,.2f} so'm**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **Umumiy Investitsiya:** **{res['total_investment']:,.2f} so'm**\n"
        f"🏷 **1 dona tovar tannarxi:** **{res['unit_cost_uzs']:,.2f} so'm**\n\n"
        "⚠️ *Uzumda sotganda 15-25% komissiya, soliq va logistikani ham hisobga olishni unutmang!*"
    )
    await message.answer(text, parse_mode="Markdown")
