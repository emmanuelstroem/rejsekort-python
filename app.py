from flask import Flask, request
from functions import authenticate, shared
from functions import travel
from bs4 import BeautifulSoup
import os, json, requests

port = os.getenv('PORT', 3000)
env = os.getenv('ENV', "development")

app = Flask(__name__)

session = requests.Session()

@app.route('/')
def health_check():
    """Return health check JSON response
    """
    return {"status": "Healthy"}, 200, {"Content-Type": "application/json"}

@app.route('/fetch', methods=['POST'])
def fetch():
    request_data = request.get_json()
    periodSelected = request_data['periodSelected']
    cookies = request_data['cookies']
    prefix = request_data['prefix']

    shared.session.cookies.update(cookies)
    
    history = travel.get_history(cookies, prefix, periodSelected)

    if "journey" in history or "orders" in history:
        return app.response_class(response=history, status=200, mimetype='application/json')
    else:
        return app.response_class(response=json.dumps({}), status=200, mimetype='application/json')

@app.route('/login', methods=['POST'])
def login():
    
    request_data = request.get_json()
    details = authenticate.login(request_data['username'], request_data['password'])

    if "Login Failed" in details:
        return app.response_class(response=details, status=401, mimetype='application/json')
    else:
        return app.response_class(response=details, status=200, mimetype='application/json')


# for docker run, host is required. app.run(host="0.0.0.0", debug=True) 
# serve production using waitress because it is WSGI
if __name__ == '__main__':
    if env == "development":
        app.run(port=port)
    else:
        from waitress import serve

        serve(app, port=port)
