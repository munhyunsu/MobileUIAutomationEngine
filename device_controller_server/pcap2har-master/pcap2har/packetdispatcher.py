#-*- coding: utf-8 -*-

import dpkt
import tcp
import udp

#pcap.py에서 pcap을 파싱하기위해서 불리는 함수
class PacketDispatcher:
    '''
    takes a series of dpkt.Packet's and calls callbacks based on their type

    For each packet added, picks it apart into its transport-layer packet type
    and adds it to an appropriate handler object. Automatically creates handler
    objects for now.

    Members:
    * flowbuilder = tcp.FlowBuilder
    * udp = udp.Processor
    '''

    def __init__(self):
        self.tcp = tcp.FlowBuilder()
        self.udp = udp.Processor()

    def add(self, ts, buf, eth): # pcap.py의 ParsePcap에서 패킷들 하나씩 읽고
                                 # 타입 확인 한 후 dispatcher에 하나씩 add함
        '''
        ts = dpkt timestamp
        buf = original packet data
        eth = dpkt.ethernet.Ethernet, whether its real Ethernet or from SLL
        '''
        #decide based on pkt.data
        # if it's IP...
        #IP패킷 확인후 프로토콜별로 캐스팅
        if (isinstance(eth.data, dpkt.ip.IP) or
            isinstance(eth.data, dpkt.ip6.IP6)):
            ip = eth.data
            # if it's TCP
            if isinstance(ip.data, dpkt.tcp.TCP):
                tcppkt = tcp.Packet(ts, buf, eth, ip, ip.data) # 여기서 HTTP까지 가진 않음. tcp패킷으로 캐스팅
                self.tcp.add(tcppkt) #tcp.FlowBuilder.add함수
            # if it's UDP...
            elif isinstance(ip.data, dpkt.udp.UDP):
                self.udp.add(ts, ip.data)

    def finish(self):
        #This is a hack, until tcp.Flow no longer has to be `finish()`ed
        self.tcp.finish()
