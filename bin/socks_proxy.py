#!/usr/bin/env python
'''
# with nc:
ssh -o ProxyCommand='nc -x 127.0.0.1:8123 %h %p' user@awshost
# without nc:
ssh -o ProxyCommand='socks_proxy.py socks5h://127.0.0.1:8123 %h %p' user@awshost
'''
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import re
import socks
import threading

def parse_proxy_url(url):
    m = re.match('(\w+)://([^:]+):(\d+)', url)
    if not m: raise Exception("invalid proxy")
    return m.group(2), int(m.group(3))

def prepare_sock(proxy_ip, proxy_port):
    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, proxy_ip, proxy_port, rdns=True)
    return s

def sendfile(sfd, ifd):
    while True:
        msg = os.read(ifd.fileno(), 4096)
        if not msg: break
        sfd.sendall(msg)

def help():
    print __doc__

len(sys.argv) == 4 or help() or sys.exit()
proxy, host, port = sys.argv[1:]
proxy_ip, proxy_port = parse_proxy_url(proxy)
s = prepare_sock(proxy_ip, proxy_port)
s.connect((host, int(port)))

t = threading.Thread(target=sendfile, args=(s, sys.stdin))
t.setDaemon(True)
t.start()
while True:
   msg = s.recv(4096)
   if not msg: break
   os.write(sys.stdout.fileno(), msg)