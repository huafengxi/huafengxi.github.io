#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
./shsvr.py 8008 # start server
quiet=False ./shsvr.py 127.0.0.1:8008 ls # execute sh cmd
./shsvr.py 127.0.0.1:8008 ls # execute sh cmd
cat a.txt | ./shsvr.py 127.0.0.1:8008 'cat >up.txt #need_stdin=True' # upload a.txt
./shsvr.py 127.0.0.1:8008 'cat a.txt' > down.txt # download a.txt
cat a.sh | ./shsvr.py 127.0.0.1:8008 # execute a sequence of cmd in a.sh
# 'END' is a special cmd to indicate end of cmd sequence
'''
import sys, os
import time
import socket
import SocketServer
import threading
from subprocess import Popen,PIPE,STDOUT

def info(msg):
    if os.getenv('quiet') != 'True':
        sys.stderr.write("# " + msg + '\n')

def popen(cmd, input, cwd=None):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd, close_fds=True)
    return p.communicate(input)[0]

def read_stdin():
    return sys.stdin.read()

def tune_sock(sock):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    #sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)

def encode_cmd(cmd, input):
    return '%s\n%s'%(cmd, input)

def decode_cmd(cmd):
    return cmd.split('\n', 1)

class PacketCodec:
    def __init__(self, sock):
        self.sock = sock
    def recvall(self, limit):
        remain, segs = limit, []
        while remain > 0:
            seg = self.sock.recv(remain)
            if not seg:
                return None
            remain -= len(seg)
            segs.append(seg)
        return ''.join(segs)
    def encode(self, req):
        self.sock.sendall('%8x'%(len(req)))
        self.sock.sendall(req)
    def decode(self):
        plen = int(self.recvall(8), 16)
        return self.recvall(plen)

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        tune_sock(self.request)
        codec = PacketCodec(self.request)
        while True:
            req, input = decode_cmd(codec.decode())
            if req == 'END':
                break
            info("accept: %s: req: '%s' input: %dbytes"%(self.client_address, req, len(input)))
            # just send back the same data, but upper-cased
            codec.encode(popen(req, input))
        info('close: %s'%(self.client_address,))

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
def run_server(host, port):
    server = ThreadedTCPServer((host, port), MyTCPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    info('server start: %s:%d'%(host, port))
    while True:
        time.sleep(1)

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.codec = PacketCodec(self.sock)
        tune_sock(self.sock)
    def execute(self, req, input):
        self.codec.encode(encode_cmd(req, input))
        if req == 'END':
            return
        start_ts = time.time()
        resp = self.codec.decode()
        end_ts = time.time()
        sys.stdout.write(resp)
        duration_ts = (end_ts - start_ts) * 1000000;
        info("request: %s input: %dbytes response: %d trx_time: %d bandwidth: %fMB"%(req, len(input), len(resp), duration_ts, len(resp)/duration_ts))

def run_client(host, port, reqs):
    client = Client(host, port)
    for req, input in reqs:
        client.execute(req, input)

def help():
    print __doc__;

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        help()
    elif ':' in sys.argv[1]:
        host, port = sys.argv[1].split(':')
        if len(sys.argv) == 2:
            run_client(host, int(port), [(cmd.strip(), '') for cmd in sys.stdin.readlines() + ['END']])
        else:
            run_client(host, int(port), [(sys.argv[2], ('need_stdin=True' in sys.argv[2]) and read_stdin() or ''), ('END', '')])
    else:
        run_server("0.0.0.0", int(sys.argv[1]))

