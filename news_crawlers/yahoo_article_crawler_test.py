## Test parsing code using manual method
from bs4 import BeautifulSoup

class YahooNewsDocumentParser(HTMLParser):
    content = ''
    ignore_texts = [
        'Click here for politics news related to business and money',
        'Read the latest financial and business news from Yahoo Finance',
        'View comments'
    ]
    ignore_tails = [
        'correspondent for Yahoo Finance.'
    ]
    
    def handle_data(self, data):
        if data.strip() in self.ignore_texts:
            return
        if any([str(data).strip().endswith(tail) for tail in self.ignore_tails]):
            return
        self.content = self.content + ' ' + str(data).strip()

with open(".\\test.html") as f:
    soup = BeautifulSoup(f.read(-1))
element = soup.findAll('div', {"class": "caas-body"})

parser = YahooNewsDocumentParser()
parser.feed(str(element[0]))
print(parser.content)