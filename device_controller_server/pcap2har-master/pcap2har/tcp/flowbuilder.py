#-*- coding: utf-8 -*-
import flow as tcp
import logging


class FlowBuilder(object):
    '''
    Builds and stores tcp.Flow's from packets.

    Takes a series of tcp.Packet's and sorts them into the correct tcp.Flow's
    based on their socket. Exposes them in a dictionary keyed by socket. Call
    .add(pkt) for each packet. This will find the right tcp.Flow in the dict and
    call .add() on it. This class should be renamed.

    Members:
    flowdict = {socket: [tcp.Flow]}
    '''

    def __init__(self):
        self.flowdict = {}

    def add(self, pkt):
        '''
        pkt : tcp패킷 받음
        filters out unhandled packets, and sorts the remainder into the correct
        flow
        '''
        #shortcut vars
        src, dst = pkt.socket # ((ip.src, tcp.sport), (ip.dst, tcp.dport))
        srcip, srcport = src
        dstip, dstport = dst
        # filter out weird packets, LSONG
        #5223,5228포트는 뭐지?
        if srcport == 5223 or dstport == 5223:
            logging.warning('hpvirtgrp packets are ignored')
            return
        if srcport == 5228 or dstport == 5228:
            logging.warning('hpvroom packets are ignored')
            return
        if srcport == 443 or dstport == 443:
            logging.warning('https packets are ignored')
            return
        # sort the packet into a tcp.Flow in flowdict. If NewFlowError is
        # raised, the existing flow doesn't want any more packets, so we
        # should start a new flow.
        if (src, dst) in self.flowdict:
            try:
                self.flowdict[(src, dst)][-1].add(pkt) #-1번째에 삽입하는 이유는?
            except tcp.NewFlowError:
                self.new_flow((src, dst), pkt)
        elif (dst, src) in self.flowdict:
            try:
                self.flowdict[(dst, src)][-1].add(pkt)
            except tcp.NewFlowError:
                self.new_flow((dst, src), pkt)
        else:
            self.new_flow((src, dst), pkt) # 새로들어운 flow라면 새로운 flow생성

    def new_flow(self, socket, packet):
        '''
        Adds a new flow to flowdict for socket, and adds the packet.

        Socket must either be present in flowdict or missing entirely, eg., if
        you pass in (src, dst), (dst, src) should not be present.

        Args:
        * socket: ((ip, port), (ip, port))
        * packet: tcp.Packet
        '''
        newflow = tcp.Flow()
        newflow.add(packet) # netflow추출해서 저장하는 기능?
        if socket in self.flowdict: #flowdict에 들어있는지 다시검사하는 이유는?
            self.flowdict[socket].append(newflow)
        else: #flowdict에 들어있지 않으면 새로운 플로우로 삽입
            self.flowdict[socket] = [newflow]

    def flows(self):
        '''
        Generator that iterates over all flows.
        '''
        for flowlist in self.flowdict.itervalues():
            for flow in flowlist:
                yield flow

    def finish(self):
        map(tcp.Flow.finish, self.flows())
