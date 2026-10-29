from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from config import Config
from models import db, Story, Submission, User
from telegram_notify import send_to_admin, send_to_user
from datetime import datetime, date
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ADMIN_URL = '/brainn-hr-admin-2026'
CATEGORIES = ["motivatsiya","hayotiy saboqlar","do'stlik","oila","muvaffaqiyat","shaxsiy rivojlanish"]

@app.before_request
def track_user():
    if 'user_key' not in session:
        session['user_key'] = os.urandom(8).hex()
        try:
            u = User(ip=request.remote_addr)
            db.session.add(u)
            db.session.commit()
        except:
            pass

@app.route('/')
def index():
    today = date.today()
    bugungi = Story.query.filter_by(is_published=True, date=today).first()
    if not bugungi:
        bugungi = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).first()
    latest = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).limit(20).all()
    # Instagram uslubi uchun - hamma nom bilan uzatamiz
    return render_template('index.html', 
                         today_story=bugungi, 
                         bugungi=bugungi,
                         stories=latest,
                         latest=latest,
                         recent_stories=latest,
                         categories=CATEGORIES)

@app.route('/kutubxona')
def kutubxona():
    cat = request.args.get('cat')
    q = request.args.get('q','')
    query = Story.query.filter_by(is_published=True)
    if cat and cat in CATEGORIES:
        query = query.filter_by(category=cat)
    if q:
        query = query.filter((Story.title.contains(q)) | (Story.content.contains(q)))
    stories = query.order_by(Story.id.desc()).all()
    return render_template('kutubxona.html', stories=stories, categories=CATEGORIES, selected_cat=cat, q=q)

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
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author_name')
        tg_user = request.form.get('tg_username')
        tg_id = request.form.get('tg_id')
        image_url = request.form.get('image_url')
        rozilik = request.form.get('rozilik')
        if not content:
            flash("Hikoya matni bosh bolmasligi kerak", "error")
            return redirect(url_for('yuborish'))
        sub = Submission(
            title=title, 
            content=content, 
            image_url=image_url,
            author_name=author if rozilik else None,
            telegram_username=tg_user, 
            telegram_id=tg_id, 
            status="Ko'rib chiqilmoqda"
        )
        db.session.add(sub)
        db.session.commit()
        try:
            send_to_admin(sub)
        except Exception as e:
            print("Telegram xato:", e)
        flash("Hikoyangiz qabul qilindi! Administrator korib chiqadi.", "success")
        return redirect(url_for('yuborish'))
    return render_template('yuborish.html')

@app.route('/sevimlilar')
def sevimlilar():
    return render_template('sevimlilar.html')

@app.route('/loyiha-haqida')
def haqida():
    return render_template('haqida.html')

def is_admin():
    return session.get('is_admin')

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if u == Config.ADMIN_USERNAME and p == Config.ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect('/brainn-hr-admin-2026')
        else:
            flash("Login yoki parol notogri", "error")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/brainn-hr-admin-2026')
@app.route('/admin')
def admin_dashboard():
    if not is_admin(): return redirect(url_for('admin_login'))
    total_stories = Story.query.count()
    total_published = Story.query.filter_by(is_published=True).count()
    total_subs = Submission.query.count()
    pending = Submission.query.filter(Submission.status=="Ko'rib chiqilmoqda").count()
    total_users = User.query.count()
    subs = Submission.query.order_by(Submission.created_at.desc()).limit(30).all()
    return render_template('admin_dashboard.html', total_stories=total_stories, total_published=total_published,
                           total_subs=total_subs, pending=pending, total_users=total_users, subs=subs, categories=CATEGORIES)

@app.route('/admin/hikoyalar')
def admin_hikoyalar():
    if not is_admin(): return redirect(url_for('admin_login'))
    stories = Story.query.order_by(Story.id.desc()).all()
    return render_template('admin_hikoyalar.html', stories=stories, categories=CATEGORIES)

@app.route('/admin/hikoya/add', methods=['GET','POST'])
def admin_add():
    if not is_admin(): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        s = Story(
            title=request.form.get('title'),
            content=request.form.get('content'),
            summary=request.form.get('summary'),
            category=request.form.get('category'),
            image_url=request.form.get('image_url'),
            date=datetime.strptime(request.form.get('date'), "%Y-%m-%d").date() if request.form.get('date') else date.today(),
            is_published=bool(request.form.get('is_published')),
            publish_at=datetime.now()
        )
        db.session.add(s)
        db.session.commit()
        flash("Hikoya qoshildi", "success")
        return redirect(url_for('admin_hikoyalar'))
    return render_template('admin_hikoya_form.html', categories=CATEGORIES, story=None)

