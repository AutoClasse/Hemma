# -*- coding: utf-8 -*-

# Simple Controler for mySensor.org serialgateway
# 2016-02-23

import serial
import logger
import Queue
import threading
import hemmaconfig as hc
import hemmastatic as hs
import db
import datetime
import calendar

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
                if(self.sanityCheck(message_list)):
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

    def sanityCheck(self, message_list):
        # message_list must be six elements long
        if (len(message_list) != 6):
            return False

        # Check node_id 0-254
        node_id = self.num(message_list[0])
        if(node_id > 254 or node_id < 0 or node_id is False):
            return False

        # Check child_sensor_id 0-254
        child_sensor_id = self.num(message_list[1])
        if(child_sensor_id > 254 or child_sensor_id < 0 or child_sensor_id is False):
            return False

        # Check message_type 0-4
        message_type = self.num(message_list[2])
        if(message_type > 4 or message_type < 0 or message_type is False):
            return False

        # Check ack 0 or 1
        ack = self.num(message_list[3])
        if (ack < 0 or ack > 1 or ack is False):
            return False

        # Check sub_type depends on message_type
        # m    vaild values
        # 0    0-35
        # 1    0-46
        # 2    0-46
        # 3    0-17
        # 4    ?
        sub_type = self.num(message_list[4])
        upper_limit = 0
        if (message_type == 0):
            upper_limit = 35
        if (message_type == 1):
            upper_limit = 46
        if (message_type == 2):
            upper_limit = 46
        if (message_type == 3):
            upper_limit = 17

        if (sub_type < 0 or sub_type > upper_limit or sub_type is False):
            return False

        # TODO Check payload many combinations

        return True

    def process(self, message_list):
        log.Writelog("Prossesing message [" + str(message_list) + "]", logger.DEBUG)
        if self.message_type == hs.PRESENTATION:
            if self.child_sensor_id == hs.NODE_SENSOR_ID:
                db.saveProtocol(self.node_id, self.payload)
            else:
                db.saveSensor(self.node_id, self.sub_type, self.payload)
        elif self.message_type == hs.SET:
            db.saveValue(self.node_id, self.child_sensor_id, self.sub_type, self.payload)
        elif self.message_type == hs.REQ:
            log.Writelog("REQ is not supported yet", logger.INFO)
        elif self.message_type == hs.INTERNAL:
            if self.sub_type == hs.I_BATTERY_LEVEL:
                # Use this to report the battery level (in percent 0-100).
                db.saveBatteryLevel(self.node_id, self.payload)

            if self.sub_type == hs.I_TIME:
                # Sensors can request the current time from the Controller using this message. The time will be reported as the seconds since 1970
                self.sendTime(self.node_id, self.child_sensor_id)

            if self.sub_type == hs.I_ID_REQUEST:
                # Use this to request a unique node id from the controller.
                self.sendNextAvailableSensorId()

            if self.sub_type == hs.I_CONFIG:
                # Config request from node. Reply with (M)etric or (I)mperal back to sensor.
                self.sendConfig(self.node_id)

            if self.sub_type == hs.I_SKETCH_NAME:
                # Optional sketch name that can be used to identify sensor in the Controller GUI
                db.saveSketchName(self.node_id, self.payload)

            if self.sub_type == hs.I_SKETCH_VERSION:
                # Optional sketch version that can be reported to keep track of the version of sensor in the Controller GUI.
                db.saveSketchVersion(self.node_id, self.payload)

        elif self.message_type == hs.STREAM:
            log.Writelog("STREAM is not supported yet", logger.INFO)
        else:
            log.Writelog("Message type " + str(self.message_type) + " is unknown ", logger.WARNING)

    def sendConfig(self, node_id):
        command = str(node_id) + ";255;3;0;6;" + hc.UNITS + "\n"
        ser.write(command)
        log.Writelog("Send command: " + command, logger.DEBUG)

    def sendNextAvailableSensorId(self):
        sensor_id = db.getAvailableSensorId()
        command = "255;255;3;0;4;"+str(sensor_id)+"\n"
        ser.write(command)
        log.Writelog("Send command: " + command, logger.DEBUG)

    def sendTime(self, node_id, child_sensor_id):
        date = datetime.datetime.now()
        timestamp = calendar.timegm(date.timetuple())
        command = str(node_id)+";"+str(child_sensor_id)+";3;0;1;"+str(timestamp)+"\n"
        ser.write(command)
        log.Writelog("Send command: " + command, logger.DEBUG)

    def num(self, s):
        try:
            return int(s)
        except ValueError:
            log.Writelog("Can't parse ''" + s + "' is not an integer", logger.WARNING)
            return False


def main():
    gatewayListner().start()

if __name__ == "__main__":
    main()
