# Controllo puntualita' treni
# ViaggiaTreno Trenitalia
# v 1.3
# Autore:flavio.giovannangeli@gmail.com

import sys
import time
import httplib, urllib, urllib2
import json as simplejson
from datetime import datetime
from bs4 import BeautifulSoup
from cl_gsmat import gsmdevice

# C O N S T A N T S  &  V A R I A B L E S

DEBUG = 1
# PushOver parameters
POV_POAT = 'aduK5mgyT1LXP7xego3b4MCPDVETxz'
POV_POUK = 'uTr1vsTiphNFCH1qvi8q7PPTeCpR1X'
POV_ADDR = 'api.pushover.net:443'


# B E G I N ...

def get_train_timeline(trainId):
    # Effettua chiamata all'URL del servizio ViaggiaTreno con il numero di treno passato.
    url = 'http://mobile.viaggiatreno.it/vt_pax_internet/mobile/scheda?dettaglio=visualizza&numeroTreno=%d&tipoRicerca=numero&lang=IT' %  int(trainId)
    if DEBUG == 1:
        print url
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    # Lettura dati pagina
    page = res.read()
    if DEBUG == 1:
        print page
    soup = BeautifulSoup(page)
    # Estrapola fermate effettuate
    mydivs = soup.findAll("div", { "class" : "giaeffettuate" })
    if DEBUG == 1:
        print mydivs
    # Estrapola orario previsto ed effettivo sull'ultima fermata effettuata
    last_stop = max(mydivs)
    stop_name = td = last_stop.find('h2')
    stop_name = stop_name.contents[0].strip()
    if DEBUG == 1:
        print stop_name
    stop_times= last_stop.find_all('strong')
    if DEBUG == 1:
        print 'Orario previsto:' + stop_times[0].contents[0].strip()
        print 'Orario effettivo:' + stop_times[1].contents[0].strip()
    stop_tprev = stop_times[0].contents[0].strip()
    stop_teffe = stop_times[1].contents[0].strip()
    today = time.localtime(time.time())
    ttoday = time.strftime('%Y-%m-%d', today)
    fmt = '%Y-%m-%d %H:%M'
    d1 = datetime.strptime(ttoday + ' ' + stop_tprev, fmt)
    d2 = datetime.strptime(ttoday + ' ' + stop_teffe, fmt)
    # Controlla ritardo/anticipo
    if d2 > d1:
        # Ritardo
        train_status = 'rit'
        diff = d2-d1
    elif d1 > d2:
        # Anticipo
        train_status = 'ant'
        diff = d1-d2
    else:
        # In orario
        train_status = 'ok'
        diff = d1-d2
    tdelay = diff.seconds/60
    # Gestisci ritardo treno
    if train_status == 'ant':
        msg = 'REG.' + str(trainId) + ' in anticipo di ' + str(tdelay) + ' minuti. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
        if DEBUG == 1:
            print msg
    elif train_status == 'rit':
        msg = 'REG.' + str(trainId) + ' in ritardo di ' + str(tdelay) + ' minuti. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
        if DEBUG == 1:
            print msg
    else:
        msg = 'REG.' + str(trainId) + ' in orario. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
        if DEBUG == 1:
            print msg
    # Invia PushOver
    pushover_service(msg)



def pushover_service(pomsg):
    bOK = True
    try:
        # Lettura parametri Pushover e invio messaggio
        poat = POV_POAT
        pouk = POV_POUK
        poaddr = POV_ADDR
        conn = httplib.HTTPSConnection(poaddr)
        conn.request("POST", "/1/messages.json",
          urllib.urlencode({
            "token": poat,
            "user": pouk,
            "message": pomsg,
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
    except Exception, err:
        bOK = False
        if DEBUG == 1:
            print sys.stderr.write('ERROR: %s\n' % str(err))
    finally:
        return bOK


if __name__ == '__main__':
  # Chiamata alla funzione get_train_timeline con num. del treno.
  get_train_timeline(sys.argv[1])