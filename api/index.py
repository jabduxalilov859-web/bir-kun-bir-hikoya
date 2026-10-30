import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, datetime
import requests

app = Flask(__name__, 
            template_folder=os.path.join(ROOT, 'templates'),
            static_folder=os.path.join(ROOT, 'static'))

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'bir-kun-2026-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    from models import db, Story, Submission, User
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if Story.query.count() == 0:
            demo = Story(
                title="Bugungi kunning qadri",
                content="Bugun - eng qimmatli kun! Har kuni bir hikoya, har kuni bir saboq.",
                category="motivatsiya",
                image_url="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800",
                date=date.today(),
                is_published=True
            )
            db.session.add(demo)
            db.session.commit()
except Exception as e:
    print(f"DB init xato: {e}")

CATEGORIES = ["motivatsiya","hayotiy saboqlar","do'stlik","oila","muvaffaqiyat","shaxsiy rivojlanish"]

# ============ TELEGRAM FUNKSIYASI ============
def send_to_admin_tg(sub):
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')
        admin_id = os.getenv('ADMIN_TELEGRAM_ID')
        if not bot_token or not admin_id:
            print("Telegram token yoki ID yo'q!")
            return
        text = f"📩 YANGI HIKOYA KELDI!\n\n📖 Sarlavha: {sub.title}\n👤 Muallif: Anonim\n\n📝 Matn:\n{sub.content[:900]}..."
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ E'lon qilish", "callback_data": f"approve_{sub.id}"},
                {"text": "❌ Rad etish", "callback_data": f"reject_{sub.id}"}
            ]]
        }
        r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": admin_id,
            "text": text,
            "reply_markup": keyboard
        }, timeout=10)
        print(f"Telegramga yuborildi: {r.status_code}")
    except Exception as e:
        print(f"Telegram xato: {e}")

@app.route('/')
def index():
    try:
        bugungi = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).first()
        latest = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).limit(20).all()
        return render_template('index.html', today_story=bugungi, bugungi=bugungi, stories=latest, latest=latest, recent_stories=latest, categories=CATEGORIES)
    except Exception as e:
        return f"<h1>Sayt ishga tushmoqda...</h1><p>{e}</p><a href='/api/init'>Qayta urinish</a>"

@app.route('/kutubxona')
def kutubxona():
    try:
        stories = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).all()
        return render_template('kutubxona.html', stories=stories, categories=CATEGORIES, selected_cat=None, q="")
    except:
        return "Baza yaratilmoqda..."

@app.route('/hikoya/<int:id>')
def hikoya_detail(id):
    story = Story.query.get_or_404(id)
    try:
        story.views += 1
        db.session.commit()
    except:
        pass
    return render_template('hikoya.html', story=story)

@app.route('/yuborish', methods=['GET','POST'])
def yuborish():
    if request.method == 'POST':
        try:
            title = request.form.get('title', 'Sarlavhasiz')
            content = request.form.get('content')
            if content:
                sub = Submission(title=title, content=content, status="Ko'rib chiqilmoqda", category="hayotiy saboqlar")
                db.session.add(sub)
                db.session.commit()
                # TELEGRAMGA YUBORISH - MUHIM!
                try:
                    send_to_admin_tg(sub)
                except Exception as e:
                    print(f"TG yuborish xato: {e}")
                flash("Hikoyangiz qabul qilindi! Admin ko'rib chiqadi.", "success")
        except Exception as e:
            print(e)
        return redirect(url_for('yuborish'))
    return render_template('yuborish.html')

@app.route('/sevimlilar')
@app.route('/sevimli')
@app.route('/favorites')
def sevimlilar():
    try:
        return render_template('sevimlilar.html')
    except:
        return """<html><head><title>Sevimlilar</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{font-family:sans-serif;text-align:center;padding:20px;background:#f5f5f5} .box{background:white;padding:40px;border-radius:20px;max-width:500px;margin:40px auto;box-shadow:0 10px 30px rgba(0,0,0,0.1)} a{background:black;color:white;padding:12px 24px;border-radius:30px;text-decoration:none;display:inline-block;margin:10px} a.sec{background:#eee;color:black}</style></head><body><div class="box"><h1>❤️ Sevimlilar</h1><p>Sevimli hikoyalaringiz bu yerda!</p><a href="/kutubxona">Kutubxonaga</a><br><a class="sec" href="/">Bosh sahifa</a></div></body></html>"""

@app.route('/loyiha-haqida')
def haqida():
    return render_template('haqida.html')

# ============ ADMIN ============
@app.route('/brainn-hr-admin-2026', methods=['GET','POST'])
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        admin_u = os.getenv('ADMIN_USERNAME', 'brainn_hr')
        admin_p = os.getenv('ADMIN_PASSWORD', 'brainn_hr123')
        if u == admin_u and p == admin_p:
            session['is_admin'] = True
            return redirect('/brainn-hr-admin-2026/dashboard')
        else:
            flash("Login yoki parol noto'g'ri", "error")
    return render_template('admin_login.html')

@app.route('/brainn-hr-admin-2026/dashboard')
@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        total = Story.query.count()
        total_published = Story.query.filter_by(is_published=True).count()
        subs = Submission.query.order_by(Submission.id.desc()).limit(30).all()
        pending = Submission.query.filter(Submission.status=="Ko'rib chiqilmoqda").count()
        return render_template('admin_dashboard.html', total_stories=total, total_published=total_published, total_subs=len(subs), pending=pending, total_users=0, subs=subs, categories=CATEGORIES)
    except Exception as e:
        return f"Admin xato: {e}"

