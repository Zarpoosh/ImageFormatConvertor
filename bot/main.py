# bot/main.py
import os
import io
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
CONVERT_API_URL = os.getenv("CONVERT_API_URL")  # e.g. https://your-project.vercel.app/api/convert

if not BOT_TOKEN or not CONVERT_API_URL:
    raise RuntimeError("Set BOT_TOKEN and CONVERT_API_URL in .env")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = ("سلام! عکس یا تصویرت رو بفرست تا برات تبدیل کنم.\n"
            "می‌تونی فرمت خروجی رو با دستور زیر انتخاب کنی:\n"
            "/format webp 85  -> webp با کیفیت 85\n"
            "تا زمانی که فرمت انتخاب نکنی، خروجی webp و کیفیت 85 خواهد بود.")
    bot.reply_to(message, text)

# نگهداری تنظیمات کاربر (ساده، در حافظه؛ بعدا میشه DB زد)
user_prefs = {}  # user_id -> {'format':'webp','quality':85}

@bot.message_handler(commands=['format'])
def set_format(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "مثال استفاده: /format webp 85")
        return
    fmt = parts[1].lower()
    q = int(parts[2]) if len(parts) > 2 else 85
    if fmt not in ('webp','png','jpg','jpeg','avif'):
        bot.reply_to(message, "فرمت پشتیبانی‌شده: webp, png, jpg, avif")
        return
    user_prefs[message.from_user.id] = {'format':fmt, 'quality': max(1, min(100, q))}
    bot.reply_to(message, f"تنظیم شد: فرمت={fmt} کیفیت={q}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    uid = message.from_user.id
    prefs = user_prefs.get(uid, {'format':'webp','quality':85})
    fmt = prefs['format']
    quality = prefs['quality']

    bot.send_chat_action(message.chat.id, 'typing')

    # دریافت فایل بزرگ‌تر (last)
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    r = requests.get(file_url, timeout=30)
    if r.status_code != 200:
        bot.reply_to(message, "خطا در دانلود عکس از تلگرام.")
        return

    files = {'image': ('image', io.BytesIO(r.content))}
    data = {'format': fmt, 'quality': str(quality)}

    try:
        res = requests.post(CONVERT_API_URL, files=files, data=data, timeout=60)
    except Exception as e:
        bot.reply_to(message, "خطا در ارتباط با سرور تبدیل: " + str(e))
        return

    if res.status_code == 200:
        bio = io.BytesIO(res.content)
        bio.seek(0)
        # اسم فایل بر اساس فرمت
        fname = f"converted.{fmt if fmt!='jpeg' else 'jpg'}"
        bot.send_document(message.chat.id, bio, filename=fname)
    else:
        bot.reply_to(message, f"خطا در تبدیل: {res.status_code} - {res.text}")

if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling()
