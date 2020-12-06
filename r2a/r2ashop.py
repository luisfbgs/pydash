# -*- coding: utf-8 -*-
"""
@authors: Caio Brandão, Léo Moraes, Luis Felipe Silva 26/11/2020

An implementation example of a very cool R2A Algorithm.

The quality list is obtained with the parameter of handle_xml_response()
method and the choice is made inside of handle_segment_size_request(),
before sending the message down.

In this algorithm the quality choice is made in a very cool way.
"""
import time, numpy;
from player.parser import *
from r2a.ir2a import IR2A
import base.whiteboard as whiteboard
import logger
import math

class R2AShop(IR2A):

    throughput = 0
    lastRequest = 0
    tabom = 0

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.whiteboard = whiteboard.Whiteboard.get_instance()
        self.ini = time.time()

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # time to define the segment quality choose to make the request
        bufferSz = self.whiteboard.get_amount_video_to_play()        
        qiId = 0
        segsize = msg.get_segment_size()
        if buferSz >= self.whiteboard.get_max_buffer_size() - 2:
            self.tabom += 1
        else:
            self.tabom = 0
        if time.time()-self.ini >= 0.5:
            for i in range(len(self.qi)):
                if bufferSz ** (1 + 0.1 * tabom) > self.qi[i] / self.qi[0] and self.throughput >= self.qi[i]:
                    qiId = i
                else:
                    break
            

        msg.add_quality_id(self.qi[qiId])
        self.lastRequest = time.time()
        self.send_down(msg)

    # Log in milliseconds the time took to receive a package
    def logPackageArrivalDelta(self):
        logger.log(f'Package response time: {math.floor(1000 * (time.time() - self.lastRequest))}')

    def handle_segment_size_response(self, msg):
        newThroughput = msg.get_bit_length() / (time.time() - self.lastRequest)
        self.throughput = self.throughput * 0.5 + newThroughput * 0.5
        self.logPackageArrivalDelta()
        self.throughput = msg.get_bit_length() / (time.time() - self.lastRequest)
        
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
