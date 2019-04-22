# API website: https://steamapi.xpaw.me/#
# iterate through game list and store them in json (for now)
import time
import requests
import json
import logging
import sys
import os

log = logging.getLogger('GameListCrawler')
hdlr = logging.FileHandler('logGameListCrawler.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.INFO)

#check point
#last_appid = 355100
#last_index = -1

with open ('tmp.json', 'w') as f:
    #app list
    res = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2')
    applist = res.json()['applist']['apps']
    with open ('applist.json', 'w') as fapps:
        json.dump(applist, fapps, indent = 2)

#    for index, items in enumerate(applist):
#        if items['appid'] == last_appid:
#            last_index = index
    for index, items in enumerate(applist):
#        if index < last_index:
#            continue
        try:
            res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))

            #sleep until request rate is low enough
            while res.reason == 'Too Many Requests':
                log.info('rate limit exceeded\n')
                time.sleep(60) #sleep for 60 sec and then request again
                res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
            
            resj = res.json()
            appDetails = resj[str(items['appid'])]
            log.info("current appid:" + str(items['appid']) + ' Progress:' + str(float(index)/float(len(applist))*100) + '  done\n')
            if (appDetails['success'] == False):
                continue
            json.dump(appDetails['data'], f, indent = 2)
        except:
            e = sys.exc_info()[0]
            log.error("exception found at index: " + str(index) + ", appid: " + str(items['appid']) + ", error: "  + str(e) + "\n")

# add '[' at the start of file 
# add ']' at the end of file 
# add ',' to split each json
with open("tmp.json", 'r+') as f:
    with open("completeGameData.json", 'w+') as output:
        output.write('[')
        lines = f.readlines()
        for i in range (0, len(lines)):
            if (lines[i] == '}{\n'):
                lines[i] = '},{\n'
            lines[i] = lines[i].replace('\n', ' ')
            output.write(lines[i])
        output.write(']')

os.remove("tmp.json")
