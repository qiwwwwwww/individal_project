from flask import Flask, current_app, session
import json
from oauth2client.contrib.flask_util import UserOAuth2
import httplib2

app = Flask(__name__)
app.config.from_object('config')
oauth2 = UserOAuth2()

def _request_user_info(credentials):
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https://www.googleapis.com/plus/v1/people/me')

    if resp.status != 200:
        current_app.logger.error(
            "Error while obtaining user profile: %s" % resp)
        return None
    session['profile'] = json.loads(content.decode('utf-8'))

oauth2.init_app(
    app,
    scopes=['email', 'profile'],
    authorize_callback=_request_user_info)

from app import views
