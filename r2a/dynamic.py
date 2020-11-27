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


class Dynamic(IR2A):

    throughput = 0
    lastRequest = 0

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.whiteboard = whiteboard.Whiteboard.get_instance()
        self.index = 0
        self.t_estimated = 0
        self.t_estimated_1 = 0
        self.delta = 0
        self.throughput = 1
        self.ini = 0

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
        segsize = msg.get_segment_size()

        #Calcula estimated segment size
        aux = 0
        if self.index > 2:
            aux = (1-self.delta)*self.t_estimated_1+self.delta*self.throughput
        else:
            aux = self.throughput


        #Calcula o desvio normalizado de throughput
        p = abs(self.throughput - aux)/aux

        #Atualiza delta
        euler = 2.718281828459045235360287
        self.delta = 1/(1+euler**(-21*(p-0.2)))

        #Calcula o tamanho do segmento esperado
        tmp = (0.95)*aux*bufferSz/segsize
        print('tmp =', tmp)

        x = []
        for i in self.qi:
            x.append(abs(i-tmp))

        #Escolhe o quality index
        qiId = numpy.argmin(x)

        self.t_estimated_1 = self.t_estimated
        self.t_estimated = aux

        self.index += 1
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