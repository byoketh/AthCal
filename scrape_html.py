import requests
from bs4 import BeautifulSoup
import csv

URL = "https://www.chlathletics.org/g5-bin/client.cgi?cwellOnly=1&G5MID=052119071109056048054057085057079121108097120099075117068089100068089084043048101043098053076105052097056050047110098085078120075090073066076116116112089043067103066054066121048&G5statusflag=view&G5genie=661&G5button=12&vw_worksheet=4087&vw_type=mySchoolOnly&school_id=7"
r = requests.get(URL)
rawhtml = BeautifulSoup(r.content, 'html5lib')
quotes=[]

table = soup.find('div', attrs = {'id':'container'})
for row in table.findAll('div', attrs = {'class':'quote'}):
    quote = {}
    quote['theme'] = row.h5.text
    quote['url'] = row.a['href']
    quote['img'] = row.img['src']
    quote['lines'] = row.h6.text
    quote['author'] = row.p.text
    quotes.append(quote)

filename = 'inspirational_quotes.csv'
with open(filename, 'wb') as f:
    w = csv.DictWriter(f,['theme','url','img','lines','author'])
    w.writeheader()
    for quote in quotes:
        w.writerow(quote)
