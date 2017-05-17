import json

from flask import make_response, session, request, redirect, render_template, url_for
from sqlalchemy.exc import IntegrityError

from catalog import app, db
from catalog.models import Item, Category
from catalog.auth import oauth, providers


def protected_resource(fn):
    def inner(*args, **kwargs):
        if not session.get('user'):
            return ('', 401)

        return fn(*args, **kwargs)

    inner.__name__ = fn.__name__
    return inner


def validates_required(data, field, errors):
    if not data.get(field):
        errors[field] = 'This field is required'

    return errors


@app.route('/oauth-connect/<string:provider_name>', methods=['POST'])
def oauth_connect(provider_name):
    # TODO: cross foreign protection
    try:
        provider = getattr(providers, provider_name)
    except AttributeError:
        return make_response(
            json.dumps(dict(message='Provider not supported')), 401)

    data = request.get_json()
    flow = oauth.OauthFlow(provider=provider.__new__(provider))
    user = flow.authenticate(data['token'])
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
@protected_resource
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
                    category=category)
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
@protected_resource
def delete_item(id):
    item = db.session.query(Item).get(id)
    if not item:
        # TODO: return 404 page
        return ('', 404)

    db.session.delete(item)
    db.session.commit()

    return redirect('/')


@app.route('/items/<int:id>/update', methods=['POST'])
@protected_resource
def update_item(id):
    item = db.session.query(Item).get(id)
    if not item:
        # TODO: return 404 page
        return ('', 404)

    data = request.form
    errors = {}
    validates_required(data, 'title', errors)
    validates_required(data, 'description', errors)
    validates_required(data, 'category', errors)

    if len(errors.keys()):
        return (render_template('edit.html', errors=errors), 400)

    item.title = data['title']
    item.description = data['description']
    item.category = data['category']

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
def create_item_page():
    return render_template('new-item.html')


@app.route('/items/<int:item_id>/show')
def show_item_page(item_id):
    item = db.session.query(Item).get(item_id)
    if not item:
        #TODO: 404 page
        return ('', 404)

    return render_template('show-item.html', item=item)


@app.route('/items/<int:item_id>/edit')
def edit_item_page(item_id):
    item = db.session.query(Item).get(item_id)
    if not item:
        #TODO: 404 page
        return ('', 404)

    return render_template('new-item.html', item=item)


# JSON endpoints
@app.route('/<string:category>/items')
def list_items_for_category(category):
    items = Item.list_by_category(category)
    return json.dumps(items, default=lambda o: o.serialize)

