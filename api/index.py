import os
import sys

# Muhim - yo'lni to'g'ri sozlash
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date

# Flask app - template va static papkalarni to'g'ri ko'rsatish
app = Flask(__name__, 
            template_folder=os.path.join(ROOT, 'templates'),
            static_folder=os.path.join(ROOT, 'static'))

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'bir-kun-2026-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Models ni import qilish
try:
    from models import db, Story, Submission
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Demo qo'shish
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

CATEGORIES = ["motivatsiya","hayotiy saboqlar","do'stlik","oila","muvaffaqiyat"]

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
        stories = Story.query.filter_by(is_published=True).all()
        return render_template('kutubxona.html', stories=stories, categories=CATEGORIES, selected_cat=None, q="")
    except:
        return "Baza yaratilmoqda..."

@app.route('/hikoya/<int:id>')
def hikoya_detail(id):
    story = Story.query.get_or_404(id)
    return render_template('hikoya.html', story=story)

@app.route('/yuborish', methods=['GET','POST'])
def yuborish():
    if request.method == 'POST':
        try:
            title = request.form.get('title', 'Sarlavhasiz')
            content = request.form.get('content')
            if content:
                sub = Submission(title=title, content=content, status="Ko'rib chiqilmoqda")
                db.session.add(sub)
                db.session.commit()
        except:
            pass
        return redirect(url_for('yuborish'))
    return render_template('yuborish.html')

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
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        total = Story.query.count()
        subs = Submission.query.order_by(Submission.id.desc()).limit(20).all()
        return render_template('admin_dashboard.html', total_stories=total, total_published=total, total_subs=len(subs), pending=0, total_users=0, subs=subs, categories=CATEGORIES)
    except Exception as e:
        return f"Admin xato: {e}"

@app.route('/api/init')
def init_db():
    try:
        db.create_all()
        return "DB tayyor! <a href='/'>Bosh sahifa</a>"
    except Exception as e:
        return f"Xato: {e}"

# Vercel uchun MUHIM - app o'zgaruvchisi
# Hech qanday if __name__ == '__main__' kerak emas
