from datetime import datetime
from catalog import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import desc

Base = declarative_base()


class Item(db.Model):
    """An Item in the catalog database.

    Items titles have to be unique within their category.
    The item category is just a string and to create a new category
    the only thing needed is to create a new item with that category.
    """
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    category = db.Column(db.String(80))
    inserted_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, title, description, category):
        """Creates a new item.

        Args:
            title (srt): the item title
            description (srt): the item description
            category (str): the item category
        """
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
    """A category in the catalog database.

    Categories are a product of the `Items` in the database, they
    are not created directly. Instead, to create a new category you
    should insert a new `Item` in that category.

    Example:

        Item(title='title', description='desc', category='examples')

        After inserting this item in the database, the category `examples`
        will be available.
    """
    __table__ = db.Table('categories',
                         Base.metadata,
                         db.Column('category', db.String(80), primary_key=True),
                         autoload=True,
                         autoload_with=db.engine)

    def item_count(self):
        return db.session.query(Item).filter(Item.category == self.category).count()