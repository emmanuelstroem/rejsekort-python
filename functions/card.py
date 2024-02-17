import logging
from socket import timeout
from typing import Dict, List
from functions import shared
from bs4 import BeautifulSoup
import re, json, cProfile, requests
import concurrent.futures


def get_expiry(prefix, cookies):
    shared.session.cookies.update(cookies)
    try:
        details = shared.session.get(f"{shared.base_url}/CWS/CardServices/Overview/{prefix}", timeout=shared.requests_timeout)

        expiry_date = re.search(r'\d{2}/\d{2}/\d{4}', details.text)
        if expiry_date is None:
            raise ValueError("Expiry date not found")
        return expiry_date.group(0)
    except Exception as e:
        print(f"An error occurred: {e}")


def get_details(cards, cookies):
    cards_list = []
    for card in cards:
        card_elements = card.find_all('div', class_='my_rejsekort_card_element')
        for card_element in card_elements:
            if card_element.find("div", class_="customer_name") and card_element.find('span', class_='bold right'):
                try:
                    customer_name = card_element.find("div", class_="customer_name").string.strip()
                    balance = card_element.find('span', class_='bold right').string + ' kr'
                    link = None
                    prefix = None
                    if card_element.find('a'):
                        link = card_element.find('a')
                        prefix = link['href'].split('/')[-1]
                    # card_expiry_date = get_expiry(prefix, cookies)

                    data = {
                        'name': customer_name,
                        'number': link.text,
                        'balance': balance,
                        'electric_number': prefix.split("cardElectronicNumber=")[1],
                        'prefix': prefix,
                        # 'expiry_date': card_expiry_date,
                        'status': 'active',
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