@app.route('/admin/submission/<int:id>/<action>')
def admin_sub_action(id, action):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        sub = Submission.query.get_or_404(id)
        if action == 'approve' or action == 'elon':
            exists = Story.query.filter_by(content=sub.content).first()
            if not exists:
                new_story = Story(title=sub.title or "Sarlavhasiz", content=sub.content, summary=sub.content[:150], category=sub.category or "hayotiy saboqlar", image_url=sub.image_url or "https://images.unsplash.com/photo-1501504905252-473cbee65f87?w=800", date=date.today(), is_published=True, author_name=sub.author_name, is_user_submitted=True)
                db.session.add(new_story)
                sub.status = "E'lon qilindi"
                db.session.commit()
        elif action == 'reject' or action == 'rad':
            sub.status = "Rad etildi"
            db.session.commit()
    except Exception as e:
        print(f"Admin action xato: {e}")
    return redirect('/brainn-hr-admin-2026/dashboard')

@app.route('/admin/hikoya/<int:id>/delete')
def admin_delete(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        story = Story.query.get_or_404(id)
        db.session.delete(story)
        db.session.commit()
    except:
        pass
    return redirect('/brainn-hr-admin-2026/dashboard')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/')

@app.route('/admin/hikoyalar')
def admin_hikoyalar():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        stories = Story.query.order_by(Story.id.desc()).all()
        return render_template('admin_hikoyalar.html', stories=stories, categories=CATEGORIES)
    except Exception as e:
        return f"Xato: {e}"

@app.route('/admin/hikoya/add', methods=['GET','POST'])
def admin_add():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        try:
            s = Story(title=request.form.get('title'), content=request.form.get('content'), summary=request.form.get('summary') or request.form.get('content','')[:150], category=request.form.get('category') or "hayotiy saboqlar", image_url=request.form.get('image_url') or "https://images.unsplash.com/photo-1501504905252-473cbee65f87?w=800", date=datetime.strptime(request.form.get('date'), "%Y-%m-%d").date() if request.form.get('date') else date.today(), is_published=bool(request.form.get('is_published')), publish_at=datetime.now())
            db.session.add(s)
            db.session.commit()
            flash("Hikoya qo'shildi!", "success")
            return redirect('/admin/hikoyalar')
        except Exception as e:
            print(f"Add xato: {e}")
    return render_template('admin_hikoya_form.html', categories=CATEGORIES, story=None)

@app.route('/admin/hikoya/<int:id>/edit', methods=['GET','POST'])
def admin_edit(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    story = Story.query.get_or_404(id)
    if request.method == 'POST':
        try:
            story.title = request.form.get('title')
            story.content = request.form.get('content')
            story.summary = request.form.get('summary')
            story.category = request.form.get('category')
            story.image_url = request.form.get('image_url')
            story.is_published = bool(request.form.get('is_published'))
            db.session.commit()
            return redirect('/admin/hikoyalar')
        except:
            pass
    return render_template('admin_hikoya_form.html', story=story, categories=CATEGORIES)

# ============ TELEGRAM WEBHOOK - ENDI ISHLAYDI! ============
@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    try:
        data = request.get_json()
        print(f"Webhook keldi: {data}")
        if data and 'callback_query' in data:
            cq = data['callback_query']
            cb_data = cq.get('data','')
            message = cq.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')
            callback_query_id = cq.get('id')
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery", json={"callback_query_id": callback_query_id, "text": "Qabul qilindi!"}, timeout=5)
            except:
                pass
            sid = None
            action = None
            if cb_data.startswith('approve_'):
                sid = int(cb_data.split('_')[1])
                action = 'approve'
            elif cb_data.startswith('reject_'):
                sid = int(cb_data.split('_')[1])
                action = 'reject'
            if sid:
                sub = Submission.query.get(sid)
                if sub:
                    if action == 'approve' and sub.status != "E'lon qilindi":
                        new_story = Story(title=sub.title or "Sarlavhasiz", content=sub.content, summary=sub.content[:150], category=sub.category or "hayotiy saboqlar", image_url=sub.image_url or "https://images.unsplash.com/photo-1501504905252-473cbee65f87?w=800", date=date.today(), is_published=True, author_name=sub.author_name, is_user_submitted=True)
                        db.session.add(new_story)
                        sub.status = "E'lon qilindi"
                        db.session.commit()
                        requests.post(f"https://api.telegram.org/bot{bot_token}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": f"✅ E'LON QILINDI!\n\n{new_story.title}"}, timeout=5)
                    elif action == 'reject':
                        sub.status = "Rad etildi"
                        db.session.commit()
                        requests.post(f"https://api.telegram.org/bot{bot_token}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": f"❌ RAD ETILDI!\n\n{sub.title}"}, timeout=5)
    except Exception as e:
        print(f"Webhook xato: {e}")
        import traceback
        traceback.print_exc()
    return jsonify({"ok": True})

@app.route('/api/init')
def init_db():
    try:
        db.create_all()
        return "DB tayyor! <a href='/'>Bosh sahifa</a>"
    except Exception as e:
        return f"Xato: {e}"
