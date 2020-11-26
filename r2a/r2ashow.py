# -*- coding: utf-8 -*-
"""
@author: Marcos F. Caetano (mfcaetano@unb.br) 03/11/2020

@description: PyDash Project

In this algorithm the quality choice is based on a estimated throughput
"""

import time;
from player.parser import *
from r2a.ir2a import IR2A
import base.whiteboard as whiteboard

class R2AShow(IR2A):
    throughput = 0
    lastRequest = 0

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.whiteboard = whiteboard.Whiteboard.get_instance()

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
        qiId = self.lastLessThan(self.qi, self.throughput)
        bufferSz = self.whiteboard.get_amount_video_to_play()

        if bufferSz <= 5:
            qiId = max(0, qiId - (15 - bufferSz) // 2)
        elif bufferSz <= 10:
            qiId = max(0, qiId - (13 - bufferSz) // 2)
        else:
            qiId = min(len(self.qi)-1, qiId + (bufferSz - 10) // 5)

        msg.add_quality_id(self.qi[qiId])
        self.lastRequest = time.time()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.throughput = msg.get_bit_length() / (time.time() - self.lastRequest)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
