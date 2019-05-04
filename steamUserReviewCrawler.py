import time
import requests
import json
import logging
import sys
import os
import filecmp


log = logging.getLogger('UserReviewCrawler')
hdlr = logging.FileHandler('logUserReviewCrawler.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.INFO)


#parameters
autoUpdate = False
loadFromFile = True

def getUserReviews(index, items):
        res = requests.get('https://store.steampowered.com/appreviews/'+str(items['appid'])+'?json=1&language=all&purchase_type=all')
        #sleep until request rate is low enough
        while res.reason == 'Too Many Requests':
            log.info('rate limit exceeded\n')
            time.sleep(60) #sleep for 60 sec and then request again
            res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
        return res




while (True):
    #app list

    # load from file instead
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



    with open ('userReviews.json', 'w') as f:
    #    for index, items in enumerate(applist):
    #        if items['appid'] == last_appid:
    #            last_index = index
        retries = 0
        for i in range(0, len(applist) - 1):
            while (retries <= 1):
                try:
                    res = getUserReviews(i, applist[i])
                    resj = res.json()
                    summary = resj['query_summary']
                    summary['appid'] = applist[i]['appid']
                    resstring = json.dumps(summary)

                    f.write(resstring)
                    f.write('\n')
                    log.info("Querying reviews: Current appid:" + str(applist[i]['appid']) + ' Progress:' + str(float(i)/float(len(applist))*100) + '  done\n')
                    retries = 0 #sucess, reset retry
                    break
                except:
                    e = sys.exc_info()[0]
                    log.error("Querying reviews: Exception found at index: " + str(i) + ", appid: " + str(applist[i]['appid']) + ", error: "  + str(e) + "\n")
                    retries = retries + 1
                    #retry 
                    continue
            retries = 0
    #        if index < last_index:
    #            continue
    if (autoUpdate == False):
        break
    time.sleep(64800) #sleep one day and check applist again

