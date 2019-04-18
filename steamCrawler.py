from steam import *
import requests
api = WebAPI(key="D2C78C484D8A9EC812B18BD2E24EE228")
a = api.doc()
S = api.call('ISteamWebAPIUtil.GetServerInfo')

vanityurl = "HongyuDing"
res = api.call('ISteamUser.ResolveVanityURL', vanityurl=vanityurl)
steamID = res['response']['steamid']

appid=814380
#achievement is friend-only by default
achievement = api.call('ISteamUserStats.GetPlayerAchievements', steamid=steamID, appid=appid)

playerCount = api.call('ISteamUserStats.GetNumberOfCurrentPlayers', appid=appid)

achievementsPercentage = api.call('ISteamUserStats.GetGlobalAchievementPercentagesForApp', gameid=appid)

OwnedGames = api.call('IPlayerService.GetOwnedGames', steamid=steamID, include_appinfo=False, include_played_free_games=True, appids_filter=0)

playerSummary = api.call('ISteamUser.GetPlayerSummaries', steamids=steamID)

#app list
res = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2')
applist = res.json()['applist']['apps']
# i = 0
# for items in applist:
#     res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(items['appid']))
#     appDetails = res.json()
#     i+=1
# print(i)

#game details (unofficial api)
res = requests.get('http://store.steampowered.com/api/appdetails?appids='+str(appid))
appDetails = res.json()


print()

