# Controllo puntualita' treni
# ViaggiaTreno Trenitalia
# v 1.2
# Autore:flavio.giovannangeli@mail.com

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
# SMS serial port parameters
SMS_SERPORT = '115200'
SMS_SERSPEED = '/dev/ttyUSB0'
SMS_NUMS = '393395882183'


# B E G I N ...

def get_train_timeline(trainId):
    while True:
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
        # Estrapola eventuale ritardo
        diff = d2-d1
        tdelay = diff.seconds/60
        # Gestisci ritardo treno
        if tdelay < 5:
            # Ritardo compreso minore di 5 min., invia messaggio PushOver
            msg = 'REG.' + str(trainId) + ' ' + train_trasc(trainId) + ' in ritardo inferiore a 5 min. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
            pushover_service(msg)
        elif (tdelay >= 5) and (tdelay < 15):
            # Ritardo compreso tra 5 e 14 min., invia messaggio PushOver
            msg = 'REG.' + str(trainId) + ' ' + train_trasc(trainId) + ' in ritardo di ' + str(tdelay) + ' min. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
            pushover_service(msg)
        else:
            # Ritardo uguale o superiore a 15 min, invia SMS
            msg = 'REG.' + str(trainId) + ' ' + train_trasc(trainId) + ' in ritardo di ' + str(tdelay) + ' min. Ultimo ril. a ' + str(stop_name) + ' alle ore ' + str(stop_teffe)
            sms_service(SMS_NUMS,msg)


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


def sms_service(nums,smstext):
    bOK = True
    try:
        serport = SMS_SERPORT
        serspeed = SMS_SERSPEED
        gsmobj = gsmdevice(serport,serspeed)
        numdest = nums.split(';')
        i = 0
        while i < len(numdest):
            if numdest[i]:
                if not gsmobj.send_sms(numdest[i],smstext) == True:
                    bOK = False
                i = i + 1
            else:
                break
    except Exception, err:
        bOK = False
        if DEBUG == 1:
            print sys.stderr.write('ERROR: %s\n' % str(err))
    finally:
        return bOK


def train_trasc(num_treno):
    # Trascodifica tratta.
    if num_treno == '7205':
        tratta = 'RTE-VEL 05:28'
    elif num_treno == '7206':
        tratta = 'VEL-RTE 06:58'
    elif num_treno == '7208':
        tratta = 'VEL-RTE 07:26'
    elif num_treno == '7223':
        tratta = 'RTE-VEL 13:28'
    elif num_treno == '7227':
        tratta = 'RTE-VEL 14:28'
    elif num_treno == '7229':
        tratta = 'RTI-VEL 14:55'
    elif num_treno == '7271':
        tratta = 'RTE-VEL 15:28'
    elif num_treno == '7273':
        tratta = 'RTI-VEL 15:55'
    elif num_treno == '7275':
        tratta = 'RTE-VEL 16:28'
    elif num_treno == '7237':
        tratta = 'RTI-VEL 16:55'
    elif num_treno == '7279':
        tratta = 'RTE-VEL 17:28'
    elif num_treno == '7241':
        tratta = 'RTI-VEL 17:55'
    elif num_treno == '7243':
        tratta = 'RTE-VEL 18:28'
    elif num_treno == '7245':
        tratta = 'RTI-VEL 18:55'
    else:
        tratta = 'TRATTA_ND'
    return tratta


if __name__ == '__main__':
  # Chiamata alla funzione get_train_timeline con num. del treno.
  get_train_timeline(sys.argv[1])