import requests
import re  # regex module
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class EmailScraper:

    def __init__(self, query):
        self.query = query

    def search(self):
        temp_query = self.query + " email"
        temp_query = "+".join(temp_query.split())

        url = "https://www.google.com/search?q={0}".format(temp_query)

        session = requests_retry_session()

        try:
            # sending an http get request with specific url and get a response
            response = session.get(url)
            if response is None:
                return
        except requests.exceptions.ConnectionError:
            print("Connection Error " + url)
            return "Connection Error"
        except requests.exceptions.Timeout:
            print("Request timed out" + url)
            return "Request timed out"
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects " + url)
            return
        except requests.exceptions.HTTPError:
            print("Bad Request." + url)
            return
        except requests.exceptions.InvalidURL:
            print("Invalid URL. " + url)
            return
        except requests.exceptions.InvalidSchema:
            print("Invalid Schema." + url)
            return
        except requests.exceptions.MissingSchema:
            print("Missing Schema URL. " + url)
            return

        soup = BeautifulSoup(response.text, 'lxml')

        all_email = []
        for tag in soup.find_all('cite'):
            url = tag.get_text()
            emails = self.get_emails(url, session)
            if emails is None:
                continue
            all_email.extend(emails)
        return set(self.strip(all_email))

    def get_emails(self, url, session):

        try:
            # sending an http get request with specific url and get a response
            response = session.get(url)

        except requests.exceptions.ConnectionError:
            print("Connection Error " + url)
            return
        except requests.exceptions.HTTPError:
            print("Bad Request. " + url)
            return
        except requests.exceptions.Timeout:
            print("Request timed out" + url)
            return
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects " + url)
            return
        except requests.exceptions.InvalidURL:
            print("Invalid URL. " + url)
            return
        except requests.exceptions.InvalidSchema:
            print("Invalid Schema." + url)
            response = session.get("http://" + url)
        except requests.exceptions.MissingSchema:
            print("Missing Schema URL. " + url)
            response = session.get("http://" + url)

        if response is None:
            return
        # email pattern to match with - name@domain.com
        email_pattern = "[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 1st pattern
        # making the regex workable - compile it with ignore case
        email_regex = re.compile(email_pattern, re.IGNORECASE)
        # match all the email in html response with regex pattern and get a set of emails
        # response.text returns html as string
        email_list = email_regex.findall(response.text)

        # email pattern to match with - name @ domain.com
        email_pattern = "[a-zA-Z0-9._-]+\s@\s[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 2nd pattern
        # making the regex workable - compile it with ignore case
        email_regex = re.compile(email_pattern, re.IGNORECASE)
        # match all the email in html response with regex pattern and get a set of emails
        # response.text returns html as string
        email_list.extend(email_regex.findall(response.text))

        # email pattern to match with - name at domain.com
        email_pattern = "[a-zA-Z0-9._-]+\sat\s[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 3rd pattern
        # making the regex workable - compile it with ignore case
        email_regex = re.compile(email_pattern, re.IGNORECASE)
        # match all the email in html response with regex pattern and get a set of emails
        # response.text returns html as string
        email_list.extend(email_regex.findall(response.text))

        return email_list

    def strip(self, all_email):
        first = [item.replace(" at ", "@") for item in all_email]
        second = [item.replace(" AT ", "@") for item in first]
        third = [item.replace(" @ ", "@") for item in second]

        return third


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    session.max_redirects = 60
    session.headers['User-Agent'] = 'Googlebot/2.1 (+http://www.google.com/bot.html)'
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


if __name__ == "__main__":

    keywords = input("Search Email: ")
    emailScraper = EmailScraper(keywords)

    email_list = emailScraper.search()

    print(str(len(email_list)) + " emails")

    for email in email_list:
        print(email)
