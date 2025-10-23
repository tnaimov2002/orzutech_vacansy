import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = "8487130668:AAG5fwf3HXSvWfKufZVs5cAKEvrBZ6E51uM"  #
ADMIN_ID = 927838060  #

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
    "2. Tug’ilgan sanangiz (kun, oy, yil)?",
    "3. Yashash manzilingiz?",
    "4. Ma’lumotingiz (o’rta maxsus, bakalavr, magistr, PhD)",
    "5. O’quv yurti nomi, tugatgan yil?",
    "6. Mutaxassislik nomi?",
    "7. Qaysi chet tillarini bilasiz?",
    "8. Oilaviy ahvolingiz (uylangan/turmushga chiqqan/yo’q)",
    "9. Farzandlaringiz bormi (soni, jinsi)?",
    "10. Texnik qobiliyatlaringiz (qaysi kompyuter dasturlarini ishlata olasiz)?",
    "11. Insoniy qobilyatlaringiz (ko’nikuvchan, kirishuvchan, intiluvchan, qiziquvchan va h.k)?",
    "12. Qaysi tashkilot yoki muassasalarda ishlagansiz?",
    "13. Qaysi lavozimlarda ishlagansiz? (oy,yil/maosh)",
    "14. Ishdan ketish sabablari?",
    "15. ORZUTECH haqida nimalarni bilasiz?",
    "16. ORZUTECH dan qancha miqdorda maosh kutyapsiz?",
    "17. ORZUTECH bilan bir yildan keyin o’zingizni qanday tasavvur qilasiz?",
    "18. Nimalarga qiziqasiz (hobbingiz)?",
    "19. Haydovchilik guvohnomangiz bormi (toifa, berilgan sana)?",
    "20. Kelayotgan ikki yildagi eng muhim reja va maqsadlaringiz?",
    "21. Siz uchun eng muhimi (mansab, insoniylik, halollik, pul va h.k)?",
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
        "Sozlovchi usta (kompyuter qurilmalari bo’yicha)", "Logist",
        "Yuristkonsult", "Kamera va xavfsizlik qurilmalari montajchisi"
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
    file = msg.document.file_id
    await state.update_data(resume_file=file)
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
        await send_to_admin(data, msg.from_user.id)
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


# --- Admin (profil) ga yuborish ---
async def send_to_admin(data, user_id):
    text = f"📩 Yangi so‘rovnoma:\n\n"
    text += f"👤 Ism: {data.get('name')}\n📞 Telefon: {data.get('contact')}\n💼 Vakansiya: {data.get('vacancy')}\n\n"

    for q, a in zip(questions, data.get('answers', [])):
        text += f"{q}\n👉 {a}\n\n"

    await bot.send_message(ADMIN_ID, text)

    # Agar rezyume fayli mavjud bo‘lsa, uni yuborish
    if "resume_file" in data:
        await bot.send_document(ADMIN_ID, data["resume_file"])

    await bot.send_message(ADMIN_ID, f"🆔 Foydalanuvchi ID: {user_id}")


# --- Run ---
async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
