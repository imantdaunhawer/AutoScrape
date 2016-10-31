import time
import smtplib
# import html2text
import os
import mechanize
import cookielib

from bs4 import BeautifulSoup
from getpass import getpass
from datetime import datetime


def auth(url, user, password):
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=5)

    br.addheaders = [('User-agent', 'Chrome')]

    # The site we will navigate into, handling it's session
    br.open(url)

    # Select the second (index one) form (the first form is a search query box)

    br.select_form(nr=0)

    # User credentials
    br.form['username'] = user
    br.form['password'] = password

    # Login
    br.submit()
    return br


def get_content_by_id(browser, url, element_id):
    bs = BeautifulSoup(browser.open(url).read(), 'html.parser')
    return bs.find(id=element_id)


def connect_mail_server(user, password, host='smtp.gmail.com', port=587):
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(user, password)
    return server


def send_mail(server, from_addr, to_addr, *args):
    msg = "".join(args)
    server.sendmail(from_addr, to_addr, msg)


if __name__ == "__main__":
    # Account credentials
    TARGET_USER = os.getenv("TARGET_USER") or raw_input("site username: ")
    TARGET_PW = os.getenv("TARGET_PW") or getpass("site password: ")
    SMTP_USER = os.getenv("SMTP_USER") or raw_input("mail address: ")
    SMTP_PW = os.getenv("SMTP_PW") or getpass("mail password: ")
    mail_list = ["max.mustermann@host.com",
                 "maximilia.mustermann@host.com"]

    # Connect to mail server to test the connection
    server = connect_mail_server(SMTP_USER, SMTP_PW)

    # Authentification
    login_url = ('https://target.website.loginpage')
    browser = auth(login_url, TARGET_USER, TARGET_PW)

    # Get initial data
    data_url = "https://target.website.contentpage"
    element_id = "il_center_col"
    old_content = get_content_by_id(browser, data_url, element_id)
    counter = 0

    # Check for new content every now and then
    while True:
        if counter > 2:
            # do not send more than 3 mails
            server.quit()
            break
        new_content = get_content_by_id(browser, data_url, element_id)
        if (old_content.text != new_content.text):
            # re-connect mail server
            server = connect_mail_server(SMTP_USER, SMTP_PW)
            # send mail and update content
            send_mail(server, SMTP_USER, mail_list, "CONTENT CHANGED")
            old_content = new_content
            counter += 1

        print(datetime.now().isoformat())
        time.sleep(60)
