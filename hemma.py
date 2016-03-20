# -*- coding: utf-8 -*-

# Simple Controler for mySensor.org serialgateway
# 2016-02-23

import serial
import logger
import Queue
import threading
import hemmaconfig as hc
import hemmastatic as hs

log = logger.Logger(logger.DEBUG)
ser = serial.Serial(hc.SERIAL_PORT, 115200, timeout=1)
stopQueue = Queue.Queue()


class gatewayListner(threading.Thread):
    def run(self):
        running = True
        while(running):
            # TODO check if we have something in the send queue
            # poll gateway
            message = ser.readline()
            if (len(message) > 0):
                log.Writelog("Read message [" + message + "]", logger.DEBUG)
                message_list = message.split(";")
                if(len(message_list) == 6):
                    self.node_id = self.num(message_list[0])
                    self.child_sensor_id = self.num(message_list[1])
                    self.message_type = self.num(message_list[2])
                    self.ack = self.num(message_list[3])
                    self.sub_type = self.num(message_list[4])
                    self.payload = message_list[5]

                    self.process(message_list)
                else:
                    log.Writelog("Not able to parse message from gateway [" + message + "]", logger.WARNING)

            # Check for stop signal
            if not stopQueue.empty():
                running = stopQueue.get()

    def process(self, message_list):
        log.Writelog("Prossesing message [" + str(message_list) + "]", logger.DEBUG)
        if self.message_type == hs.PRESENTATION:
            if self.child_sensor_id == NODE_SENSOR_ID:
                db.saveProtocol(self.node_id, self.payload)
            else:
                db.saveSensor(self.node_id, self.sub_type, self.payload)
        elif self.message_type == hs.SET:
            db.saveValue(self.node_id, self.child_sensor_id, self.sub_type, self.payload)
        elif self.message_type == hs.REQ:
            log.Writelog("REQ is not supported yet", logger.INFO)
        elif self.message_type == hs.INTERNAL:
            log.Writelog("INTERNAL is not supported yet", logger.INFO)
        elif self.message_type == hs.STREAM:
            log.Writelog("STREAM is not supported yet", logger.INFO)
        else:
            log.Writelog("Message type " + str(self.message_type) + " is unknown ", logger.WARNING)

    def num(self, s):
        try:
            return int(s)
        except ValueError:
            log.Writelog("Can't parse message [" + str(self.message_list) + "] '" + s + "' is not an integer", logger.WARNING)


def main():
    gatewayListner().start()

if __name__ == "__main__":
    main()
