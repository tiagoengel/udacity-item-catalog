import unittest
from sqlalchemy.exc import IntegrityError
from catalog.models import Item, Category
from catalog import db


def create_items():
    def create_item(idx):
        db.session.add(Item(title=('I%s' % idx),
                            description='desc',
                            category=('c%s' % (idx % 5))))

    [create_item(idx) for idx in range(0, 20)]
    db.session.commit()


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
        create_items()

        latest_10 = Item.latest_10()
        titles = [i.title for i in latest_10]
        expected = ['I19', 'I18', 'I17', 'I16', 'I15', 'I14', 'I13', 'I12', 'I11', 'I10']  # noqa

        self.assertEqual(titles, expected)

    def test_list_by_category(self):
        create_items()
        c1 = Item.list_by_category('c1')
        self.assertEqual(len(c1), 4)
        self.assertEqual(set([i.category for i in c1]), set(['c1']))


class CategoryTest(unittest.TestCase):
    def setUp(self):
        db.session.query(Item).delete()

    def test_keep_categories_in_sync_with_items(self):
        create_items()

        self.assertEqual(db.session.query(Category).count(), 5)

        db.session.query(Item).filter(Item.category == 'c4').delete()
        db.session.commit()

        self.assertEqual(db.session.query(Category).count(), 4)


