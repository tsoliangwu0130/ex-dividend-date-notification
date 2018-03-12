import requests
import textwrap
from bs4 import BeautifulSoup
from datetime import datetime

# today = datetime.now().strftime('%m/%d/%Y')
today = '05/01/2017'

def fetch_ex_dividend_data(symbol, url):
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
            message = '''
                -- Today is {} Ex-Dividend Date --
                Distribution: {}
                Payable Date: {}
            '''.format(symbol, record['distribution'], record['payable-date'])
            print(textwrap.dedent(message))



if __name__ == '__main__':
    base_url = 'https://personal.vanguard.com/us/JSP/Funds/VGITab/VGIFundDistributionTabContent.jsf?fundsdisableredirect=true&FundIntExt=INT&FundId='
    target_list = [
        {'symbol': 'VT', 'fund_id': '3141'},
        {'symbol': 'BND', 'fund_id': '0928'}
    ]

    for target in target_list:
        fetch_ex_dividend_data(target['symbol'], base_url + target['fund_id'])
