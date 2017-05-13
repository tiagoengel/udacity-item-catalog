import json

from flask import make_response, session, request, redirect, render_template
from catalog import app, db
from catalog.models import Item
from catalog.auth import oauth, providers


def protected_resource(fn):
    def inner(*args, **kwargs):
        if not session.get('user'):
            return ('', 401)

        return fn(*args, **kwargs)

    inner.__name__ = '%s__protected' % (fn.__name__)
    return inner


def validates_required(data, field, errors):
    if not data.get(field):
        errors[field] = 'This field is required'

    return errors


@app.route('/')
def index():
    return 'hey'


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


@app.route('/logout', methods=['POST'])
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
        return (render_template('edit.html', errors=errors), 400)

    title = data['title']
    category = data['category']
    description = data['description']

    new_item = Item(title=title,
                    description=description,
                    category=category)

    db.session.add(new_item)
    db.session.commit()

    return redirect('/%s/%s' % (category, title))


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
