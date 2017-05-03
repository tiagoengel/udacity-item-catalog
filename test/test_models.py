import unittest
from sqlalchemy.exc import IntegrityError
from catalog.models import Item, Category
from catalog import db


class ItemTest(unittest.TestCase):
    def setUp(self):
        db.session.rollback()
        db.session.query(Item).delete()
        db.session.commit()

    def test_can_create_an_item(self):
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.commit()

        self.assertEqual(db.session.query(Item).count(), 1)

    def test_item_uniqueness(self):
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        self.assertRaises(IntegrityError, db.session.commit)

    def test_list_latest_10(self):
        def create_item(idx):
            db.session.add(Item(title=('I%s' % idx),
                                description='desc',
                                category=('c%s' % (idx % 5))))
            db.session.commit()

        [create_item(idx) for idx in range(0, 20)]

        latest_10 = Item.latest_10()
        titles = [i.title for i in latest_10]
        expected = ['I19', 'I18', 'I17', 'I16', 'I15', 'I14', 'I13', 'I12', 'I11', 'I10']  # noqa

        self.assertEqual(titles, expected)


class CategoryTest(unittest.TestCase):
    def setUp(self):
        db.session.query(Item).delete()

    def test_keep_categories_in_sync_with_items(self):
        def create_item(idx):
            db.session.add(Item(title=('I%s' % idx),
                                description='desc',
                                category=('c%s' % (idx % 5))))

        [create_item(idx) for idx in range(0, 20)]
        db.session.commit()

        self.assertEqual(db.session.query(Category).count(), 5)

        db.session.query(Item).filter(Item.category == 'c4').delete()
        db.session.commit()

        self.assertEqual(db.session.query(Category).count(), 4)


