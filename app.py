import json
import requests
import smtplib
import textwrap
from bs4 import BeautifulSoup
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText


def get_dividend(url):
    global config
    html_doc = requests.get(url)
    soup = BeautifulSoup(html_doc.text, 'html.parser')

    ex_dividend_table = soup.find('table', {'id': 'divCapGainsTable'})

    table_field_list = [
        'distribution-type',
        'distribution',
        'record-date',
        'ex-dividend-date',
        'payable-date',
        'distribution-yield',
        'sec-yield'
    ]

    ex_dividend_list = []

    for tr in ex_dividend_table.find_all('tr')[1:]:
        ex_dividend_dict = {}
        for index, td in enumerate(tr.find_all('td')):
            ex_dividend_dict[table_field_list[index]] = td.text
        ex_dividend_list.append(ex_dividend_dict)

    for record in ex_dividend_list:
        if record['ex-dividend-date'] == today:
            message = textwrap.dedent("""\
            Distribution: {}
            Payable Date: {}
            """.format(record['distribution'], record['payable-date']))
            send_email(message)


def send_email(message):
    global symbol, config
    # connect to SMTP server
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(config['email'], config['password'])
    except smtplib.SMTPAuthenticationError as e:
        exit(e)
    except smtplib.SMTPServerDisconnected as e:
        exit(e)

    # create email content
    email_text = MIMEText(message, 'plain', 'utf-8')
    email_text['From'] = Header(config['email'], 'utf-8')
    email_text['To'] = Header(', '.join(config['recipients']), 'utf-8')
    subject = 'Today is {} Ex-Dividend Date'.format(symbol)
    email_text['Subject'] = Header(subject, 'utf-8')

    try:
        server.sendmail(config['email'], config['recipients'], email_text.as_string())
        server.quit()
    except smtplib.SMTPException as e:
        exit(e)


if __name__ == '__main__':
    global symbol, config
    config = json.load(open('config.json'))
    today = datetime.now().strftime('%m/%d/%Y')

    for target in config['target_list']:
        symbol = target['symbol']
        get_dividend(config['base_url'] + target['fund_id'])
