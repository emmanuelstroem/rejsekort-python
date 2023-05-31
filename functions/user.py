from functions import shared
from bs4 import BeautifulSoup


def fetch_user_details(session, token):
    """
    Fetch the user details from the website.

    Args:
    session (requests.Session): The session object with the user's cookies.
    token (str): The __RequestVerificationToken value.

    Returns:
    dict: A dictionary containing the user's details.

    Raises:
    ValueError: If the __RequestVerificationToken input tag is not found in the HTML page.
    ValueError: If the myInformationReadOnlyTable is not found in the HTML page.
    """

    # Fetch the user details from the website
    details = session.get(shared.base_url + '/CWS/CustomerManagement/MyInformation',
                          data={'__RequestVerificationToken': token}, timeout=shared.requests_timeout)

    soup = BeautifulSoup(details.text, "html.parser")
    my_info_container = soup.find('div', {"id": "readonlyDisplay"})

    if not my_info_container:
        raise ValueError("readonlyDisplay not found in the HTML page.")

    info_tables = my_info_container.find_all('table', class_='myInformationReadOnlyTable')

    if not info_tables:
        raise ValueError("myInformationReadOnlyTable not found in the HTML page.")

    info_details = {}

    # get th as Keys
    for table in info_tables:
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if tds:
                key = tds[0].text.strip()
                value = tds[1].text.strip()
                info_details[key] = value

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
