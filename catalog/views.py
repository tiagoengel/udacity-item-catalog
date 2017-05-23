import json

from flask import make_response, session, request, redirect
from flask import render_template, url_for, jsonify, flash
from sqlalchemy.exc import IntegrityError

from catalog import app, db
from catalog.models import Item, Category, User
from catalog.auth import oauth, providers


def protected_resource(owner_only=False, table=Item):
    """Decorator that protects a resource from being accessed
    by an unauthenticated user or unauthorized users.

    Args:
        owner_only (bool): indicates if authorization check should be performed.
        table (db.Model): the table to check if the resource provided in the
                          current url is owned by this user.

    Returns:
        a new function that first check if the user is authenticated
        and unauthorized before executing the actual function
    """
    def decorator(fn):
        def inner(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash(u'You need to login before accessing this resource',
                      'danger')
                return redirect('/')

            if owner_only:
                id = kwargs.get('id') or args.get(0)
                model = db.session.query(table).get(id)
                if not model.owned_by(user['local_id']):
                    flash(u"Only the resource's owner can execute this operation",  # noqa
                         'danger')
                    return redirect('/')

            return fn(*args, **kwargs)

        # Flask tracks functions by their name, we have
        # to keep the original name otherwise we'll run
        # into naming conflicts
        decorator.__name__ = fn.__name__
        inner.__name__ = fn.__name__
        return inner

    return decorator


def validates_required(data, field, errors):
    """Validates if a required field is present.

    Args:
        data (dict): data to check whether the field is present
        field (str): the field name
        errors (dict): dict where errors will be put

    Returns:
        `errors` containing `field` if `field` is not present
    """
    if not data.get(field):
        errors[field] = 'This field is required'

    return errors


def current_user():
    return db.session.query(User).get(session['user']['local_id'])


@app.route('/oauth-connect/<string:provider_name>', methods=['POST'])
def oauth_connect(provider_name):
    try:
        provider = getattr(providers, provider_name)
    except AttributeError:
        return make_response(
            json.dumps(dict(message='Provider not supported')), 401)

    data = request.get_json()
    flow = oauth.OauthFlow(provider=provider.__new__(provider))
    user = flow.authenticate(data['token'])
    user_data = user['user_data']
    user_id = user_data.get('email') or user_data.get('user_id')
    local_user = User.get_or_create(user['provider'], user_id)
    user['local_id'] = local_user.id
    session['user'] = user
    return ('', 204)


@app.route('/logout', methods=['GET'])
def disconnect():
    user = session['user']
    if not user:
        return redirect('/')

    provider = getattr(providers, user['provider'])
    flow = oauth.OauthFlow(provider=provider.__new__(provider))
    flow.revoke(user['access_token'], user['user_data']['user_id'])
    del session['user']

    return redirect('/')


@app.route('/items/create', methods=['POST'])
@protected_resource()
def create_item():
    data = request.form
    errors = {}
    validates_required(data, 'title', errors)
    validates_required(data, 'description', errors)
    validates_required(data, 'category', errors)

    if len(errors.keys()):
        return (render_template('new-item.html', errors=errors, item=data), 400)

    title = data['title']
    category = data['category']
    description = data['description']

    new_item = Item(title=title,
                    description=description,
                    category=Category.get_or_create(category),
                    user=current_user())
    try:
        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('show_item_page', item_id=new_item.id))
    except IntegrityError:
        errors['title'] = """
        There is already an item with this title/category in the database.
        Try a different title.
        """
        return (render_template('new-item.html', errors=errors, item=data), 400)


@app.route('/items/<int:id>/delete', methods=['POST'])
@protected_resource(owner_only=True)
def delete_item(id):
    item = db.session.query(Item).get(id)
    if not item:
        return ('', 404)

    category = item.category

    db.session.delete(item)
    db.session.commit()

    if category.item_count() == 0:
        db.session.delete(category)
        db.session.commit()

    return redirect('/')


@app.route('/items/<int:id>/update', methods=['POST'])
@protected_resource(owner_only=True)
def update_item(id):
    item = db.session.query(Item).get(id)
    if not item:
        return ('', 404)

    data = request.form
    errors = {}
    validates_required(data, 'title', errors)
    validates_required(data, 'description', errors)
    validates_required(data, 'category', errors)

    if len(errors.keys()):
        return (render_template('new-item.html',
                                errors=errors), 400)

    item.title = data['title']
    item.description = data['description']
    item.category = Category.get_or_create(data['category'])

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('show_item_page', item_id=item.id))


# PAGES
@app.route('/')
def index():
    latest_items = Item.latest_10()
    categories = db.session.query(Category).all()
    return render_template('index.html',
                           latest_items=latest_items,
                           categories=categories)


@app.route('/items/create')
@protected_resource()
def create_item_page():
    return render_template('new-item.html')


@app.route('/items/<int:item_id>/show')
def show_item_page(item_id):
    item = db.session.query(Item).get(item_id)
    if not item:
        return ('', 404)

    return render_template('show-item.html', item=item)


@app.route('/items/<int:id>/edit')
@protected_resource(owner_only=True)
def edit_item_page(id):
    item = db.session.query(Item).get(id)
    if not item:
        return ('', 404)

    return render_template('new-item.html', item=item)


# JSON endpoints
@app.route('/catalog/<string:category>/items.json')
def list_items_for_category(category):
    items = [i.serialize for i in Item.list_by_category(category)]
    return jsonify(items)


@app.route('/catalog/categories.json')
def list_categories():
    categories = [c.description for c in db.session.query(Category).all()]
    return jsonify(categories)


@app.route('/catalog.json')
def list_all():
    categories = db.session.query(Category).all()
    all_catalog = {}
    for c in categories:
        items = [i.serialize for i in Item.list_by_category(c.category)]
        all_catalog[c.category] = items

    return jsonify({'catalog': all_catalog})

