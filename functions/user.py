from functions import shared
from bs4 import BeautifulSoup
import json

def fetch_user_details(session, token):
  """Retrieves User Details

  Parameters
  ----------
  session: requests.session
    same session as the one that logged in. 
    this has to be passed down to all the subsequent requests
  token: 
    request verification token extracted from rejsekort html page. 
    this is different with every response.
  """
  details = session.get(shared.base_url + '/CWS/CustomerManagement/MyInformation',  data = {'__RequestVerificationToken': token }, timeout=shared.requests_timeout)

  soup = BeautifulSoup(details.text, "html.parser")
  my_info_container = soup.find('div', class_='my-information-modifiable-container')

  info_tables = my_info_container.find_all('table', class_='myInformationReadOnlyTable')

  info_details = {}

  # get th as Keys
  for row in info_tables:
    for tr in row.find_all('tr', recursive=False):
      info = {}
      field = []
      for index, td in enumerate(tr.find_all('td', recursive=False)):
        if index == 0:
          field.append(td.text.strip())
        if index == 1:
          info[field[0]] = td.text.strip()
      info_details.update(info)

  return info_details


# ChangeUsername: /CWS/CustomerManagement/ChangeUsername

# ChangePassword: /CWS/CustomerManagement/ChangePassword

# Export Personal Data: /CWS/CustomerManagement/PersonalDataExport
# ConsentMessage: * I acknowledge that after receiving the my personal data export I am solely responsible for securely handling this.
  # Parameters
  # ----------
  # Email: str
    # in the format me@example.com. read from profile
  # PhoneNumber: str
    # +4512345678 - take number and concat country code. prepoluate number from profile
  # StatementOfConsent: bool
    # true or false

# AccountStatement: /CWS/Payment/AccountStatement
