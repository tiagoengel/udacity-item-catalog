from datetime import datetime
from catalog import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import desc
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(db.Model):
    """An User in the catalog dadabase.

    Users are created based on a oauth response object
    containing user information, since that information
    can change only the oauth user id (generally email)
    and provider are saved in the database.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(80))
    provider_user_id = db.Column(db.String(80))
    inserted_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, provider, provider_user_id):
        """Creates a new user.

        Args:
            provider (srt): the authentication provider name
            provider_user_id (srt): the user id in that provider
        """
        self.provider = provider
        self.provider_user_id = provider_user_id

    @classmethod
    def get_or_create(cls, provider, id):
        user = db.session.query(User).filter(
            User.provider == provider, User.provider_user_id == id
        ).first()

        if not user:
            user = User(provider=provider,
                        provider_user_id=id)

            db.session.add(user)
            db.session.commit()

        return user


class Category(db.Model):
    """A category in the catalog database.

    Categories are just strings used to group items, they
    don't really need to be in a separated table but they
    are just for the sake of using SqlAlchemy relationships.
    """

    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    inserted_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, description):
        """Creates a new category.

        Args:
            description (srt): the category description
        """
        self.description = description

    def item_count(self):
        return len(self.items)

    @classmethod
    def get_or_create(cls, description):
        category = db.session.query(Category).filter(
            Category.description == description
        ).first()

        if not category:
            category = Category(description=description)

            db.session.add(category)
            db.session.commit()

        return category

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'description': self.description,
           'id': self.id
        }

    def __str__(self):
        return self.description


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
    inserted_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = relationship(Category, back_populates='items')

    def __init__(self, title, description, category, user):
        """Creates a new item.

        Args:
            title (srt): the item title
            description (srt): the item description
            category (str): the item category
        """
        self.title = title
        self.description = description
        self.category = category
        self.user = user

    def owned_by(self, user_id):
        return self.user_id == user_id

    @classmethod
    def latest_10(cls):
        return db.session.query(Item).order_by(desc(Item.inserted_at)).limit(10)

    @classmethod
    def list_by_category(cls, category):
        return db.session.query(Item).join(Category).filter(
            Category.description == category
        ).all()

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'title': self.title,
           'description': self.description,
           'id': self.id,
           'category': self.category.description
        }


# Just because during category definition item is not defined...
Category.items = relationship('Item',
                              order_by=desc(Item.inserted_at),
                              back_populates='category')
