import io
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto, BufferedInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from handlers.states import ProductCreationState
from services.card_generator import CardGeneratorService
from services.secretary import SecretaryPersona
from services.excel_exporter import UzumExcelExporter

router = Router()

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Yangi tovar qo'shish (Uzum)")],
            [KeyboardButton(text="🧮 Kurs va Kalkulyator"), KeyboardButton(text="✈️ Kargo tekshiruvi")]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    greeting = SecretaryPersona.get_greeting()
    await message.answer(
        f"{greeting}\n\n"
        "Men sizning **Uzum Seller va Xitoy biznesingiz bo'yicha shaxsiy yordamchingizman**.\n\n"
        "Quyidagi imkoniyatlar mavjud:\n"
        "1. 📦 **Uzum tovar kartochkasi**: Rasm, tavsif va narx tashlang — bot sarlavha, SEO tavsif va xarakteristikalarni chiqarib beradi.\n"
        "2. 🧮 **Kalkulyator**: MB valyuta kursi va tannarx hisoblash.\n"
        "3. ✈️ **Kargo tekshiruvi**: Tovar Havo (Air) yoki Avto kargoga to'g'ri kelishini tekshirish.\n\n"
        "Boshlash uchun pastdagi tugmalardan birini tanlang:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@router.message(F.text == "📦 Yangi tovar qo'shish (Uzum)")
@router.message(Command("product"))
async def start_product_creation(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ProductCreationState.waiting_for_photo)
    name_intro = SecretaryPersona.get_greeting()
    await message.answer(
        f"{name_intro}\n\n"
        "📸 **1-Qadam:** Mahsulotning **rasmini** yuboring (yoki rasmsiz davom etish uchun /skip bosing):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

@router.message(ProductCreationState.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await state.set_state(ProductCreationState.waiting_for_description)
    await message.answer(
        "📝 **2-Qadam:** Mahsulot haqida **qisqacha ma'lumot** yozing:\n"
        "(Masalan: *Ayollar sport krossovkasi, oq rang, engil, yozgi, Turkiya/Xitoy*)",
        parse_mode="Markdown"
    )

@router.message(ProductCreationState.waiting_for_photo, Command("skip"))
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo_file_id=None)
    await state.set_state(ProductCreationState.waiting_for_description)
    await message.answer(
        "📝 **2-Qadam:** Mahsulot haqida **qisqacha ma'lumot** yozing:\n"
        "(Masalan: *Simsiz naushnik, bluetooth 5.3, qora, sensorli boshqaruv*)",
        parse_mode="Markdown"
    )

@router.message(ProductCreationState.waiting_for_description, F.text)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(user_description=message.text)
    await state.set_state(ProductCreationState.waiting_for_price)
    await message.answer(
        "💰 **3-Qadam:** Tovarning **sotuv narxini** kiriting (masalan: *120 000 so'm*):",
        parse_mode="Markdown"
    )

@router.message(ProductCreationState.waiting_for_price, F.text)
async def process_price(message: Message, state: FSMContext):
    price = message.text
    user_data = await state.get_data()
    photo_file_id = user_data.get("photo_file_id")
    user_description = user_data.get("user_description", "")

    status_msg = await message.answer("⏳ **Kotiba buyrug'ingizni bajarmoqda, ma'lumotlar tahlil qilinmoqda...**", parse_mode="Markdown")

    image_bytes = None
    if photo_file_id:
        file = await message.bot.get_file(photo_file_id)
        file_io = io.BytesIO()
        await message.bot.download_file(file.file_path, destination=file_io)
        image_bytes = file_io.getvalue()

    card_data = await CardGeneratorService.generate_card(
        image_bytes=image_bytes,
        user_description=user_description,
        price=price
    )
    card_data["price"] = price # Excel uchun narxni qo'shamiz

    await status_msg.delete()

    # Uzum talablariga mos 6 xil AI rasmlarni generatsiya qilish
    img_status = await message.answer("🎨 **Kotiba Uzum Market talablariga mos 6 xil professional rasm generatsiya qilmoqda... (10-15 sekund kuting)**", parse_mode="Markdown")
    try:
        generated_images = await CardGeneratorService.generate_images(
            user_description=user_description,
            dalle_prompt=card_data.get("dalle_prompt"),
            count=6
        )
        await img_status.delete()

        if generated_images:
            media_group = [InputMediaPhoto(media=url) for url in generated_images]
            await message.answer_media_group(media=media_group)
        else:
            await message.answer("⚠️ Rasmlarni generatsiya qilishda API xatoligi yuz berdi.")
    except Exception as e:
        try:
            await img_status.delete()
        except Exception:
            pass
        await message.answer(f"❌ Rasm generatsiyasida xatolik: {e}")

    # Excel faylini yaratish
    excel_io = UzumExcelExporter.create_excel(card_data)
    await message.answer_document(
        document=BufferedInputFile(excel_io.getvalue(), filename=f"uzum_tovar_{price.replace(' ', '')}.xlsx"),
        caption="📊 **Uzum Seller uchun tayyor Excel fayl.**\nBuni to'g'ridan-to'g'ri Uzum Seller kabinetiga yuklashingiz mumkin."
    )

    attrs_text = ""
    for k, v in card_data.get("attributes", {}).items():
        attrs_text += f"• **{k}**: {v}\n"

    secretary_intro = SecretaryPersona.get_greeting()

    result_text = (
        f"{secretary_intro}\n\n"
        "✅ **UZUM MARKET UCHUN TAYYOR TOVAR KARTOCHKASI**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 **Sarlavha (O'zbekcha):**\n`{card_data.get('title_uz')}`\n\n"
        f"📌 **Sarlavha (Ruscha):**\n`{card_data.get('title_ru')}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 **Tavsif (O'zbekcha):**\n```\n{card_data.get('description_uz')}\n```\n\n"
        f"📋 **Tavsif (Ruscha):**\n```\n{card_data.get('description_ru')}\n```\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **Xarakteristikalar:**\n{attrs_text}\n"
        f"📂 **Tavsiya etilgan kategoriya:** {card_data.get('category_suggestion', 'Aniqlanmadi')}\n"
        f"💡 **Narx bo'yicha maslahat:** {card_data.get('pricing_advice', '')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{card_data.get('disclaimer')}\n\n"
        "💡 *Maslahat: Matn ustiga bosib to'g'ridan-to'g'ri nusxa olishingiz mumkin!*"
    )

    await message.answer(result_text, parse_mode="Markdown", reply_markup=main_keyboard())
    await state.clear()
