import unittest
from sqlalchemy.exc import IntegrityError
from catalog.models import Item, Category, User
from catalog import db


def create_items(user):
    def create_item(idx):
        category_desc = ('c%s' % (idx % 5))
        category = db.session.query(Category).filter(
            Category.description == category_desc
        ).first()
        if not category:
            category = Category(description=category_desc)
            db.session.add(category)

        db.session.add(Item(title=('I%s' % idx),
                            description='desc',
                            user=user,
                            category=category))

    [create_item(idx) for idx in range(0, 20)]
    db.session.commit()


class ItemTest(unittest.TestCase):
    def setUp(self):
        db.session.rollback()
        db.session.query(Item).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.commit()
        self.user = User.get_or_create('test', '1')
        self.default_cat = Category(description='default')

    def test_can_create_an_item(self):
        db.session.add(Item(title='Foo',
                            description='bar',
                            category=self.default_cat,
                            user=self.user))
        db.session.commit()

        self.assertEqual(db.session.query(Item).count(), 1)

    def test_item_uniqueness(self):
        db.session.add(Item(title='Foo',
                            description='bar',
                            user=self.user,
                            category=self.default_cat))
        db.session.add(Item(title='Foo',
                            description='bar',
                            user=self.user,
                            category=self.default_cat))
        self.assertRaises(IntegrityError, db.session.commit)

    def test_list_latest_10(self):
        create_items(self.user)

        latest_10 = Item.latest_10()
        titles = [i.title for i in latest_10]
        expected = ['I19', 'I18', 'I17', 'I16', 'I15', 'I14', 'I13', 'I12', 'I11', 'I10']  # noqa

        self.assertEqual(titles, expected)

    def test_list_by_category(self):
        create_items(self.user)
        c1 = Item.list_by_category('c1')
        self.assertEqual(len(c1), 4)
        self.assertEqual(set([i.category.description for i in c1]), set(['c1']))


class CategoryTest(unittest.TestCase):
    def setUp(self):
        db.session.rollback()
        db.session.query(Item).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.commit()
        self.user = User.get_or_create('test', '1')

    def test_item_count(self):
        create_items(self.user)

        category = db.session.query(Category).filter(
            Category.description == 'c4'
        ).first()
        self.assertEqual(category.item_count(), 4)

        item = db.session.query(Item).join(Category).filter(
            Category.description == 'c4'
        ).first()
        db.session.delete(item)
        db.session.commit()

        self.assertEqual(category.item_count(), 3)


