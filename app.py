from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fab_rental_jalgaon_2026_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fab_rental.db'
# MySQL option: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:PASSWORD@localhost/fab_rental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
os.makedirs('uploads', exist_ok=True)

from models import db, User, Cloth, Booking
db.init_app(app)

# ── HELPERS ──
def allowed_file(f): return '.' in f and f.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def get_cart():
    return session.get('cart', {})

def get_cart_count():
    return len(session.get('cart', {}))

@app.context_processor
def inject_globals():
    """Auto-inject cart_count into every template — no need to pass manually."""
    return dict(cart_count=get_cart_count())

def login_required(f):
    @wraps(f)
    def dec(*a,**k):
        if 'user_email' not in session:
            flash('Please login first.','warning')
            return redirect(url_for('login'))
        return f(*a,**k)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a,**k):
        if 'user_email' not in session:
            flash('Please login first.','warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required!','danger')
            return redirect(url_for('home'))
        return f(*a,**k)
    return dec

# ── SEED DATA ──
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        if not User.query.filter_by(email='admin@fab.com').first():
            db.session.add(User(
                name='Admin', email='admin@fab.com',
                password_hash=generate_password_hash('admin123'),
                phone='9529770750', role='admin'
            ))

        if Cloth.query.count() == 0:
            clothes = [
                # ── WOMEN: LEHENGAS ──
                Cloth(title='Green Multi-Colored Lehenga Set', category='Women', cloth_type='Lehenga', size='M',
                      price_per_day=4800, occasion='Sangeet',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/f9dac09b-f090-45d6-ba5d-bf8fa0e1880d.jpeg',
                      description='Vibrant green multi-colored lehenga with exquisite embroidery. Perfect for Sangeet and Mehendi.'),
                Cloth(title='Baby Pink Bridal Lehenga', category='Women', cloth_type='Lehenga', size='S',
                      price_per_day=9500, occasion='Wedding',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/66ad375f-92c8-4932-9e97-258ee941c2de.jpeg',
                      description='Dreamy baby pink lehenga with gold embellishments. A true princess look for the wedding day.'),
                Cloth(title='White Shrwani', category='Men', cloth_type='Sherwani', size='XXL',
                      price_per_day=8500, occasion='Wedding',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/d682a310-edbc-47dc-bab5-a00a4e2ebb04.jpeg',
                      description='Stunning deep White Groom Sherwani with heavy zardozi embroidery and real work.'),
                Cloth(title='Black Bandhgala', category='Men', cloth_type=' Bandhgala', size='L',
                      price_per_day=7500, occasion='Wedding',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/43f75914-b5d3-4546-8d03-f7dac2001708.jpeg',
                      description='Exquisite Black Bandhgala For Wedding With Attractive And Fitted.'),
                Cloth(title='Marron Jacket ', category='Men', cloth_type='Jackets', size='S',
                      price_per_day=4200, occasion='Reception',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/662104a5-efde-43be-9806-f4db6440465d.jpeg',
                      description='Ethereal Marron Jacket Suitable in every Outfit and asthetic way.'),
                # ── WOMEN: ANARKALI ──
                Cloth(title='Baby Pink Dress', category='Women', cloth_type='Dress', size='XL',
                      price_per_day=5500, occasion='Sangeet',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/fe22fcdd-27c3-4d05-a679-f854fb13691c.jpeg',
                      description='Yellow and pink multi-colored anarkali. Stunning floor-length silhouette.'),
                Cloth(title='baby pink two piece', category='Women', cloth_type='Lehenga', size='XXL',
                      price_per_day=3800, occasion='Party',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/27df7fff-e58d-41b7-ad18-9381dfdc1e81.jpeg',
                      description='Floor-length royal blue anarkali with gold embroidery and perfectly flared silhouette.'),
                Cloth(title='White Shirt With Grey Pant And Jacket', category='Men', cloth_type='Shirt', size='S',
                      price_per_day=4200, occasion='Cocktail',
                      image='https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/86a28694-df7a-4f82-b9df-5439f9c250e0.jpeg',
                      description='Rich White Cotton Shirt with intricate thread and sequin Grey Pant And Jacket.'),
                # ── WOMEN: SAREE ──
                Cloth(title='Kanjeevaram Red Silk Saree', category='Women', cloth_type='Saree', size='Free',
                      price_per_day=2800, occasion='Wedding',
                      image='https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=800&q=90&fit=crop&crop=top',
                      description='Luxurious Kanjeevaram pure silk saree with wide golden zari border.'),
                Cloth(title='Teal Embroidered Saree', category='Women', cloth_type='Saree', size='Free',
                      price_per_day=3200, occasion='Reception',
                      image='https://images.unsplash.com/photo-1583391733981-8498408ee4b7?w=800&q=90&fit=crop&crop=top',
                      description='Gorgeous teal saree with heavy embroidered border. Graceful and stunning.'),
                # ── WOMEN: GOWN ──
                Cloth(title='Sea Green Embellished Gown', category='Women', cloth_type='Gown', size='M',
                      price_per_day=3500, occasion='Cocktail',
                      image='https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&q=90&fit=crop&crop=top',
                      description='Sea green one-shoulder embellished gown — effortlessly glamorous for evenings.'),
                Cloth(title='Black Sequin Side-Slit Gown', category='Women', cloth_type='Gown', size='M',
                      price_per_day=3500, occasion='Cocktail',
                      image='https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=800&q=90&fit=crop&crop=top',
                      description='Classic black sequinned gown with a dramatic side slit.'),
                # ── MEN: SHERWANI ──
                Cloth(title='Royal Black Sherwani', category='Men', cloth_type='Sherwani', size='L',
                      price_per_day=5200, occasion='Wedding',
                      image='https://images.unsplash.com/photo-1610694518607-7ea2697a640e?w=800&q=90&fit=crop&crop=top',
                      description='Majestic black sherwani with intricate gold thread embroidery. Comes with churidar and dupatta.'),
                Cloth(title='Off-White Bridal Sherwani', category='Men', cloth_type='Sherwani', size='M',
                      price_per_day=5800, occasion='Wedding',
                      image='https://images.unsplash.com/photo-1594938298603-c8148c4b5696?w=800&q=90&fit=crop&crop=top',
                      description='Pristine off-white sherwani with subtle silver embroidery — perfect groom look.'),
                Cloth(title='Navy Blue Sherwani', category='Men', cloth_type='Sherwani', size='XL',
                      price_per_day=4800, occasion='Reception',
                      image='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=90&fit=crop&crop=top',
                      description='Deep navy sherwani with gold embroidered collar and cuffs.'),
                # ── MEN: BANDHGALA ──
                Cloth(title='Sky Blue Bandhgala Suit', category='Men', cloth_type='Bandhgala', size='M',
                      price_per_day=3800, occasion='Reception',
                      image='https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=800&q=90&fit=crop&crop=top',
                      description='Contemporary powder blue bandhgala with subtle floral embroidery.'),
                Cloth(title='Charcoal Grey Bandhgala', category='Men', cloth_type='Bandhgala', size='L',
                      price_per_day=3400, occasion='Cocktail',
                      image='https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=800&q=90&fit=crop&crop=top',
                      description='Sleek charcoal grey bandhgala suit — smart, modern and incredibly versatile.'),
                # ── MEN: KURTA ──
                Cloth(title='Ivory Silk Kurta Set', category='Men', cloth_type='Kurta', size='L',
                      price_per_day=1800, occasion='Sangeet',
                      image='https://images.unsplash.com/photo-1583231682454-25f5a79e7e2d?w=800&q=90&fit=crop&crop=top',
                      description='Elegant ivory silk kurta with straight-cut pajama. Perfect for Sangeet and Haldi.'),
                Cloth(title='Maroon Nehru Jacket Set', category='Men', cloth_type='Kurta', size='M',
                      price_per_day=2200, occasion='Wedding',
                      image='https://images.unsplash.com/photo-1480455624313-e29b44bbfde1?w=800&q=90&fit=crop&crop=top',
                      description='Rich maroon kurta with embroidered Nehru jacket. A complete festive ensemble.'),
            ]
            for c in clothes:
                db.session.add(c)

        db.session.commit()
        print("✅ DB ready! Login: admin@fab.com / admin123")

