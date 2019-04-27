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

#check point
#last_appid = 355100
#last_index = -1

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
    # res = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2')
    # applist = res.json()['applist']['apps']
    # with open ('newapplist.json', 'w') as fapps:
    #     json.dump(applist, fapps, indent = 2)
    # #latest app list is still the same as the last one, no need to re-pull game data
    # #if (filecmp.cmp('newapplist.json', 'applist.json') == True):
    # #    continue
    # with open ('applist.json', 'w') as fapps:
    #     json.dump(applist, fapps, indent = 2)

    # load from file instead
    with open ('newapplist.json', 'r+') as fapps:
        applist = json.load(fapps)


    with open ('completeGameData.json', 'w') as f:
    #    for index, items in enumerate(applist):
    #        if items['appid'] == last_appid:
    #            last_index = index
        retries = 0
        for i in range(0, len(applist) - 1):
            while (retries <= 30):
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
    time.sleep(64800) #sleep one day and check applist again

    # add '[' at the start of file 
    # add ']' at the end of file 
    
    # with open("tmp.json", 'r+') as f:
    #     with open("completeGameData.json", 'w+') as output:
    #         output.write('[')
    #         lines = f.readlines()
    #         for i in range (0, len(lines)):
    #             # if (lines[i] == '}{\n'):
    #             #     lines[i] = '},{\n'
    #             # else:
    #             #     lines[i] = lines[i].replace('\n', ' ')
    #             output.write(lines[i])
    #         output.write(']')

    # os.remove("tmp.json")
