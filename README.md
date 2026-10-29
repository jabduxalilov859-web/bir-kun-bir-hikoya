# Bir kun — bir hikoya (Website)

Telegram bot topshirig'i asosida website + Telegram admin integratsiyasi.

## Papka tuzilmasi
app.py, config.py, models.py, telegram_notify.py, templates/, static/css/, .env.example

## O'rnatish
pip install -r requirements.txt
cp .env.example .env  # token, admin ID ni to'ldiring
python app.py
/api/init-db ga 1 marta kiring
/admin - login

## Telegram oqim
Foydalanuvchi /yuborish formani to'ldiradi -> send_to_admin -> sizga ✅ E'lon / ❌ Rad tugmalari bilan keladi
Webhook: https://api.telegram.org/botTOKEN/setWebhook?url=https://domain/telegram/webhook

## Talablar bajarildi
Bugungi hikoya, kutubxona filter, sevimlilar, yuborish, admin stats, qayta e'lon blok, .env xavfsizlik
