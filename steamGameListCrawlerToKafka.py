# API website: https://steamapi.xpaw.me/#
# iterate through game list and store them in json (for now)
import time
import requests
import json
import logging
import sys
import os
import filecmp
log = logging.getLogger('GameListCrawler')
hdlr = logging.FileHandler('logGameListCrawler.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.INFO)

#parameters
autoUpdate = False
loadFromFile = True
#check point
#last_appid = 355100
#last_index = -1

from kafka import KafkaProducer
from kafka.errors import KafkaError

producer = KafkaProducer(bootstrap_servers=['compute-1-1.local:9092'])



def getGameDetails(index, items):

        res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
        #sleep until request rate is low enough
        while res.reason == 'Too Many Requests':
            log.info('rate limit exceeded\n')
            time.sleep(60) #sleep for 60 sec and then request again
            res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
        
        return res

while (True):
    #app list
    # load from file
    if (loadFromFile == True):
        with open ('newapplist.json', 'r+') as fapps:
            applist = json.load(fapps)
    else:
        res = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2')
        applist = res.json()['applist']['apps']
        with open ('newapplist.json', 'w') as fapps:
            json.dump(applist, fapps, indent = 2)
        # #latest app list is still the same as the last one, no need to re-pull game data
        if (autoUpdate == True):
            if (filecmp.cmp('newapplist.json', 'applist.json') == True):
                continue
            with open ('applist.json', 'w') as fapps:
                json.dump(applist, fapps, indent = 2)

    with open ('completeGameData.json', 'w') as f:
    #    for index, items in enumerate(applist):
    #        if items['appid'] == last_appid:
    #            last_index = index
        retries = 0
        for i in range(0, len(applist) - 1):
            while (retries <= 1):
                try:
                    res = getGameDetails(i, applist[i])
                    resj = res.json()
                    appDetails = resj[str(applist[i]['appid'])]
                    if (appDetails['success'] == False):
                        log.info("appdetails[success] equals false, appid:" + str(applist[i]['appid']) + ', retries: ' + str(retries) + '\n')
                        retries = retries + 1
                        #retry
                        continue
                    resstring = json.dumps(appDetails['data'])
                    resstring = resstring.replace('\r', ' ')
                    resstring = resstring.replace('\n', ' ')
                    f.write(resstring)
                    f.write('\n')
                    # Asynchronous by default
                    print("sending to kafka")
                    future = producer.send('my-topic', resstring.encode('utf-8'))

                    # Block for 'synchronous' sends
                    try:
                        record_metadata = future.get(timeout=10)
                    except KafkaError:
                        # Decide what to do if produce request failed...
                        log.error("kafka error when sending appid:" + str(applist[i]['appid']))
                        pass

                    # Successful result returns assigned partition and offset
                    print (record_metadata.topic)
                    print (record_metadata.partition)
                    print (record_metadata.offset)
                    log.info("current appid:" + str(applist[i]['appid']) + ' Progress:' + str(float(i)/float(len(applist))*100) + '  done\n')
                    retries = 0 #sucess, reset retry
                    break
                except:
                    e = sys.exc_info()[0]
                    log.error("exception found at index: " + str(i) + ", appid: " + str(applist[i]['appid']) + ", error: "  + str(e) + "\n")
                    retries = retries + 1
                    #retry 
                    continue
            retries = 0
    #        if index < last_index:
    #            continue
    producer.flush()

    break
    time.sleep(64800) #sleep one day and check applist again
