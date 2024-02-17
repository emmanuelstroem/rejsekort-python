import json
import logging as log
from bs4 import BeautifulSoup
from functions import shared, authenticate

def get_paginated_history(cookies, prefix, periodSelected='ThreeMonths'):
    page = 1
    has_next = True
    rows = []
    
    shared.session.cookies.update(cookies)

    while has_next:
        url = shared.base_url + '/CWS/TransactionServices/TravelCardHistory/' + prefix
        params = {'periodSelected': periodSelected, 'page': page}
        
        try:
            history = shared.session.get(url, params=params, timeout=shared.requests_timeout)
            soup = BeautifulSoup(history.text, "lxml")

            pages = len(soup.find_all('div', {"class": "historyPage"}))

            # find all rows in the table
            data = soup.find_all('tr')

            rows.extend(data)

            # check if there is a 'Next' button in the pagination
            pagination = soup.find_all('span', {"class": "paginationButton"}, {"name": "goToPage"})
            has_next = any('Next' in result.text for result in pagination)

            if has_next:
                page += pages
        except Exception as e:
            log.error(f"Error fetching travel history: {e}")
            return []

    # get the headers from the first row
    if not rows:
        return []
    else:
        headers = [th.text for th in rows[0].find_all('th')]
        dataset = [{headers[i]: cell.text.strip() for i, cell in enumerate(row.find_all('td'))} for row in rows[1:]]
        return dataset


def get_history(cookies, prefix, periodSelected='OneWeek'):
    # cProfile.run(get_paginated_travel_history(session, prefix, token))
    dataset = get_paginated_history(cookies, prefix, periodSelected)
    data = {}

    # print(credentials["cookies"])

    if not dataset:
        return json.dumps({"Fetch": "No Travel History"})
    else:
        orders = list(filter(
            lambda x: "Reload agreement" in x.values() or "Reload" in x.values() or "Rejsekort ordered" in x.values() or "Top-up" in x.values(),
            dataset))
        # Remove empty key-values and empty objects from orders
        orders = [{k: v for k, v in d.items() if v} for d in orders]

        journeys = list(filter(lambda x: x not in orders, dataset))
        # Remove empty key-values and empty objects from journeys
        journeys = [{k: v for k, v in d.items() if v} for d in journeys]

        data: dict[str, list[dict]] = {
            "journeys": list(filter(bool, journeys)),
            "orders": list(filter(bool, orders))
        }

    return json.dumps(data, indent=2, ensure_ascii=False)
