import os
import sys

# Yo'lni sozlash
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date, datetime

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
                flash("Hikoyangiz qabul qilindi!", "success")
        except Exception as e:
            print(e)
        return redirect(url_for('yuborish'))
    return render_template('yuborish.html')

@app.route('/sevimlilar')
def sevimlilar():
    return render_template('sevimlilar.html')

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

# >>> MUHIM - RAD / E'LON QILISH ROUTELARI - MANA SHU YETISHMAYOTGAN EDI <<<
@app.route('/admin/submission/<int:id>/<action>')
def admin_sub_action(id, action):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    try:
        sub = Submission.query.get_or_404(id)
        if action == 'approve' or action == 'elon':
            # Allaqachon bormi tekshirish
            exists = Story.query.filter_by(content=sub.content).first()
            if not exists:
                new_story = Story(
                    title=sub.title or "Sarlavhasiz", 
                    content=sub.content,
                    summary=sub.content[:150], 
                    category=sub.category or "hayotiy saboqlar",
                    image_url=sub.image_url or "https://images.unsplash.com/photo-1501504905252-473cbee65f87?w=800",
                    date=date.today(), 
                    is_published=True, 
                    author_name=sub.author_name, 
                    is_user_submitted=True
                )
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
    except Exception as e:
        print(e)
    return redirect('/brainn-hr-admin-2026/dashboard')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/')

@app.route('/api/init')
def init_db():
    try:
        db.create_all()
        return "DB tayyor! <a href='/'>Bosh sahifa</a> | <a href='/brainn-hr-admin-2026/dashboard'>Admin</a>"
    except Exception as e:
        return f"Xato: {e}"
