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
EMAIL_RECEIVER = "malikamagnat92@gmail.com"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# --- States ---
class VacancyForm(StatesGroup):
    get_contact = State()
    choose_vacancy = State()
    ask_questions = State()
    confirm_consent = State()


# --- Savollar ---
questions = [
    "1. Familya ism sharifingiz?",
    "2. Tug‘ilgan sanangiz (kun, oy, yil)?",
    "3. Ma’lumotingiz (o‘quv yurt nomi, yil, mutaxassislik)?",
    "4. Shu sohadagi tajribangiz (oy, yil)?",
    "5. Qaysi chet tillarini bilasiz?",
    "6. Oilaviy ahvolingiz?",
    "7. Farzandlaringiz bormi (soni, jinsi)?",
    "8. Texnik qobiliyatlaringiz?",
    "9. Insoniy qobiliyatlaringiz?",
    "10. Qaysi tashkilot yoki muassasalarda ishlagansiz?",
    "11. Ish tajribangiz (lavozim, maosh)?",
    "12. Ishdan ketish sabablari?",
    "13. OrzuTech haqida nimalarni bilasiz?",
    "14. Qancha maosh kutyapsiz?",
    "15. OrzuTech bilan bir yildan keyin o‘zingizni qanday tasavvur qilasiz?",
    "16. Nimalarga qiziqasiz (hobbingiz)?",
    "17. Haydovchilik guvohnomangiz bormi?",
    "18. Kelayotgan ikki yildagi eng muhim rejalaringiz?",
    "19. Siz uchun eng muhimi?",
    "20. So‘rovnoma to‘ldirilgan sana?",
    "21. Bog‘lanish uchun telefon raqamingiz?",
]


# --- Start bosilganda ---
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await msg.answer("👋 Assalomu alaykum Orzutech Vacancy Bot’ga xush kelibsiz!")
    await msg.answer("Endi siz bilan yaqindan tanishamiz.\nIltimos, telegram profilingizni biz bilan ulashing👇")

    kb = ReplyKeyboardBuilder()
    kb.button(text="📱 Kontaktni ulashish", request_contact=True)
    kb.adjust(1)
    await msg.answer("Profilingizni ulashish uchun pastdagi tugmani bosing:", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(VacancyForm.get_contact)


# --- Kontaktni qabul qilish ---
@dp.message(VacancyForm.get_contact, F.contact)
async def process_contact(msg: types.Message, state: FSMContext):
    contact = msg.contact.phone_number
    user_name = msg.from_user.full_name
    await state.update_data(contact=contact, name=user_name)
    await msg.answer("Rahmat 😊", reply_markup=types.ReplyKeyboardRemove())

    # Vakansiyalar ro‘yxatini yuborish (ReplyKeyboard orqali)
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
    await state.update_data(vacancy=vacancy, answers=[])
    await msg.answer(f"✅ Siz tanladingiz: {vacancy}\n\nKeling, endi siz bilan tanishamiz!", reply_markup=types.ReplyKeyboardRemove())
    await msg.answer(questions[0])
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
        await msg.answer("🔒 Ma’lumotlaringizni qayta ishlashga rozimisiz?", reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(VacancyForm.confirm_consent)


# --- Rozilikni qabul qilish yoki rad etish ---
@dp.message(VacancyForm.confirm_consent)
async def consent_handler(msg: types.Message, state: FSMContext):
    data = await state.get_data()

    if msg.text == "✅ Roziman":
        # Email yuborish
        await send_email(data)
        await msg.answer("✅ Barcha javoblar qabul qilindi.\nSo‘rovnomaga javob berganingiz uchun rahmat!\nTez orada siz bilan bog‘lanamiz.", reply_markup=types.ReplyKeyboardRemove())
    else:
        await msg.answer("❌ Hurmatli foydalanuvchi, ma’lumotlaringizni qayta ishlash bekor qilindi.\n/start buyrug‘ini bosib qayta urinish mumkin.", reply_markup=types.ReplyKeyboardRemove())

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
