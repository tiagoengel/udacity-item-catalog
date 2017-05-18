from datetime import datetime
from catalog import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import desc

Base = declarative_base()


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    category = db.Column(db.String(80))
    inserted_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, title, description, category):
        self.title = title
        self.description = description
        self.category = category

    @classmethod
    def latest_10(cls):
        return db.session.query(Item).order_by(desc(Item.inserted_at)).limit(10)

    @classmethod
    def list_by_category(cls, category):
        return db.session.query(Item).filter(Item.category == category).all()

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'title': self.title,
           'description': self.description,
           'id': self.id,
           'category': self.category
        }


class Category(Base):
    __table__ = db.Table('categories',
                         Base.metadata,
                         db.Column('category', db.String(80), primary_key=True),
                         autoload=True,
                         autoload_with=db.engine)

    def item_count(self):
        return db.session.query(Item).filter(Item.category == self.category).count()