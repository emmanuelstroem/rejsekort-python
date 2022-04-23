import requests, re
from bs4 import BeautifulSoup

base_url = "https://selvbetjening.rejsekort.dk"
login_url = base_url + '/CWS/Home/UserNameLogin'
index_url = base_url + '/CWS/Home/Index'
travel_history_url = base_url + "/CWS/TransactionServices/TravelCardHistory"
requests_timeout = 10


def get_verification_token(html_page):
  """Extract request verification token from a given html response text
  This token is available on all selvbetjening.rejsekort.dk pages.
  And is required when making every subsequent request.
  """
  # extract token input tag from script tag
  token_input_tag = re.search(r'<input name="__RequestVerificationToken".*', html_page.text)
  # parse the token input tag and get the value field
  soup = BeautifulSoup(token_input_tag.group(0), "html.parser")
  token = soup.findAll('input')[0]['value']

  return token
