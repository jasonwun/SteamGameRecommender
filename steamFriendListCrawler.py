##This orientation is proved having low weight since there is high possibility 
# that we don't get any data from the API due to privacy limit

from steam import *
import requests
api = WebAPI(key="D2C78C484D8A9EC812B18BD2E24EE228")
a = api.doc()
S = api.call('ISteamWebAPIUtil.GetServerInfo')

vanityurl = "dadayin"
steamId = api.call('ISteamUser.ResolveVanityURL', vanityurl=vanityurl)['response']['steamid']


FirstfriendList = api.call("ISteamUser.GetFriendList", steamid=steamId)['friendslist']['friends']
FirstOwnedGameList = []
FirstRecentlyPlayList = []
'''
for i in FirstfriendList:
    
    print(api.call("IPlayerService.GetRecentlyPlayedGames", steamid=i['steamid'], count=100, format='json'))
    print(api.call("IPlayerService.GetOwnedGames", steamid=i['steamid'], include_appinfo=True, include_played_free_games=True, format='json', appids_filter=[]))
'''
print("1st " + str(len(FirstfriendList)) + " friends")

SecondList = []
for i in FirstfriendList:
    llst = [i for x in api.call("ISteamUser.GetFriendList", steamid=i['steamid'])['friendslist']['friends'] if x['steamid'] != i['steamid']]
    SecondList += llst
'''
for i in SecondList:
    print(api.call("IPlayerService.GetRecentlyPlayedGames", steamid=i['steamid'], count=100, format='json'))
    print(api.call("IPlayerService.GetOwnedGames", steamid=i['steamid'], include_appinfo=True, include_played_free_games=True, format='json', appids_filter=[]))
'''
print("2nd " + str(len(SecondList)) + " friends")

ThirdList = []
ThirdOwnedGameList = []
ThirdRecentlyPlayedList = []
for i in SecondList:
    llst = api.call("ISteamUser.GetFriendList", steamid=i['steamid'])['friendslist']['friends']
    ThirdList += llst
for i in ThirdList:
    rep1 = api.call("IPlayerService.GetRecentlyPlayedGames", steamid=i['steamid'], count=100, format='json')['response']
    if 'games' in rep1:
        ThirdRecentlyPlayedList += rep1['games']
    rep2 = api.call("IPlayerService.GetOwnedGames", steamid=i['steamid'], include_appinfo=True, include_played_free_games=True, format='json', appids_filter=[])['response']
    if 'games' in rep2:
        ThirdOwnedGameList += rep2['games']
print("3rd " + str(len(ThirdList)) + " friends")
print("3rd " + str(len(ThirdRecentlyPlayedList)) + " recently played games")
print("3rd " + str(len(ThirdOwnedGameList)) + " owned games")
