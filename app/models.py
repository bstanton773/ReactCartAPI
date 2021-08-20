import base64
import os
from sqlalchemy.orm import backref
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


cart = db.Table('cart',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    products = db.relationship('Product', secondary='cart', backref=db.backref('users', lazy='dynamic'))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.commit()
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


    def to_dict(self):
        user_dict = dict()
        for attr in ['id', 'first_name', 'last_name', 'username', 'email']:
            user_dict[attr] = getattr(self, attr)
        user_dict['products'] = [p.to_dict() for p in self.products]
        return user_dict

    def from_dict(self, data):
        for attr in ['first_name', 'last_name', 'username', 'email', 'password']:
            if attr == 'password':
                setattr(self, attr, self.hash_password(data[attr]))
            else:
                setattr(self, attr, data[attr])
        db.session.add(self)
        db.session.commit()

    def add_product(self, product):
        self.products.append(product)
        db.session.commit()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(10))
    image_url = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    

    def to_dict(self):
        prod_dict = dict()
        for attr in ['id', 'name', 'description', 'price', 'image_url', 'date_created']:
            if isinstance(type(getattr(self, attr)), db.Model):
                prod_dict[attr] = getattr(self, attr.to_dict())
            else:
                prod_dict[attr] = getattr(self, attr)
        return prod_dict

    def from_dict(self, data):
        for attr in ['name', 'description', 'price', 'image_url']:
            setattr(self, attr, data[attr])
        db.session.add(self)
        db.session.commit()
