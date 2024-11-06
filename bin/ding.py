#!/usr/bin/env python2
'''
echo ...| ./ding.py <token>
echo ...| DING=... ./ding.py
'''
import sys, os
import socket
# https://github.com/Anorov/PySocks
try:
    import socks
    from sockshandler import SocksiPyHandler
except:
    socks = None
    print 'import socks fail, proxy will not work'
import json
import urllib2
opener = urllib2.build_opener()

proxy = os.getenv('ALL_PROXY')
print 'proxy=%s'%(proxy)
if proxy and socks:
     protocol, hostport = proxy.split('://')
     host, port = hostport.split(':')
     if protocol.startswith('socks5'):
         print 'use socks proxy: %s'%(hostport)
         opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, host, int(port), True))

def post_json(url, d):
    req = urllib2.Request(url, data=json.dumps(d), headers={'Content-Type': 'application/json; charset=utf-8'})
    return opener.open(req).read()
def make_msg(msg):
    return dict(msgtype='text', text=dict(content=msg))

def help():
    print __doc__

token = len(sys.argv) > 1 and sys.argv[1] or os.getenv("DING")
url = 'https://oapi.dingtalk.com/robot/send?access_token=%s'%(token)
msg = not sys.stdin.isatty() and sys.stdin.read() or ''
(url and msg) or help() or sys.exit(1)
print json.dumps(make_msg(msg))
print post_json(url, make_msg(msg))
