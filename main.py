import asyncio
import smtplib
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from email.mime.text import MIMEText

API_TOKEN = "8487130668:AAG5fwf3HXSvWfKufZVs5cAKEvrBZ6E51uM"  # <-- o'z tokeningni qo'y
EMAIL_SENDER = "malikamagnat92@gmail.com"
EMAIL_PASSWORD = "lbyz qzyx wupq pbkz"  # <-- Gmail uchun App Password ishlatiladi
EMAIL_RECEIVER = "malika-magnat@mail.ru"  # <-- Yangi qabul qiluvchi pochta

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# --- States ---
class VacancyForm(StatesGroup):
    get_contact = State()
    choose_vacancy = State()
    resume_choice = State()
    upload_resume = State()
    ask_questions = State()
    confirm_consent = State()


# --- Savollar ---
questions = [
    "1. Familya ism sharifingiz?",
    "2. Tug‘ilgan sanangiz (kun, oy, yil)?",
    "3. Ma’lumotingiz (o‘quv yurt nomi, yil, mutaxassislik)?",
    "4. Shu sohadagi tajribangiz (oy, yil)?",
    "5. Qaysi chet tillarini bilasiz?",
    "6. Oilaviy ahvolingiz (uylangan/turmushga chiqqan, yo’q)",
    "7. Farzandlaringiz bormi (soni, jinsi)?",
    "8. Texnik qobiliyatlaringiz (kompyuter dasturlarini ishlata olasiz)?",
    "9. Insoniy qobilyatlaringiz (kirishuvchan, intiluvchan va h.k)?",
    "10. Qaysi tashkilot yoki muassasalarda ishlagansiz?",
    "11. Ish tajribangiz (lavozim, maosh)?",
    "12. Ishdan ketish sabablari?",
    "13. OrzuTech haqida nimalarni bilasiz?",
    "14. Qancha maosh kutyapsiz?",
    "15. OrzuTech bilan bir yildan keyin o‘zingizni qanday tasavvur qilasiz?",
    "16. Nimalarga qiziqasiz (hobbingiz)?",
    "17. Haydovchilik guvohnomangiz bormi (toifa, berilgan sana)?",
    "18. Kelayotgan ikki yildagi eng muhim rejalaringiz?",
    "19. Siz uchun eng muhimi (mansab, insoniylik, halollik, pul va b)?",
    "20. So‘rovnoma to‘ldirilgan sana?",
]


