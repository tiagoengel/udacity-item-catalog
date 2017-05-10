import json

from flask import make_response, session, request, redirect
from catalog import app
from catalog.auth import oauth, providers


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
