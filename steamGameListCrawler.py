# API website: https://steamapi.xpaw.me/#
# iterate through game list and store them in json (for now)
import time
import requests
import json


with open ('gamelist.json', 'w') as f:
    #app list
    res = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2')
    applist = res.json()['applist']['apps']
    for items in applist:
        print(items['appid'])
        res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))

        #sleep until request rate is low enough
        while res.reason == 'Too Many Requests':
            print('rate limit exceeded')
            time.sleep(60) #sleep for 60 sec and then request again
            res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
            
        resj = res.json()
        appDetails = resj[str(items['appid'])]
        print(appDetails['success'])
        if (appDetails['success'] == False):
            continue
        json.dump(appDetails['data'], f, ensure_ascii=False)
        