# --- Start bosilganda ---
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await msg.answer("👋 Assalomu alaykum Orzutech Vacancy Bot’ga xush kelibsiz!")
    await msg.answer("Endi siz bilan yaqindan tanishamiz.\nIltimos, telegram profilingizni biz bilan ulashing👇")

    kb = ReplyKeyboardBuilder()
    kb.button(text="📱 Kontaktni ulashish", request_contact=True)
    kb.adjust(1)
    await msg.answer(
        "Profilingizni ulashish uchun pastdagi tugmani bosing:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(VacancyForm.get_contact)


# --- Kontaktni qabul qilish ---
@dp.message(VacancyForm.get_contact, F.contact)
async def process_contact(msg: types.Message, state: FSMContext):
    contact = msg.contact.phone_number
    user_name = msg.from_user.full_name
    await state.update_data(contact=contact, name=user_name)
    await msg.answer("Rahmat 😊", reply_markup=types.ReplyKeyboardRemove())

    # Vakansiyalar ro‘yxatini yuborish
    kb = ReplyKeyboardBuilder()
    vacancies = [
        "Sotuvchi", "Haydovchi", "Omborchi", "Savdo mutaxassisi", "Broker",
        "SMM mutaxassisi", "Grafik dizayner", "Dasturchi", "Hisobchi",
        "Sozlovchi usta", "Avtoturargoh nazoratchisi", "Logist",
        "Yuristkonsult", "Radioelektron texnik-montajchi",
        "Telemexanika muhandisi"
    ]
    for v in vacancies:
        kb.button(text=v)
    kb.adjust(2)
    await msg.answer("📋 Vakansiyalardan birini tanlang:", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(VacancyForm.choose_vacancy)


# --- Vakansiya tanlash ---
@dp.message(VacancyForm.choose_vacancy)
async def vacancy_chosen(msg: types.Message, state: FSMContext):
    vacancy = msg.text.strip()
    await state.update_data(vacancy=vacancy)
    kb = ReplyKeyboardBuilder()
    kb.button(text="📄 Rezyume yuborish")
    kb.button(text="⏭ Rezyumesiz davom etish")
    kb.adjust(2)
    await msg.answer(
        f"✅ Siz tanladingiz: {vacancy}\nEndi quyidagilardan birini tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(VacancyForm.resume_choice)


# --- Rezyume tanlovi ---
@dp.message(VacancyForm.resume_choice)
async def handle_resume_choice(msg: types.Message, state: FSMContext):
    if msg.text == "📄 Rezyume yuborish":
        await msg.answer("📎 Marhamat, bizga rezyumingizni fayl shaklida yuboring (PDF, DOCX, JPG va h.k).")
        await state.set_state(VacancyForm.upload_resume)
    elif msg.text == "⏭ Rezyumesiz davom etish":
        await msg.answer("Keling, endi siz bilan tanishamiz!", reply_markup=types.ReplyKeyboardRemove())
        await msg.answer(questions[0])
        await state.update_data(answers=[])
        await state.set_state(VacancyForm.ask_questions)
    else:
        await msg.answer("Iltimos, pastdagi tugmalardan birini tanlang.")


# --- Rezyume faylini qabul qilish ---
@dp.message(VacancyForm.upload_resume, F.document)
async def handle_resume_file(msg: types.Message, state: FSMContext):
    file_info = await bot.get_file(msg.document.file_id)
    file_path = file_info.file_path
    await state.update_data(resume_file=file_path)
    await msg.answer("✅ Rezyume qabul qilindi!\nEndi savol-javob jarayoniga o‘tamiz.", reply_markup=types.ReplyKeyboardRemove())
    await msg.answer(questions[0])
    await state.update_data(answers=[])
    await state.set_state(VacancyForm.ask_questions)


# --- Savollar jarayoni ---
@dp.message(VacancyForm.ask_questions)
async def process_questions(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", [])
    answers.append(msg.text)
    idx = len(answers)

    if idx < len(questions):
        await state.update_data(answers=answers)
        await msg.answer(questions[idx])
    else:
        await state.update_data(answers=answers)
        kb = ReplyKeyboardBuilder()
        kb.button(text="✅ Roziman")
        kb.button(text="❌ Rad etaman")
        kb.adjust(2)
        await msg.answer(
            "🔒 Ma’lumotlaringizni qayta ishlashga rozimisiz?",
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        await state.set_state(VacancyForm.confirm_consent)


# --- Rozilikni qabul qilish yoki rad etish ---
@dp.message(VacancyForm.confirm_consent)
async def consent_handler(msg: types.Message, state: FSMContext):
    data = await state.get_data()

    if msg.text == "✅ Roziman":
        await send_email(data)
        await msg.answer(
            "✅ Barcha javoblar qabul qilindi.\nSo‘rovnomaga javob berganingiz uchun rahmat!\nTez orada siz bilan bog‘lanamiz.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await msg.answer(
            "❌ Hurmatli foydalanuvchi, ma’lumotlaringizni qayta ishlash bekor qilindi.\n/start buyrug‘ini bosib qayta urinish mumkin.",
            reply_markup=types.ReplyKeyboardRemove()
        )

    await state.clear()


# --- Email yuborish funksiyasi ---
async def send_email(data):
    text = f"📩 Yangi so‘rovnoma:\n\n"
    text += f"Ism: {data.get('name')}\nTelefon: {data.get('contact')}\nVakansiya: {data.get('vacancy')}\n\n"

    for q, a in zip(questions, data.get('answers', [])):
        text += f"{q}\n👉 {a}\n\n"

    msg = MIMEText(text)
    msg["Subject"] = "Yangi Orzutech vakansiya so‘rovnomasi"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email yuborildi")
    except Exception as e:
        print("❌ Email yuborishda xatolik:", e)


# --- Run ---
async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

