from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import config

apiKey = config.coinmarketcapKey

class Moeda:
    def __init__(self, name, symbol, price):
        self.name = name
        self.symbol = symbol
        self.price = price

def printCoins(coinsArray):
    for coin in coinsArray:
        print("Nome: " + coin.name)
        print("Símbolo: " + coin.symbol)
        print("R$%.2f" % coin.price)
        print(" ")

def getCryptoInfo():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit':'5',
        'sort': 'num_market_pairs',
        'sort_dir': 'desc',
        'cryptocurrency_type': 'coins',
        'convert':'BRL'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': apiKey,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url,params=parameters)
        data = json.loads(response.text)

        coins = []

        for coinData in data['data']:
            name = coinData['name']
            symbol = coinData['symbol']
            price = coinData['quote']['BRL']['price']

            coins.append(Moeda(name, symbol, price))

        return coins
        #printCoins(coins)

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)

getCryptoInfo()
