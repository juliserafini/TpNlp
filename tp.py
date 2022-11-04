import datetime
import math
from pprint import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from requests import Request, Session
import json
import nltk
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import requests
from bs4 import BeautifulSoup


googlePrin = 'news.google.com'
googleFinal = '&hl=en'

bingPrin = 'www.bing.com/news'
bingFinal = '&hl=en&qft=sortbydate%3d"1"&form=YFNR'

import tweepy
TW_API_KEY = 'kvXdTL2YkKj6rAlQQy11gJMUe'
TW_API_SECRET_KEY = '04ry6xwn700PhENHKXdem13dN5bERNH0T1vBIIbMkRpiKyUH4N'
TW_ACCESS_TOKEN = '4872760203-qbVfsijOOnYX2g55q71NbWeULjyIpsQ5y8lmSOY'
TW_ACCESS_TOKEN_SECRET = '2cKaYgh7JBiIL6NNMlywJFbyMGTJDYIQPz9iqBAiXT024'
auth = tweepy.OAuthHandler(TW_API_KEY, TW_API_SECRET_KEY)
auth.set_access_token(TW_ACCESS_TOKEN, TW_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
sia = SIA()
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

stop_words = stopwords.words('spanish')

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
headers = {
    'Accepts':'application/json',
    'X-CMC_PRO_API_KEY':'7fe42f85-db35-4a8d-87f0-5ff02470ba9e'
}
session = Session()
session.headers.update(headers)


def buscarEnTwitter(unaCrypto):
    status = api.rate_limit_status()
    misTweets = set()
    if status['resources']['search']['/search/tweets']['remaining']:
        someTweets = [status._json for status in tweepy.Cursor(api.search_tweets, q=unaCrypto, count=180, tweet_mode='extended', lang='en').items(180)]
        for aTweet in someTweets:
            misTweets.add(aTweet["full_text"])   
    return misTweets
    

def buscarEn(prin, fin, unaCrypto):
    headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }
    url =  'https://' + prin + '/search?q=' + unaCrypto + fin
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')
    unasNoticias = set()
    for resultado in soup.select('.card-with-cluster'):    
        titulo = resultado.select_one('.title').text
        unasNoticias.add(titulo)
    unasNoticias = crearListaSinRepetidos(unasNoticias) 
    return unasNoticias


def buscarUnaCrypto(crypto):
    unasNoticias = set()
    unasNoticias = unasNoticias.union(buscarEnTwitter(crypto))
    unasNoticias = unasNoticias.union(buscarEn(googlePrin, googleFinal, crypto))
    unasNoticias = unasNoticias.union(buscarEn(bingPrin, bingFinal, crypto))
    return unasNoticias

def sentimentToTable(unosSentimientos):
    tabla = pd.DataFrame.from_records(unosSentimientos)
    tabla['positividad'] = 0
    tabla.loc[tabla['compound'] > 0.2, 'positividad'] = 1
    tabla.loc[tabla['compound'] < -0.2, 'positividad'] = -1
    return tabla


def procesarTexto(unasNoticias):
    tokens = []
    for unaNoticia in unasNoticias:
        toks = tokenizer.tokenize(unaNoticia)
        toks = [t.lower() for t in toks if t.lower() not in stop_words]
        tokens.extend(toks)
    return tokens 

def sentimientosDe(crypto):
        noticiasAux = buscarUnaCrypto(crypto)
        cryptoAux = analizarSentimiento(noticiasAux, crypto)
        print('termino')


def analizarSentimiento(unasNoticias, crypto):
    palabrasClave = []
    positivas = 0
    negativas = 0
    neutras = 0
    noticias = 0

    archivo = open("analisis.txt", "a")
    archivo.write(crypto)
    archivo.write(": ")
    archivo.write("\n")
    
    spacy.load('en_core_web_sm')
    for unaNoticia in unasNoticias:
        noticias += 1
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe('spacytextblob')
        doc = nlp(unaNoticia)
        polarity = doc._.blob.polarity
        clave = doc._.blob.sentiment_assessments.assessments
        print(doc._.blob.sentiment_assessments.assessments)
        
        if clave != []:
            palabrasClave.append(clave)
            archivo.write(pasarAString(clave))
            archivo.write("\n")

        if polarity > 0.3:
            positivas += 1
        elif polarity < -0.3:
            negativas += 1
        else:
            neutras += 1

    archivo.write('Cantidad de noticias: '+str(noticias)+'\n')
    archivo.write('Resultados positivos: '+str(positivas)+'\n')
    archivo.write('Resultados positivos: '+str(negativas)+'\n')
    archivo.write('Resultados neutros: '+str(neutras)+'\n\n')
    print('Crypto:', crypto)
    print('Cantidad de noticias:', noticias)
    print('Resultados positivos:', positivas)
    print('Resultados negativos:',negativas)
    print('Resultados neutros:',neutras)
    
    archivo.close()

def crearListaSinRepetidos(lista):
    result = []
    for item in lista:
        if item not in result:
            result.append(item)
    return result

def pasarAString(lista):
    string='['
    
    for tupla in lista:
        string+='('+convertirAStr(tupla[0])
        string+=', '+str(tupla[1])
        string+=', '+str(tupla[2])
        string+=', '+str(tupla[3])+'), '
    string+=']'    
    return string

def convertirAStr(lista):
    string='['
    for item in lista:
        string+=item+', '
    string+=']'
    return string




moneda= 'BTC'
sentimientosDe(moneda)
