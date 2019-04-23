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

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass
        
class CustomHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(("<html><body><h1>hi!</h1></body></html>").encode('utf-8'))

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        output = sparkTODO(post_data)
        self._set_headers()
        self.wfile.write(("<html><body><h1>POST!</h1></body></html>" + str(output)).encode('utf-8'))
    


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
    port = 8001
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