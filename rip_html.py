#Installation
#pip install requests
#pip install html5lib
#pip install bs4

import requests
URL = "https://www.geeksforgeeks.org/data-structures/"
r = requests.get(URL)

from bs4 import BeautifulSoup
soup = BeautifulSoup(r.content, 'html5lib')
print(soup.prettify())
