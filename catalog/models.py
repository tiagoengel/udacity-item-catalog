from catalog import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    category = db.Column(db.String(80))

    def __init__(self, title, description, category):
        self.title = title
        self.description = description
        self.category = category


class Category(Base):
    __table__ = db.Table('categories',
                         Base.metadata,
                         db.Column('category', db.String(80), primary_key=True),
                         autoload=True,
                         autoload_with=db.engine)
