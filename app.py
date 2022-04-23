from flask import Flask, request
from functions import shared
from functions.user import fetch_user_details
from functions.card import extract_card_details
from bs4 import BeautifulSoup
import os, re, json, requests

port = os.getenv('PORT', 3000)
env = os.getenv('ENV', "development")

app = Flask(__name__)

session = requests.Session()

@app.route('/')
def health_check():
  """Return health check JSON response
  """
  return {"status": "Healthy"}, 200, {"Content-Type": "application/json"}


@app.route('/login', methods=['POST'])
def login():
  """Login user and fetch details, cards and journeys

  Parameters
  ----------
  username: str
    username created from selfservice portal: https://selvbetjening.rejsekort.dk/
  password: str
    password associated with the user account above
  """    
  request_data = request.get_json()

  # Get Login Page HTML
  # Timeout after 10seconds 
  login_page_html = session.get(shared.base_url + '/CWS/Home/UserNameLogin', timeout=shared.requests_timeout)
  login_request_verification_token = shared.get_verification_token(login_page_html)

  # Build post data for login
  login_credentials = {
    'Username': request_data['username'],
    'Password': request_data['password'],
    '__RequestVerificationToken': login_request_verification_token
  }

  login_page = session.post(shared.base_url + '/CWS/Home/Index', login_credentials)
  soup = BeautifulSoup(login_page.text, "html.parser")
  token = shared.get_verification_token(login_page)

  # Check if login_page contains error in response and return message to user.
  # Otherwise, continue to get user details and travel history

  # TODO: fix error string/message to search for in place of YaNeverKNOW
  error_on_login_page = re.search(r'Sorry. A technical error has occurred', login_page.text)
  if error_on_login_page:
    # Error Loggin In. Clear Session Cookies for next request
    # StatusCode 401 is unauthorized/unauthenticated
    session.cookies.clear()
    session.close()
    login_error = {"error": "unsuccessful login"}
    return json.dumps(login_error, indent=2, ensure_ascii=False), 401
  elif login_page_html.status_code == 500:
    # Close and Clear Session Cookies for next request
    session.cookies.clear()
    session.close()
    timeout_error = {"error": "request timed out"}
    return json.dumps(timeout_error, indent=2, ensure_ascii=False), 500
  else: 
    # Login was successful
    user_details = fetch_user_details(session, token)
    active_cards = soup.find_all('div', class_='ActiveCard')
    cards = extract_card_details(active_cards, session, token)

    user_data = {
      "cards": cards,
      "user": user_details
    }

    # Clear Session Cookies for next request
    session.cookies.clear()
    session.close()

    return json.dumps(user_data)
    # end successful login


# run app in debug mode if env is development 
# use waitress for production
if __name__ == '__main__':
  if env == "development":
    app.run(host="0.0.0.0", debug=True, port=port)
  else:
    from waitress import serve
    serve(app, port=port)
