
import requests
from config import Config

def send_to_admin(submission):
    if not Config.BOT_TOKEN or not Config.ADMIN_TELEGRAM_ID:
        print("BOT_TOKEN yoki ADMIN_ID yoq - .env ni toldiring @brainn_hr")
        return False
    text = f"📝 YANGI HIKOYA @brainn_hr UCHUN!\n\n🏷 Sarlavha: {submission.title or 'Sarlavhasiz'}\n👤 Muallif: {submission.author_name or 'Nomalum'}\n🔗 Username: @{submission.telegram_username or 'yoq'}\n🆔 TG ID: {submission.telegram_id or 'yoq'}\n\nMatn:\n{submission.content[:3500]}\n\nID: {submission.id}"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ E'lon qilish", "callback_data": f"approve_{submission.id}"},
                {"text": "❌ Rad etish", "callback_data": f"reject_{submission.id}"}
            ],
            [{"text": "💬 Muallifga javob", "callback_data": f"reply_{submission.id}"}]
        ]
    }
    url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": Config.ADMIN_TELEGRAM_ID, "text": text, "reply_markup": keyboard}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print(e)
        return False

def send_to_user(tg_id, text):
    if not Config.BOT_TOKEN or not tg_id:
        return False
    url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": tg_id, "text": text}, timeout=10)
    except:
        pass
