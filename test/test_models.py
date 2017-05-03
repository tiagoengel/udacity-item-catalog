import unittest
from sqlalchemy.exc import IntegrityError
from catalog.models import Item, Category
from catalog import db


class ItemTest(unittest.TestCase):
    def setUp(self):
        db.session.query(Item).delete()

    def test_can_create_an_item(self):
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.commit()

        self.assertEqual(db.session.query(Item).count(), 1)

    def test_item_uniqueness(self):
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        self.assertRaises(IntegrityError, db.session.commit)


class CategoryTest(unittest.TestCase):
    def setUp(self):
        db.session.query(Item).delete()

    def test_keep_categories_in_sync_with_items(self):
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.add(Item(title='Fo', description='bar', category='FooBar'))
        db.session.add(Item(title='Foo', description='bar', category='Foo'))
        db.session.commit()

        self.assertEqual(db.session.query(Category).count(), 2)

        db.session.query(Item).filter(Item.category == 'Foo').delete()
        db.session.commit()

        self.assertEqual(db.session.query(Category).count(), 1)


