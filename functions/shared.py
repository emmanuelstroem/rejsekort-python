import re
from bs4 import BeautifulSoup

base_url = "https://selvbetjening.rejsekort.dk"
login_url = base_url + '/CWS/Home/UserNameLogin'
index_url = base_url + '/CWS/Home/Index'
travel_history_url = base_url + "/CWS/TransactionServices/TravelCardHistory"
requests_timeout = 10

pattern = re.compile(r'<input[^>]*name="__RequestVerificationToken"[^>]*>')


def get_verification_token(html_page):
    """
    Extract the __RequestVerificationToken from the HTML page.

    Args:
    html_page (str): The HTML page to extract the token from.

    Returns:
    str: The __RequestVerificationToken value.

    Raises:
    ValueError: If the __RequestVerificationToken input tag is not found in the HTML page.
    TypeError: If the html_page is not a string
    ValueError: If the html_page is empty
    """

    if not isinstance(html_page, str):
        raise TypeError("html_page must be a string.")
    if not html_page:
        raise ValueError("html_page cannot be empty.")

    # Search for the __RequestVerificationToken input tag
    token_input_tag = pattern.search(html_page)

    # Check if the input tag is found
    if not token_input_tag:
        raise ValueError("__RequestVerificationToken input tag not found in the HTML page.")

    # Parse the input tag using BeautifulSoup
    soup = BeautifulSoup(token_input_tag.group(0), "lxml")
    try:
        token = soup.find('input')['value']
    except KeyError:
        raise ValueError("__RequestVerificationToken input tag not contain value attribute.")
    return token
