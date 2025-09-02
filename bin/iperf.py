#!/usr/bin/env python2
'''
./iperf.py client 127.0.0.1:8111 400
./iperf.py server 0.0.0.0:8111
'''
import sys
import socket
import time
def parse_addr(addr):
    host, port = addr.split(':')
    return host, int(port)

def server(listen_addr='0.0.0.0:9999'):
    host, port = parse_addr(listen_addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print 'listen: %s'%(listen_addr)
    conn, addr = s.accept()
    print 'Connected by', addr
    while 1:
        data = conn.recv(1024)
        if not data: break
        conn.sendall(data)
    conn.close()

class Stat:
    def __init__(self):
        self.last_time, self.last_count = time.time(), 0
        self.count = 0
    def event(self):
        self.count += 1
        now = time.time()
        if now > self.last_time + 1:
            latency = 1000.0 * (now - self.last_time)/(self.count - self.last_count)
            print 'latency=%.2fms'%(latency)
            self.last_time, self.last_count = now, self.count

def client(addr='127.0.0.1:9999', req_size=400):
    host, port = parse_addr(addr)
    req_size = int(req_size)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    msg = '0' * req_size
    stat = Stat()
    while True:
        s.send(msg)
        s.recv(req_size)
        stat.event()

def help():
    print __doc__

if __name__ == '__main__':
    len(sys.argv) > 1 or help() or sys.exit(1)
    func = globals().get(sys.argv[1])
    callable(func) or help() or sys.exit(2)
    ret = func(*sys.argv[2:])
    if ret != None:
        print ret

