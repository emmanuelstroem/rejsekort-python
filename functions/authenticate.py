from functions import shared, user, card
import json, re, logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def login(username, password):

    # Get Login Page HTML
    # Timeout after 10seconds
    login_page_html = shared.session.get(shared.base_url + '/CWS/Home/UserNameLogin', timeout=shared.requests_timeout)
    request_verification_token = shared.get_verification_token(login_page_html.text)

    # Build post data for login
    credentials = {
        'Username': username,
        'Password': password,
        '__RequestVerificationToken': request_verification_token
    }

    # ⬇ NOTE: Rejsekort changed the Username login URL from Index to UserNameLogin
    response = shared.session.post(shared.base_url + '/CWS/Home/UserNameLogin', credentials)
    soup = BeautifulSoup(response.text, "html.parser")    

    print(f"Login Status: {is_login_successful(soup)}")

    # Check if login_page contains error in response and return message to user.
    # Otherwise, continue to get user details and travel history

    # TODO: fix error string/message to search for in place of YaNeverKNOW
    if is_login_successful(soup):
        # Login was successful
        details = user.get_details()
        active_cards = soup.find_all('div', class_='ActiveCard')
        cards = card.get_details(active_cards, shared.session.cookies.get_dict())

        login_time = ""
        login_expiry = ""
        
        try:
            login_time = datetime.strptime(response.headers['Date'], '%a, %d %b %Y %H:%M:%S GMT')
            login_expiry = login_time + timedelta(hours=3) # 3 hours
        except Exception as e:
            logging.error(f"Error parsing cookie datetime from header: {e}")

        user_details = {
            "user": details,
            "cards": cards,
            "credentials": {    
                "username": username,
                "password": password,
                "cookies": {
                    "data": shared.session.cookies.get_dict(),
                    "issue": str(login_time),
                    "expiry": str(login_expiry)
                }
            }
        }

        # print(json.dumps(shared.session.cookies.get_dict(), indent=2, ensure_ascii=False))
        
        # Clear Session Cookies for next request
        shared.session.cookies.clear()
        shared.session.close()

        return json.dumps(user_details, indent=2, ensure_ascii=False)
        # end successful login
            
    # error_on_login_page = re.search(r'Sorry. A technical error has occurred', login_page.text)
    elif is_login_failed(soup):
        # Error Loggin In. Clear Session Cookies for next request
        # StatusCode 401 is unauthorized/unauthenticated
        shared.session.cookies.clear()
        shared.session.close()
        login_error = {"Login Failed": "Username or Password is incorrect. Please try again."}
        return json.dumps(login_error, indent=2, ensure_ascii=False)
    elif login_page_html.status_code == 500:
        # Close and Clear Session Cookies for next request
        shared.session.cookies.clear()
        shared.session.close()
        timeout_error = {"Login Failed": "Request timed out. Please try again later."}
        return json.dumps(timeout_error, indent=2, ensure_ascii=False)
    else:
        # Close and Clear Session Cookies for next request
        shared.session.cookies.clear()
        shared.session.close()
        timeout_error = {"Login Failed": "Something else went wrong. Please try again later."}
        return json.dumps(timeout_error, indent=2, ensure_ascii=False)
        

def is_login_required(html_page):
    if html_page.find(string="Sorry. A technical error has occurred.") or html_page.find(string="Go to Log in"):
        return True
    else:
        return False
 

def is_login_failed(page):
    if page.find(string="Sorry. A technical error has occurred.") or page.find(string="Go to Log in") or page.find(string="Dit brugernavn eller din adgangskode er indtastet forkert.") or page.find(string="The username or password is incorrect") or page.find(string="The username or password is incorrect."): 
        return True
    else:
        return False


def is_login_successful(page):
    if page.find_all('div', class_='ActiveCard'):
        return True
    else:
        return False
