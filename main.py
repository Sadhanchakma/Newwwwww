import telebot
from telebot import types
import requests

# আপনার টেলিগ্রাম বট টোকেন দিন
TOKEN = '8789432285:AAE0NsRd-lHLhDkzhx1CCUXekobc2sME_HQ'
bot = telebot.TeleBot(TOKEN)

# হোস্টিং করলে লোকালহোস্টের বদলে আপনার সার্ভার ইউআরএল দিন
# main.py এর ভেতর এই লাইনটি পরিবর্তন করুন
BASE_URL = "https://newwwwww-production-ca26.up.railway.app"


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📷 QR CODE", callback_data="connect_qr")
    btn2 = types.InlineKeyboardButton("📱 PAIR CODE", callback_data="connect_pair")
    markup.add(btn1, btn2)

    welcome_text = (
        "💎 *Chakma WhatsApp Checker*\n\n"
        "Welcome! Please select an option below to connect your WhatsApp:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "connect_pair":
        msg = bot.send_message(
            call.message.chat.id, 
            "🟡 *WhatsApp connecting...*\n\n"
            "📱 *আপনার WhatsApp নম্বর দিন:*\n\n"
            "Country code (880) সহ শুধু সংখ্যা লিখুন।\n"
            "✅ উদাহরণ: `8801533833020`",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_pair_code)

def process_pair_code(message):
    num = message.text.strip()
    if not num.isdigit():
        bot.reply_to(message, "❌ ভুল নম্বর! শুধু সংখ্যা দিন।")
        return

    wait_msg = bot.send_message(message.chat.id, "⌛ *Pairing code তৈরি হচ্ছে...*", parse_mode="Markdown")

    try:
        response = requests.get(f"{BASE_URL}/pair?number={num}", timeout=60)
        data = response.json()

        if 'code' in data:
            code = data['code']
            result_text = (
                "🔑 *Your Pairing Code:*\n\n"
                f"`{code.upper()}`\n\n"
                "───────────────────\n"
                "*কিভাবে ব্যবহার করবেন:*\n"
                "1️⃣ WhatsApp > Settings > Linked Devices\n"
                "2️⃣ 'Link with phone number instead' চাপুন\n"
                "3️⃣ উপরের কোডটি দিন।\n\n"
                "⏰ *Code কিছুক্ষণের মধ্যে expire হবে।*"
            )
            bot.edit_message_text(result_text, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ সার্ভার কোড দিতে পারেনি। আবার ট্রাই করুন।", message.chat.id, wait_msg.message_id)
            
    except Exception:
        bot.edit_message_text("⚠️ সার্ভার কানেকশন এরর!", message.chat.id, wait_msg.message_id)

bot.infinity_polling()
