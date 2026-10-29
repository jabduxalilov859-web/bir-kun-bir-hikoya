
from app import app, db, Story
from datetime import date

with app.app_context():
    stories = Story.query.all()
    print(f"Jami hikoyalar: {len(stories)}")
    for s in stories:
        print(f"  ID:{s.id} | {s.title} | published={s.is_published} | date={s.date}")
        s.is_published = True
    
    # Agar umuman hikoya yoq bolsa, bitta yaratamiz
    if len(stories) == 0:
        print("Hikoya yoq ekan, yangisini yaratamiz...")
        new_story = Story(
            title="Bugungi kunning qadri",
            summary="Vaqt - qaytarib bolmaydigan eng qimmat boylik",
            content="Bir kuni dono bobo nevarasiga dedi: Hayotda eng qimmat narsa vaqt. Uni qaytarib bolmaydi. Bugun qilgan kichik ishing ertaga katta natija beradi.",
            category="hayotiy saboqlar",
            image_url="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800",
            date=str(date.today()),
            is_published=True,
            views=0
        )
        db.session.add(new_story)
        print("Yangi hikoya yaratildi!")
    
    db.session.commit()
    
    stories = Story.query.filter_by(is_published=True).all()
    print(f"Endi e'lon qilingan: {len(stories)} ta")
    print("Tayyor! Endi python app.py ni qayta ishga tushiring va CTRL+F5 bosing!")

