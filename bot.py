import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests.sessions import session
import sys
import os
import subprocess
import json
import time
import nltk
import re

import cryptoquery
import scraper
import config


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

        #print(json.dumps(data, indent=4, sort_keys=True))

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

def downloadVideo(url):
    print('Baixando vídeo...')

    os.system('youtube-dl -f "bestvideo[filesize<50M][ext=mp4]+bestaudio[ext=m4a]" -o "./videos/%(title)s.%(ext)s" "' + url + '"')
    filename = subprocess.run(['youtube-dl', '-o', '"./videos/%(title)s.%(ext)s"', '--get-filename',  url], stdout=subprocess.PIPE)

    # Tratando string
    filename = filename.stdout.decode('utf-8')
    filename = re.split(r'\.', filename[3:len(filename) -2])[0] + ".mp4"

    print(filename)

    return filename

def sendVideo(chatId, video):
    url = 'https://api.telegram.org/bot' + botToken + '/sendVideo'

    file = {'video':open(video, 'rb')}

    parameters = {
        'chat_id': chatId
        # The file parameter is passed separately in the request
    }

    print('Enviado para o Telegram...')

    session = Session()

    try:
        response = session.get(url,params=parameters,files=file)
        data = json.loads(response.text)

        print(json.dumps(data, indent=4, sort_keys=True))

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)


def listen():

    #sendMessage('-563780415', 'Comecei a ouvir as mensagens do grupo...\nPara interagir comigo digite um comando seguido do texto desejado\nCommandos possíveis: !repete, !bitcoin, !fazoq, !wiki\nConsigo perceber updates de 5 em 5 segundos porque meu dev é preguiçoso e burro por enquanto...')
    print('Started listening...')

    file = open('lastmessage.txt', 'rt')
    prevMsg = json.loads(file.read())
    file.close()

    while True:
        data = getUpdates()

        lastMsg = data.pop()

        #print(json.dumps(lastMsg, indent=4, sort_keys=True))


        if  (lastMsg != prevMsg) and ('text' in lastMsg['message']):
            print(lastMsg['message']['from']['first_name'] + ' -> ' + lastMsg['message']['text'])

            answerID = lastMsg['message']['chat']['id']
            text = nltk.word_tokenize(lastMsg['message']['text'])

            if (len(text) >= 2) and str(text[0]) == '!':
                command = text.pop(0)
                command += text.pop(0)

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
                    messageText = wikiInfo.content + '\n\nPara saber mais acesse: ' + wikiInfo.url
                    sendMessage(answerID, messageText)

                elif command == '!fazoq':
                    sendMessage(answerID, 'Como cu de curioso :)')

                elif command == '!help':
                    sendMessage(answerID, 'Comandos:\n!repete\n!bitcoin\n!wiki\n!download\n!fazoq')

                elif command == '!download':
                    sendMessage(answerID, 'Beleza, vou baixar o vídeo e já te envio...')
                    downloadUrl = re.sub(r'\s', "", message)
                    sendVideo(answerID, downloadVideo(downloadUrl))
                    print('Vídeo enviado!')

                elif command == '!quit':
                    sendMessage(answerID, 'Ok, até a próxima!')
                    file = open('lastmessage.txt', 'wt')
                    file.write(json.dumps(lastMsg))
                    file.close()
                    return

                elif prevMsg != '':
                    sendMessage(answerID, 'Foi mal, não consegui entender o commando que você digitou :/')

                prevMsg = lastMsg

                # Register command in log file
                file = open('log.txt', 'at')
                file.write(lastMsg['message']['from']['first_name'] + ' -> ' + command + ' ' + message + '\n')
                file.close()

        time.sleep(5)

def changeTitle():
    #chatId = input('Chat ID: ')
    title = input('New title: ')

    url = 'https://api.telegram.org/bot' + botToken + '/setChatTitle'

    parameters = {
        'chat_id': '-563780415',
        'title': title
    }

    session = Session()

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        print(json.dumps(data, indent=4, sort_keys=True))

    except (ConnectionError, Timeout, TooManyRedirects) as error:
        print(error)



option = sys.argv[1]

if option == 'test':
    downloadVideo('https://youtu.be/WVkD4lgXTEU')
    #testBot()
elif option == 'msg':
    sendMessage(-1, -1)
elif option == 'update':
    getUpdates()
elif option == 'getchat':
    getChat()
elif option == 'change-title':
    changeTitle()
elif option == 'send':
    sendVideo('1567935039', 'videos/Bones in the Ocean.mp4')
elif option == 'listen':
    listen()


