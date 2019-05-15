#!/usr/bin/env python

#Reference https://github.com/Nakiami/MultithreadedSimpleHTTPServer/blob/master/MultithreadedSimpleHTTPServer.py
#Reference https://gist.github.com/bradmontgomery/2219997



# Python 3.x
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Pool
from steam import *
from time import sleep
import subprocess
import json

api = WebAPI(key="D2C78C484D8A9EC812B18BD2E24EE228")

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass
        
class CustomHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(("<h1>Please enter your UserName on Steam</h1>\
            <form action=\"Result.html\" method=\"POST\">\
            <input type=\"text\" name=\"UserName\" id=\"userName\"/>\
            <input type=\"submit\" value=\"Submit\"/>\
            </form>").encode('utf-8'))

    
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        html_raw = "<h2>Here's your recommendation provided by leading edge artificial intelligence</h1>"
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode("utf-8") # <--- Gets the data itself
        
        
        userName = post_data[post_data.index("=")+1:]
        html_raw  = html_raw + "<h3>" + userName + "</h3><table><tr>\
        <th>Name</th>\
        <th>HeaderImage</th>\
        <th>SteamUrl</th>\
        </tr>"
        res = api.call('ISteamUser.ResolveVanityURL', vanityurl=userName)
        print(type(res))

        print(res["response"]["steamid"])
        steamID = res["response"]["steamid"]
        gameResult = api.call('IPlayerService.GetOwnedGames', steamid=steamID, include_appinfo=False, include_played_free_games=True, appids_filter=0)["response"]["games"]
        sleep(5)
        print(gameResult)

        gameIds = [i["appid"] for i in gameResult]
        print(gameIds)
        head = 5
        for i in gameIds:
            print("processing appid: " + str(i))
            cat = subprocess.Popen(["hadoop", "fs", "-cat", "FinalProject/Recommandation/" + str(i) + "/*"], stdout=subprocess.PIPE)
            out = cat.stdout
            count = 0
            print("cat out: " + str(out))
            for line in out:
                if count > head:
                    break
                print("type of line: " + str(type(line)))
                dump = json.loads(line)
                print("dump: " + str(dump))
                html_raw = str(html_raw) + "<tr><td>" + dump["name"].encode("utf-8") + "</td>" + "<td><img width=\"200\" height=\"200\" src=\"" + dump["header_image"].encode("utf-8") + "\"></td>" + "<td><a href=\"https://store.steampowered.com/app/" + str(dump["steam_appid"]) + "\">Visit Steam</a></td></tr>"
                count += 1
        self._set_headers()
        html_raw = html_raw + "</table>"
        #with open('Result.html', 'r') as content_file:
        #    content = content_file.read().encode('utf-8')
        
        self.wfile.write(html_raw)
    


def sparkTODO(steamid):
    return str(steamid) + "sparkoutput"


if sys.argv[1:]:
    address = sys.argv[1]
    if (':' in address):
        interface = address.split(':')[0]
        port = int(address.split(':')[1])
    else:
        interface = '0.0.0.0'
        port = int(address)
else:
    port = 8002
    interface = '0.0.0.0'

if sys.argv[2:]:
    os.chdir(sys.argv[2])

print('Started HTTP server on ' +  interface + ':' + str(port))

server = ThreadingSimpleServer((interface, port), CustomHandler)
try:
    while 1:
        sys.stdout.flush()
        server.handle_request()
except KeyboardInterrupt:
    print('Finished.')
