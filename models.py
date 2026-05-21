from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ══════════════════════════════════════════
#   USER MODEL
# ══════════════════════════════════════════
class User(db.Model):
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone         = db.Column(db.String(15), default='')
    role          = db.Column(db.String(20), default='user')   # 'user' or 'admin'
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

# ══════════════════════════════════════════
#   CLOTH MODEL
# ══════════════════════════════════════════
class Cloth(db.Model):
    __tablename__ = 'cloth'

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    category      = db.Column(db.String(50), nullable=False)   # 'Women' / 'Men'
    cloth_type    = db.Column(db.String(80), default='')       # Saree, Lehenga, Sherwani…
    size          = db.Column(db.String(20), nullable=False)   # XS S M L XL XXL
    price_per_day = db.Column(db.Float, nullable=False)
    image         = db.Column(db.String(500), nullable=False)  # URL or upload path
    occasion      = db.Column(db.String(50), default='Wedding')
    description   = db.Column(db.Text, default='')
    available     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cloth {self.title}>'

# ══════════════════════════════════════════
#   BOOKING MODEL
# ══════════════════════════════════════════
class Booking(db.Model):
    __tablename__ = 'booking'

    id          = db.Column(db.Integer, primary_key=True)
    user_email  = db.Column(db.String(100), nullable=False)
    cloth_id    = db.Column(db.Integer, db.ForeignKey('cloth.id'), nullable=False)
    cloth       = db.relationship('Cloth', backref='bookings')
    days        = db.Column(db.Integer, default=3)
    total_price = db.Column(db.Float, nullable=False)
    status      = db.Column(db.String(30), default='Confirmed')  # Confirmed / Cancelled
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.id} by {self.user_email}>'