@app.route('/admin/hikoya/<int:id>/edit', methods=['GET','POST'])
def admin_edit(id):
    if not is_admin(): return redirect(url_for('admin_login'))
    story = Story.query.get_or_404(id)
    if request.method == 'POST':
        story.title = request.form.get('title')
        story.content = request.form.get('content')
        story.summary = request.form.get('summary')
        story.category = request.form.get('category')
        story.image_url = request.form.get('image_url')
        story.is_published = bool(request.form.get('is_published'))
        if request.form.get('date'):
            try:
                story.date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").date()
            except:
                pass
        db.session.commit()
        flash("Yangilandi", "success")
        return redirect(url_for('admin_hikoyalar'))
    return render_template('admin_hikoya_form.html', story=story, categories=CATEGORIES)

@app.route('/admin/hikoya/<int:id>/delete')
def admin_delete(id):
    if not is_admin(): return redirect(url_for('admin_login'))
    story = Story.query.get_or_404(id)
    db.session.delete(story)
    db.session.commit()
    return redirect(url_for('admin_hikoyalar'))

@app.route('/admin/submission/<int:id>/<action>')
def admin_sub_action(id, action):
    if not is_admin(): return redirect(url_for('admin_login'))
    sub = Submission.query.get_or_404(id)
    if action == 'approve':
        exists = Story.query.filter_by(content=sub.content).first()
        if exists:
            flash("Bu hikoya allaqachon elon qilingan!", "error")
        else:
            new_story = Story(
                title=sub.title or "Sarlavhasiz hikoya", 
                content=sub.content,
                summary=sub.content[:150], 
                category="hayotiy saboqlar",
                image_url=sub.image_url,
                date=date.today(), 
                is_published=True, 
                author_name=sub.author_name, 
                is_user_submitted=True
            )
            db.session.add(new_story)
            sub.status = "E'lon qilindi"
            db.session.commit()
            if sub.telegram_id:
                try:
                    send_to_user(sub.telegram_id, f"Tabriklaymiz! '{sub.title}' hikoyangiz kutubxonaga elon qilindi!")
                except:
                    pass
            flash("Elon qilindi", "success")
    elif action == 'reject':
        sub.status = "Rad etildi"
        db.session.commit()
        if sub.telegram_id:
            try:
                send_to_user(sub.telegram_id, f"Afsuski, '{sub.title}' hikoyangiz hozirda elon qilinmadi.")
            except:
                pass
        flash("Rad etildi", "success")
    return redirect('/brainn-hr-admin-2026')

@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if data and 'callback_query' in data:
        cq = data['callback_query']
        cb_data = cq.get('data','')
        chat_id = cq['message']['chat']['id']
        if str(chat_id) != str(Config.ADMIN_TELEGRAM_ID):
            return jsonify({"ok":True})
        if cb_data.startswith('approve_'):
            sid = int(cb_data.split('_')[1])
            sub = Submission.query.get(sid)
            if sub and sub.status != "E'lon qilindi":
                new_story = Story(
                    title=sub.title or "Sarlavhasiz", 
                    content=sub.content,
                    summary=sub.content[:150], 
                    category="hayotiy saboqlar",
                    image_url=sub.image_url,
                    date=date.today(), 
                    is_published=True, 
                    author_name=sub.author_name, 
                    is_user_submitted=True
                )
                db.session.add(new_story)
                sub.status = "E'lon qilindi"
                db.session.commit()
                if sub.telegram_id:
                    try:
                        send_to_user(sub.telegram_id, "Hikoyangiz elon qilindi!")
                    except:
                        pass
        elif cb_data.startswith('reject_'):
            sid = int(cb_data.split('_')[1])
            sub = Submission.query.get(sid)
            if sub:
                sub.status = "Rad etildi"
                db.session.commit()
                if sub.telegram_id:
                    try:
                        send_to_user(sub.telegram_id, "Hikoyangiz rad etildi.")
                    except:
                        pass
    return jsonify({"ok":True})

@app.route('/api/init-db')
def init_db_route():
    db.create_all()
    if Story.query.count()==0:
        demo = Story(
            title="Bugungi kunning qadri", 
            content="Bir kuni dono bobodan sorashdi... Hayotning eng qimmatli lahzasi qaysi? Bobo jilmaydi va dedi: Bugun. Kecha otdi, ertaga hali kelmadi. Bor narsa - bugun.\n\nHar kuni bir hikoya - har kuni bir saboq.", 
            summary="Bugunni qadrlash haqida", 
            category="motivatsiya", 
            image_url="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800",
            date=date.today(), 
            is_published=True
        )
        db.session.add(demo)
        db.session.commit()
    return "DB tayyor"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)