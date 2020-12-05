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

class R2ATop(IR2A):

    throughput = 0
    lastRequest = 0

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.whiteboard = whiteboard.Whiteboard.get_instance()
        self.ini = time.time()
        self.bf_list = [1.0249178501583587, 1.97817287389064, 2.9006674409712723, 3.8867132351702494, 4.828899746773227, 5.830034454522184, 7.571019392147242, 9.077943787062908, 11.534472007821076, 13.187730310343895, 17.457305940297935, 22.830951763236005, 28.950354295618393, 40.56359512465341, 50, 60, 75.43924325865669, 92.75347528768623, 98.32051764363828, 106.7380880912145]

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.send_up(msg)

    def lastLessThan(self, vals, target):
        for i in range(len(vals)):
            if vals[i] >= target:
                return max(0, i - 1)
        return len(vals) - 1

    def handle_segment_size_request(self, msg):
        # time to define the segment quality choose to make the request
        #qiId = self.lastLessThan(self.qi, self.throughput)
        bufferSz = self.whiteboard.get_amount_video_to_play()        
        qiId = 0
        segsize = msg.get_segment_size()
        if time.time()-self.ini < 0.5:
            qiId = 0
        else:
            y = []
            for i in range(len(self.bf_list)):
                # print(i)
                # print(bufferSz/self.bf_list[i])
                y.append(abs(bufferSz/(segsize)-self.bf_list[i]))

            print(bufferSz)
            print(y)
            qiId = max(qiId, numpy.argmin(y))
            qiId = max(qiId, 0)
            qiId = min(qiId, 19)

        msg.add_quality_id(self.qi[qiId])
        self.lastRequest = time.time()
        self.send_down(msg)

    # Log in milliseconds the time took to receive a package
    def logPackageArrivalDelta(self):
        logger.log(f'Package response time: {math.floor(1000 * (time.time() - self.lastRequest))}')

    def handle_segment_size_response(self, msg):
        self.logPackageArrivalDelta()
        self.throughput = msg.get_bit_length() / (time.time() - self.lastRequest)
        
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass