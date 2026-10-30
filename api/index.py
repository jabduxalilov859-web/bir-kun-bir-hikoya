import sys
import os

# Asosiy papkani yo'lga qo'shish
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)

from app import app

# Vercel faqat /tmp ga yoza oladi - baza uchun
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/bir_kun_bir_hikoya.db'

# Baza yaratish
with app.app_context():
    from models import db
    from models import Story
    from datetime import date
    
    db.create_all()
    
    # Agar baza bo'sh bo'lsa, demo hikoya qo'shish
    if Story.query.count() == 0:
        demo = Story(
            title="Bugungi kunning qadri",
            content="Bir kuni dono bobodan so'rashdi: Hayotning eng qimmatli lahzasi qaysi? Bobo jilmaydi va dedi: Bugun. Kecha o'tdi, ertaga hali kelmadi. Bor narsa - bugun.\n\nHar kuni bir hikoya - har kuni bir saboq.",
            summary="Bugunni qadrlash haqida",
            category="motivatsiya",
            image_url="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800",
            date=date.today(),
            is_published=True
        )
        db.session.add(demo)
        db.session.commit()

# Vercel uchun kerak
app = app
