import logging
from socket import timeout
from typing import Dict, List

from functions import shared
from bs4 import BeautifulSoup
import re
import concurrent.futures


def fetch_card_expiry(prefix, session, token):
    """
    Fetch the card expiry date from the website using the provided session and token.

    Args:
    - prefix (str): The prefix used to construct the URL for fetching card details.
    - session: An instance of the session used for making the request.
    - token (str): The token used for fetching card details.
    - timeout (int): The number of seconds to wait for a response from the server.

    Returns:
    - str: The card expiry date in the format 'MM/DD/YYYY'

    Raises:
    - ValueError: If the div class 'my_reload_agreement_left' is not found in the HTML page.
    - ValueError: If the expiry date is not found in the HTML page.
    - Exception: If any other error occurs during the request.
    """
    try:
        details = session.get(f"{shared.base_url}/CWS/CardServices/Overview/{prefix}",
                              data={'__RequestVerificationToken': token}, timeout=shared.requests_timeout)

        expiry_date = re.search(r'\d{2}/\d{2}/\d{4}', details.text)
        if expiry_date is None:
            raise ValueError("Expiry date not found")
        return expiry_date.group(0)
    except Exception as e:
        print(f"An error occurred: {e}")


def get_paginated_travel_history(session, prefix, token):
    """
    Retrieves all paginated data from a table and return it in the form of a list of dictionaries

    Parameters:
    session (Session) : session object to handle the connection with the server
    prefix (str) : prefix for the url
    token (str) : token for the request

    Returns:
    List[Dict[str,str]] : list of dictionaries containing the data
    """

    page = 1
    has_next = True
    rows = []

    while has_next:
        url = shared.base_url + '/CWS/TransactionServices/TravelCardHistory/' + prefix
        params = {'periodSelected': 'All', '__RequestVerificationToken': token, 'page': page}
        history = session.get(url, params=params, timeout=shared.requests_timeout)
        soup = BeautifulSoup(history.text, "html.parser")

        pages = len(soup.find_all('div', {"class": "historyPage"}))

        # find all rows in the table
        data = soup.find_all('tr')
        rows.extend(data)

        # check if there is a 'Next' button in the pagination
        pagination = soup.find_all('span', {"class": "paginationButton"}, {"name": "goToPage"})
        has_next = any('Next' in result.text for result in pagination)

        if has_next:
            page += pages

    # get the headers from the first row
    headers = [th.text for th in rows[0].find_all('th')]

    dataset = [{headers[i]: cell.text.strip() for i, cell in enumerate(row.find_all('td'))} for row in rows[1:]]

    return dataset


def fetch_travel_history(prefix, session, token):
    """
    Retrieves the travel history data, separates it into orders and journeys, and returns it as a dictionary

    Parameters:
    prefix (str) : prefix for the url
    session (Session) : session object to handle the connection with the server
    token (str) : token for the request

    Returns:
    Dict[str, List[Dict[str,str]]] : dictionary containing the data for orders and journeys
    """
    # cProfile.run(get_paginated_travel_history(session, prefix, token))
    dataset = get_paginated_travel_history(session, prefix, token)

    orders = list(filter(
        lambda x: "Reload agreement" in x.values() or "Reload" in x.values() or "Rejsekort ordered" in x.values(),
        dataset))
    # Remove empty key-values and empty objects from orders
    orders = [{k: v for k, v in d.items() if v} for d in orders]

    journeys = list(filter(lambda x: x not in orders, dataset))
    # Remove empty key-values and empty objects from journeys
    journeys = [{k: v for k, v in d.items() if v} for d in journeys]

    travel_data: dict[str, list[dict]] = {
        "journeys": list(filter(bool, journeys)),
        "orders": list(filter(bool, orders))
    }

    return travel_data


def extract_card_details(cards, session, token):
    """
    Extract card details from the provided cards using the provided session and token.

    Args:
    - cards (bs4.element.ResultSet): A result set of card elements.
    - session: An instance of the session used for making the request.
    - token (str): The token used for fetching card details.

    Returns:
    - list: A list of dictionaries containing card details.

    Raises:
    - ValueError: If any required card details are missing.
    """

    cards_list = []
    for card in cards:
        card_elements = card.find_all('div', class_='my_rejsekort_card_element')
        for card_element in card_elements:
            if card_element.find("div", class_="customer_name") and card_element.find('span', class_='bold right'):
                try:
                    customer_name = card_element.find("div", class_="customer_name").string.strip()
                    card_balance = card_element.find('span', class_='bold right').string + ' kr'
                    card_link = None
                    card_prefix = None
                    if card_element.find('a'):
                        card_link = card_element.find('a')
                        card_prefix = card_link['href'].split('/')[-1]
                    card_expiry_date = fetch_card_expiry(card_prefix, session, token)
                    history = fetch_travel_history(card_prefix, session, token)

                    data = {
                        'name': customer_name,
                        'number': card_link.text,
                        'balance': card_balance,
                        'electric_number': card_prefix.split("cardElectronicNumber=")[1],
                        'prefix': card_prefix,
                        'expiry_date': card_expiry_date,
                        'status': 'active',
                        'journeys': history["journeys"],
                        'orders': history["orders"]
                    }

                    cards_list.append(data)
                except Exception as e:
                    logging.error('Error extracting card details: %s', e)
                # else:
                #     logging.error('Could not extract card details. No exceptions caught')
            # else:
            #     # logging.error('===> Invalid Card')
            #     pass

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
