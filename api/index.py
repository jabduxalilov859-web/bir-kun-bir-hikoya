import os
import sys

# Yo'lni sozlash - MUHIM!
root_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_path)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import date, datetime

app = Flask(__name__, 
            template_folder=os.path.join(root_path, 'templates'),
            static_folder=os.path.join(root_path, 'static'))

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'bir-kun-bir-hikoya-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/bir_kun_bir_hikoya.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models AFTER app config
from models import db, Story, Submission, User
db.init_app(app)

CATEGORIES = ["motivatsiya","hayotiy saboqlar","do'stlik","oila","muvaffaqiyat","shaxsiy rivojlanish"]

# Baza yaratish - har safar tekshirish
with app.app_context():
    try:
        db.create_all()
        if Story.query.count() == 0:
            demo = Story(
                title="Bugungi kunning qadri",
                content="Bir kuni dono bobodan so'rashdi: Hayotning eng qimmatli lahzasi qaysi? Bobo dedi: Bugun. Kecha o'tdi, ertaga hali kelmadi.",
                summary="Bugun haqida",
                category="motivatsiya",
                image_url="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800",
                date=date.today(),
                is_published=True
            )
            db.session.add(demo)
            db.session.commit()
    except Exception as e:
        print(f"DB xato: {e}")

@app.route('/')
def index():
    try:
        today = date.today()
        bugungi = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).first()
        latest = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).limit(20).all()
        return render_template('index.html', today_story=bugungi, bugungi=bugungi, stories=latest, latest=latest, recent_stories=latest, categories=CATEGORIES)
    except Exception as e:
        return f"<h1>Sayt ishga tushmoqda...</h1><p>{str(e)}</p><p><a href='/api/init-db'>Bazani yaratish</a></p>"

@app.route('/kutubxona')
def kutubxona():
    try:
        stories = Story.query.filter_by(is_published=True).order_by(Story.id.desc()).all()
        return render_template('kutubxona.html', stories=stories, categories=CATEGORIES, selected_cat=None, q="")
    except Exception as e:
        return f"Xato: {e}"

@app.route('/hikoya/<int:id>')
def hikoya_detail(id):
    story = Story.query.get_or_404(id)
    return render_template('hikoya.html', story=story)

@app.route('/yuborish', methods=['GET','POST'])
def yuborish():
    if request.method == 'POST':
        try:
            title = request.form.get('title') or "Sarlavhasiz"
            content = request.form.get('content')
            sub = Submission(title=title, content=content, status="Ko'rib chiqilmoqda")
            db.session.add(sub)
            db.session.commit()
            flash("Qabul qilindi!", "success")
        except Exception as e:
            print(f"Yuborish xato: {e}")
        return redirect(url_for('yuborish'))
    return render_template('yuborish.html')

@app.route('/sevimlilar')
def sevimlilar():
    return render_template('sevimlilar.html')

@app.route('/loyiha-haqida')
def haqida():
    return render_template('haqida.html')

@app.route('/api/init-db')
def init_db_route():
    try:
        db.create_all()
        return "DB tayyor! <a href='/'>Bosh sahifaga</a>"
    except Exception as e:
        return f"Xato: {e}"

# Vercel uchun - bu o'zgaruvchi SHART!
# Vercel app o'zgaruvchisini qidiradi
