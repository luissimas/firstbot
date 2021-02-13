from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import sys
import json
import time
import nltk

import cryptoquery
import scraper
import config

from requests.sessions import session

botToken = config.botToken

def testBot():
    url = 'https://api.telegram.org/bot' + botToken + '/getMe'

    session = Session()

    try:
        response = session.get(url)
        data = json.loads(response.text)

        print(json.dumps(data, indent=4, sort_keys=True))

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)

def sendMessage(chatId, message):
    if (chatId == -1) and  (message == -1):
        chatId = input('Id: ')
        message = input('Mensagem: ')

    url = 'https://api.telegram.org/bot' + botToken + '/sendMessage'

    parameters = {
        'chat_id': chatId,
        'text': message
    }

    session = Session()

    try:
        response = session.get(url,params=parameters)
        data = json.loads(response.text)

        #print(json.dumps(data, indent=4, sort_keys=True))

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)

def getUpdates():
    url = 'https://api.telegram.org/bot' + botToken + '/getUpdates'

    parameters={
        'limit': '1',
        'offset': '-1'
    }

    session = Session()

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)['result']

        print(json.dumps(data, indent=4, sort_keys=True))

        return data

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)

def getChat():
    url = 'https://api.telegram.org/bot' + botToken + '/getChat'

    chatId = input('Id: ')

    parameters = {
        'chat_id': chatId
    }

    session = Session()

    try:
        response = session.get(url,params=parameters)
        data = json.loads(response.text)

        print(json.dumps(data, indent=4, sort_keys=True))

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)

def listen():

    sendMessage('-563780415', 'Comecei a ouvir as mensagens do grupo...\nPara interagir comigo digite um comando seguido do texto desejado\nCommandos possíveis: !repete, !bitcoin, !fazoq, !wiki\nConsigo perceber updates de 5 em 5 segundos porque meu dev é preguiçoso e burro por enquanto...')

    file = open('lastmessage.txt', 'rt')
    prevMsg = json.loads(file.read())
    file.close()

    while True:
        data = getUpdates()

        lastMsg = data.pop()

        #print(json.dumps(lastMsg, indent=4, sort_keys=True))


        if  (lastMsg != prevMsg):
            answerID = lastMsg['message']['chat']['id']
            text = nltk.word_tokenize(lastMsg['message']['text'])

            if (len(text) >= 2) and str(text[0]) == '!':
                command = text.pop(0)
                command += text.pop(0)

                print(command)

                message = ''

                for word in text:
                    message += str(word) + ' '

                if command == '!repete':
                    sendMessage(answerID, message)

                elif command == '!bitcoin':
                    coins = cryptoquery.getCryptoInfo()

                    messageText = 'Consegui as seguintes informações: \n'

                    for coin in coins:
                        messageText += coin.name + '(' + coin.symbol + '): R${0:.2f}'.format(coin.price) + '\n'

                    sendMessage(answerID, messageText)

                elif command == '!wiki':
                    wikiInfo = scraper.scrapePage(message)
                    sendMessage(answerID, wikiInfo.content)

                elif command == '!fazoq':
                    sendMessage(answerID, 'Como cu de curioso :)')

                elif command == '!quit':
                    sendMessage(answerID, 'Ok, até a próxima!')
                    file = open('lastmessage.txt', 'wt')
                    file.write(json.dumps(lastMsg))
                    file.close()
                    return

                elif prevMsg != '':
                    sendMessage(answerID, 'Foi mal, não consegui entender o commando que você digitou :/')

                prevMsg = lastMsg

        time.sleep(5)


option = sys.argv[1]

if option == 'test':
    testBot()
elif option == 'msg':
    sendMessage(-1, -1)
elif option == 'update':
    getUpdates()
elif option == 'getchat':
    getChat()
elif option == 'listen':
    listen()