# ── AUTH ROUTES ──
@app.route('/')
def index():
    return redirect(url_for('home') if 'user_email' in session else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_email' in session: return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_email'] = user.email
            session['user_name']  = user.name
            session['role']       = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_email' in session: return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        phone = request.form.get('phone','').strip()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm','')
        if not name or not email or not password:
            flash('All fields required.','danger')
        elif password != confirm:
            flash('Passwords do not match.','danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.','danger')
        else:
            db.session.add(User(name=name, email=email, phone=phone,
                                password_hash=generate_password_hash(password), role='user'))
            db.session.commit()
            flash('Account created! Please login.','success')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.','success')
    return redirect(url_for('login'))

# ── MAIN ROUTES ──
@app.route('/home')
@login_required
def home():
    featured = Cloth.query.filter_by(available=True).limit(8).all()
    total    = Cloth.query.filter_by(available=True).count()
    return render_template('home.html', featured=featured, total_clothes=total)

@app.route('/dashboard')
@login_required
def dashboard():
    category   = request.args.get('category','all')
    occasion   = request.args.get('occasion','all')
    cloth_type = request.args.get('type','all')
    search     = request.args.get('search','').strip()
    sort       = request.args.get('sort','newest')

    q = Cloth.query.filter_by(available=True)
    if category   != 'all': q = q.filter_by(category=category)
    if occasion   != 'all': q = q.filter_by(occasion=occasion)
    if cloth_type != 'all': q = q.filter_by(cloth_type=cloth_type)
    if search: q = q.filter(Cloth.title.ilike(f'%{search}%'))
    if sort == 'price_low':  q = q.order_by(Cloth.price_per_day.asc())
    elif sort == 'price_high': q = q.order_by(Cloth.price_per_day.desc())
    else: q = q.order_by(Cloth.id.desc())

    clothes = q.all()
    return render_template('dashboard.html', clothes=clothes,
        category=category, occasion=occasion, cloth_type=cloth_type,
        search=search, sort=sort, total=len(clothes))



