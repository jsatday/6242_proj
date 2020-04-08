import wget
import os

#os.mkdir("Stocks2")

url = "https://6242stockmarket.blob.core.windows.net/stocks/aapl.us.txt"

wget.download(url, "Stocks2/")


#import requests

#url = 'https://6242stockmarket.blob.core.windows.net/stocks/a.us.txt'

#myfile = requests.get(url)

#open('~/Downloads/', 'wb').write(myfile.content)