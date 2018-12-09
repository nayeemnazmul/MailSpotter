import requests
import re  # regex module
from bs4 import BeautifulSoup


class EmailScraper:

    def __init__(self, query):
        self.query = query

    def search(self):
        temp_query = self.query + " email"
        temp_query = "+".join(temp_query.split())

        url = "https://www.google.com/search?q={0}".format(temp_query)

        response = None
        try:
            # sending an http get request with specific url and get a response
            response = requests.get(url)

        except requests.exceptions.ConnectionError:
            print("Connection Error")
        except requests.exceptions.HTTPError:
            print("Bad Request.")
        except requests.exceptions.InvalidURL:
            print("Invalid URL.")
        except requests.exceptions.InvalidSchema:
            print("Invalid URL.")
        except requests.exceptions.MissingSchema:
            print("Invalid URL.")

        soup = BeautifulSoup(response.text, 'lxml')

        all_email = []
        for tag in soup.find_all('cite'):
            url = tag.get_text()
            emails = self.get_emails(url)

            all_email.extend(emails)
        return set(self.strip(all_email))

    def get_emails(self, url):

        response = None

        try:
            # sending an http get request with specific url and get a response
            response = requests.get(url)

        except requests.exceptions.ConnectionError:
            print("Connection Error " + url)
        except requests.exceptions.HTTPError:
            print("Bad Request. " + url)
        except requests.exceptions.InvalidURL:
            response = requests.get("http://" + url)
        except requests.exceptions.InvalidSchema:
            response = requests.get("http://" + url)
        except requests.exceptions.MissingSchema:
            response = requests.get("http://" + url)

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


if __name__ == "__main__":

    keywords = input("Search Email: ")
    emailScraper = EmailScraper(keywords)

    email_list = emailScraper.search()

    print(str(len(email_list)) + " emails")

    for email in email_list:
        print(email)
