from socket import timeout
from functions import shared
from bs4 import BeautifulSoup
import re, json

def fetch_card_expiry_date(prefix, session, token):
  """Fetch Card Expiry date using shared session, prefix and token
  
  Parameters
  ----------
  prefix: str
    contains dynamic url with card number
  session: requests.session
    same session as the one that logged in. 
    this has to be passed down to all the subsequent requests
  token: 
    request verification token extracted from rejsekort html page. 
    this is different with every response.
  """
  details = session.get(shared.base_url + '/CWS/CardServices/Overview/' + prefix,  data = {'__RequestVerificationToken': token }, timeout=shared.requests_timeout)

  soup = BeautifulSoup(details.text, "html.parser")
  card_detail_elements = soup.find_all('div', class_='my_reload_agreement_left')

  expiry = ""

  for detail in card_detail_elements:
    expiry_date = re.search(r'\d{2}/\d{2}/\d{4}', detail.text, re.IGNORECASE)
    if expiry_date is None:
      pass
    else:
      expiry = expiry_date.group()
  
  return expiry


def fetch_travel_history(prefix, session, token):
  """Fetch Travel History from Card
  This uses the card prefix to fetch all travel history (13 months).

  It also separates _journeys_ and _orders_ into different JSON objects.

  Parameters
  ----------
  periodSelected: str 
    duration for which to fetch history.
    value is one of: OneWeek, TwoWeeks, OneMonth, ThreeMonths, All
  prefix: str
    contains dynamic url with card number
  token: 
    request verification token extracted from rejsekort html page. 
    this is different with every response.
  """
  history = session.get(shared.base_url + '/CWS/TransactionServices/TravelCardHistory/' + prefix,  data = {'periodSelected': 'All', '__RequestVerificationToken': token }, timeout=shared.requests_timeout)
  soup = BeautifulSoup(history.text, "html.parser")

  history_table = soup.find('div', class_='historyPage')

  journeys = []
  orders = []
  fields = []
  
  # get th as Keys
  for row in history_table.table.find_all('tr', recursive=False):
    table_headers = row.find_all('th', recursive=False)
    for th in table_headers:
      if len(th.text.strip()) == 0 and "Journey no." not in table_headers:
        fields.append("Transaction Type")
      else:
        fields.append(th.text.strip())
  # get td as Values
  for row in history_table.table.find_all('tr', recursive=False):
    travel_records = {}
    for index, td in enumerate(row.find_all('td', recursive=False)):
      if td.img:
        travel_records[fields[index]] = re.sub(" +", " ",td.img['transactionscreentype'].strip())   
      else:
          if len(td.text.replace('\r\n', '').strip()) == 0:
            pass
          else:
            travel_records[fields[index]] = re.sub(" +", " ",td.text.replace('\r\n', '').strip())   
    if travel_records:
      journeys.append(travel_records)

  for index, travel in enumerate(journeys):
    # check if Transaction Type is empty and remove the key with its value
    # otherwise, its an "order" or "topup" - add it to orders
    if "Transaction Type" in travel and travel["Transaction Type"] == '':
      travel.pop("Transaction Type")
    else:
      orders.append(travel)
      journeys.pop(index)

  data = {
    "journeys": journeys,
    "orders": orders
  }

  return json.dumps(data, indent=2, ensure_ascii=False)


def extract_card_details(cards, session, token):
  """Retrives details of cards and returns them in a JSON array

  Parameters
  ----------
  cards: [cards] 
    list of cards to fetch details of
  session: requests.session
    same session as the one that logged in. 
    this has to be passed down to all the subsequent requests
  token: 
    request verification token extracted from rejsekort html page. 
    this is different with every response.
  """

  cards_list = []
  
  for card in cards:
    card_elements = card.find_all('div', class_='my_rejsekort_card_element')
    for card_element in card_elements:
      if card_element.find("div", class_="customer_name") and card_element.find('a') and card_element.find('span', attrs={'class': 'bold right'}):
        card_prefix = card_element.find('a')['href'].split('/')[-1]
        card_expiry_date = fetch_card_expiry_date(card_prefix, session, token)
        journeys_and_orders = fetch_travel_history(card_prefix, session, token)

        data = {
          'name': card_element.find("div", class_="customer_name").string.strip(),
          'number': card_element.find('a').text,
          'balance': card_element.find('span', class_='bold right').string + ' kr',
          'electric_number': card_prefix.split("cardElectronicNumber=")[1],
          'prefix': card_prefix,
          'expiry_date': card_expiry_date,
          'history': journeys_and_orders,
          'status': 'active'
        }

        cards_list.append(data)
      else:
        pass
  
  return cards_list

# MyDiscount
# ChangeCad: /CWS/CardServices/MyDiscount
  # cardSelected: #Number
  # controller: CardServices
  # action: MyDiscount

# CreateReloadAgreement
# Parameters: CardNumber, Reload agreement amount (DKK), Reload at balance (DKK), Max. number of daily reloads (1-6)

# Block Card: /CWS/BlockCard/Index

# ReplaceCard: /CWS/ReplaceCard/Index
