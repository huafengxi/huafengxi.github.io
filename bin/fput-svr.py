#!/usr/bin/env python2
'''
./fput-svr.py 9111
# bash version
while true; do nc -4 -l -p 9111 > fname=upload.$(date +%Y%m%d%H%M%S); done
'''
import sys
def help(): print __doc__
len(sys.argv) == 2 or help() or sys.exit(1)

import time
import SocketServer
import threading
class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        path = 'upload.{}'.format(int(time.time()))
        with open(path, 'w') as f:
            while True:
                data = self.request.recv(65536)
                if not data: break
                f.write(data)
        self.request.close()
        print 'write file {}'.format(path)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

port = int(sys.argv[1])
server = ThreadedTCPServer(('0.0.0.0', port), MyTCPHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
print 'server start: {}'.format(port)
while True:
    time.sleep(1)