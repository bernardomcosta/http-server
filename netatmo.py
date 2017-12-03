# This code is heavly based on the sample provided at https://dev.netatmo.com/resources/technical/samplessdks/codesamples#authcode

from flask import Flask, render_template, redirect
from flask import request as r
import requests
import uuid
import sys

CLIENT_ID = None
CLIENT_SECRET = None

app = Flask(__name__)

@app.route('/')
def sign():
    return "<form action='/signin' method='get'><button type='submit'>Sign in</button></form>"

#Authorization Code type authentication flow
@app.route('/signin', methods=['GET'])
def signin():
    # Test if "code" is provided in get parameters (that would mean that user has already accepted the app and has been redirected here)
    if r.args.get('code'):
        code = r.args.get('code')
        payload = {'grant_type': 'authorization_code',
           'client_id': CLIENT_ID,
           'client_secret': CLIENT_SECRET,
           'code': code,
           'redirect_uri': 'http://localhost:5000/signin'}
        try:
            response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
            response.raise_for_status()
            access_token=response.json()["access_token"]
            refresh_token=response.json()["refresh_token"]
            scope=response.json()["scope"]
            return "<p>Your access_token is:" + access_token + "</p>"

        except requests.exceptions.HTTPError as error:
            print(error.response.status_code, error.response.text)
    # Test if "error" is provided in get parameters (that would mean that the user has refused the app)
    elif r.args.get('error') == 'access_denied':
        return "The user refused to give access to his Netatmo data"
    # If "error" and "code" are not provided in get parameters: the user should be prompted to authorize your app
    else:

        payload = {'client_id': CLIENT_ID,
                'redirect_uri': "http://localhost:5000/signin",
                'scope': 'read_station',
                'state': uuid.uuid4().hex}
        try:
            response = requests.post("https://api.netatmo.com/oauth2/authorize", params=payload)
            response.raise_for_status()
            return redirect(response.url, code=302)
        except requests.exceptions.HTTPError as error:
            print(error.response.status_code, error.response.text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please give client id and client secret as arguments. The order matters!")
    else:
        CLIENT_ID = sys.argv[1]
        CLIENT_SECRET = sys.argv[2]

        app.run()