# ── CART ROUTES ──
@app.route('/cart/add/<int:cloth_id>', methods=['POST'])
@login_required
def cart_add(cloth_id):
    cloth = Cloth.query.get_or_404(cloth_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not cloth.available:
        if is_ajax: return jsonify(success=False, message='Item unavailable.')
        flash('Item unavailable.', 'warning')
        return redirect(request.referrer or url_for('home'))
    cart = session.get('cart', {})
    key = str(cloth_id)
    if key in cart:
        if is_ajax: return jsonify(success=False, message='Already in cart!', cart_count=len(cart))
        flash('Already in cart!', 'info')
        return redirect(request.referrer or url_for('home'))
    cart[key] = {
        'title': cloth.title, 'price': cloth.price_per_day,
        'image': cloth.image, 'category': cloth.category,
        'cloth_type': cloth.cloth_type, 'size': cloth.size,
        'occasion': cloth.occasion, 'days': 3
    }
    session['cart'] = cart
    session.modified = True
    if is_ajax: return jsonify(success=True, message='Added!', cart_count=len(cart))
    flash(f'✅ "{cloth.title}" cart mein add hua!', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route('/cart')
@login_required
def view_cart():
    cart = get_cart()
    items, grand_total = [], 0
    for cid, item in cart.items():
        subtotal = item['price'] * item['days']
        grand_total += subtotal
        items.append({**item, 'cloth_id': int(cid), 'subtotal': subtotal})
    return render_template('cart.html', items=items, grand_total=grand_total)

@app.route('/cart/update/<int:cloth_id>', methods=['POST'])
@login_required
def cart_update(cloth_id):
    cart = session.get('cart', {})
    key = str(cloth_id)
    days = max(1, min(int(request.form.get('days', 3)), 30))
    if key in cart:
        cart[key]['days'] = days
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:cloth_id>')
@login_required
def cart_remove(cloth_id):
    cart = session.get('cart', {})
    cart.pop(str(cloth_id), None)
    session['cart'] = cart
    session.modified = True
    flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/clear')
@login_required
def cart_clear():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/checkout', methods=['POST'])
@login_required
def checkout_cart():
    cart = session.get('cart', {})
    if not cart:
        flash('Cart khali hai!', 'warning')
        return redirect(url_for('view_cart'))
    booked, skipped = [], []
    for cid, item in cart.items():
        cloth = Cloth.query.get(int(cid))
        if not cloth or not cloth.available:
            skipped.append(item['title']); continue
        days = item.get('days', 3)
        db.session.add(Booking(user_email=session['user_email'], cloth_id=int(cid),
                               days=days, total_price=days*cloth.price_per_day, status='Confirmed'))
        cloth.available = False
        booked.append(cloth.title)
    db.session.commit()
    session.pop('cart', None)
    if booked: flash(f'🎉 {len(booked)} item(s) successfully booked!', 'success')
    if skipped: flash(f'⚠️ {len(skipped)} item(s) unavailable the skipped.', 'warning')
    return redirect(url_for('my_bookings'))

@app.route('/book/<int:cloth_id>', methods=['GET','POST'])
@login_required
def book(cloth_id):
    cloth = Cloth.query.get_or_404(cloth_id)
    if not cloth.available:
        flash('Sorry, this item is already rented out.','danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        days = int(request.form.get('days', 4))
        days = max(1, days)
        total_price = days * cloth.price_per_day
        db.session.add(Booking(user_email=session['user_email'], cloth_id=cloth_id,
                               days=days, total_price=total_price, status='Confirmed'))
        cloth.available = False
        db.session.commit()
        flash(f'✅ Booked "{cloth.title}" for {days} days! Total: ₹{int(total_price)}','success')
        return redirect(url_for('my_bookings'))
    return render_template('book.html', cloth=cloth, now=datetime.now())

@app.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_email=session['user_email'])\
                            .order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if b.user_email != session['user_email']:
        flash('Not authorized.','danger')
        return redirect(url_for('my_bookings'))
    b.status = 'Cancelled'
    b.cloth.available = True
    db.session.commit()
    flash('Booking cancelled.','success')
    return redirect(url_for('my_bookings'))

# ── ADMIN ROUTES ──
@app.route('/admin')
@admin_required
def admin_panel():
    all_clothes  = Cloth.query.order_by(Cloth.id.desc()).all()
    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    all_users    = User.query.order_by(User.id.desc()).all()
    revenue = sum(b.total_price for b in all_bookings if b.status=='Confirmed')
    return render_template('admin.html', clothes=all_clothes, bookings=all_bookings,
                           users=all_users, total_revenue=revenue)

@app.route('/add-cloth', methods=['GET','POST'])
@admin_required
def add_cloth():
    if request.method == 'POST':
        image_path = request.form.get('image_url','').strip()
        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            fn = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            image_path = url_for('uploaded_file', filename=fn)
        if not image_path:
            image_path = 'https://images.unsplash.com/photos/1612935532258-8b6e0d2ee0a8?w=600'
        cloth = Cloth(
            title=request.form.get('title','').strip(),
            category=request.form.get('category'),
            cloth_type=request.form.get('cloth_type',''),
            size=request.form.get('size'),
            price_per_day=float(request.form.get('price',0)),
            occasion=request.form.get('occasion','Wedding'),
            description=request.form.get('description',''),
            image=image_path
        )
        db.session.add(cloth)
        db.session.commit()
        flash(f'"{cloth.title}" added!','success')
        return redirect(url_for('admin_panel'))
    return render_template('add_cloth.html')

@app.route('/edit-cloth/<int:cloth_id>', methods=['GET','POST'])
@admin_required
def edit_cloth(cloth_id):
    cloth = Cloth.query.get_or_404(cloth_id)
    if request.method == 'POST':
        cloth.title       = request.form.get('title', cloth.title)
        cloth.category    = request.form.get('category', cloth.category)
        cloth.cloth_type  = request.form.get('cloth_type', cloth.cloth_type)
        cloth.size        = request.form.get('size', cloth.size)
        cloth.price_per_day = float(request.form.get('price', cloth.price_per_day))
        cloth.occasion    = request.form.get('occasion', cloth.occasion)
        cloth.description = request.form.get('description', cloth.description)
        url = request.form.get('image_url','').strip()
        if url: cloth.image = url
        db.session.commit()
        flash('Cloth updated!','success')
        return redirect(url_for('admin_panel'))
    return render_template('edit_cloth.html', cloth=cloth)

@app.route('/delete-cloth/<int:cloth_id>')
@admin_required
def delete_cloth(cloth_id):
    cloth = Cloth.query.get_or_404(cloth_id)
    db.session.delete(cloth)
    db.session.commit()
    flash('Cloth deleted.','success')
    return redirect(url_for('admin_panel'))

@app.route('/toggle-available/<int:cloth_id>')
@admin_required
def toggle_available(cloth_id):
    cloth = Cloth.query.get_or_404(cloth_id)
    cloth.available = not cloth.available
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    print("🚀 Fab Rental → http://127.0.0.1:5000")
    app.run(debug=True, port=5000)                                                                                                                                                                  
    