# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from steam import *
import json
import requests
from time import sleep

# Create your views here.
api = WebAPI(key="D2C78C484D8A9EC812B18BD2E24EE228")

def get_GameDetail(id):
    url = 'http://store.steampowered.com/api/appdetails?appids='+ str(id)
    res = requests.get(url).json()[str(id)]['data']
    print res
    return res

def Index(request):
    return render(request, 'recommenderApp/Index.html')

def Submit(request):
    userName = request.POST['UserName']
    steamId = api.call('ISteamUser.ResolveVanityURL', vanityurl=userName)['response']['steamid']
    return HttpResponseRedirect(reverse('recommenderApp:result', args=(steamId,userName)))

def Result(request, steamId, userName):
    gameList = api.call('IPlayerService.GetOwnedGames', 
                        steamid=steamId, 
                        include_appinfo=False, 
                        include_played_free_games=False, 
                        appids_filter=0)["response"]["games"]
    sleep(5)
    result = [get_GameDetail(str(i['appid'])) for i in gameList]
    return render(request, 'recommenderApp/Result.html',
        {
            'steamId' : steamId,
            'userName' : userName,
            'data' : result
        })