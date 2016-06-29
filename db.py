# -*- coding: utf-8 -*-

# Save data from the MySensor serial gateway to the database

import sqlite3
import datetime
import logger
from passlib.hash import pbkdf2_sha256
import hemmastatic as hs

DBNAME = 'hemma.db'

log = logger.Logger(logger.DEBUG)


def getSensorsDataJSON():
    con = sqlite3.connect(DBNAME)
    return_string = '{"sensors" : ['

    cursor = con.execute("SELECT DISTINCT NODE_ID FROM MIN_MAX_VALUES")
    nodes = cursor.fetchall()
    con.close()

    for node in nodes:
        return_string = return_string + '{ "node_id" : "' + str(node[0]) + '", "subs" : '
        return_string = return_string + str(getSensorDataJSON(node[0]))
        return_string = return_string + ' },'

    return_string = return_string[:-1] + ']}'

    return return_string


def getSensorDataJSON(node_id):
    return_string = "["
    con = sqlite3.connect(DBNAME)
    cursor = con.execute("SELECT CHILD_ID, SUB_TYPE, CURRENT, MIN_VALUE, MAX_VALUE, TIMESTAMP FROM MIN_MAX_VALUES WHERE NODE_ID = ?", (node_id,))
    sub_sensor = cursor.fetchall()

    for sub in sub_sensor:
        time_stamp = sub[5][0:10] + " " + sub[5][11:19]
        return_string = return_string + '{"type":"' + hs.sub_type_list[sub[1]] + '", "value" : "' + sub[2] + '", "unit_sign" : "' + hs.unit_list[sub[1]]
        return_string += '","max":"' + str(sub[4]) + '","min":"' + str(sub[3]) + '","timestamp":"' + str(time_stamp) + '"},'

    return_string = return_string[:-1] + "]"

    return return_string


def saveBatteryLevel(node_id, payload):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)
    value = int(float(payload))
    d = str(datetime.datetime.now().isoformat())

    cursor = con.execute("SELECT COUNT(NODE_ID) FROM BATTERY WHERE NODE_ID = ?", (node_id,))
    rows = cursor.fetchone()
    if rows[0] == 1:
        con.execute("UPDATE BATTERY SET VALUE = ?, TIMESTAMP = ? WHERE NODE_ID = ?", (value, d, node_id))
    else:
        con.execute("INSERT INTO BATTERY (NODE_ID, VALUE, TIMESTAMP) VALUES(?,?,?)", (node_id, value, d))
    con.commit()
    con.close()

    log.Writelog("Save battery info for node " + str(node_id), logger.DEBUG)


def getBatteryLevel(node_id):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)

    cursor = con.execute("SELECT NODE_ID, VALUE, TIMESTAMP FROM BATTERY WHERE NODE_ID = ?", (node_id, ))
    row = cursor.fetchone()

    con.commit()
    con.close()

    return row


def getAvailableSensorId():
    con = sqlite3.connect(DBNAME)

    # Change so that we look in all sensor tables
    cursor = con.execute("SELECT MAX(NODE_ID) FROM SENSOR_VALUES")
    row = cursor.fetchone()

    con.commit()
    con.close()

    return row[0] + 1


def saveValue(node_id, child_id, sub_type, value):
    # TODO fix more error handling check if the value type and the sensor type matches
    con = sqlite3.connect(DBNAME)
    d = str(datetime.datetime.now().isoformat())
    sub_type = int(sub_type)
    node_id = int(node_id)
    child_id = int(child_id)
    value = str(value)

    # Only intrestead in the current value for a binary switch
    if sub_type == hs.V_TRIPPED:
        cursor = con.execute("SELECT COUNT(VALUE) FROM SENSOR_VALUES WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?", (node_id, sub_type, child_id))

        if cursor.fetchone()[0] == 0:
            con.execute("INSERT INTO SENSOR_VALUES (NODE_ID, CHILD_ID, SUB_TYPE, TIMESTAMP, VALUE) VALUES(?,?,?,?,?)", (node_id, child_id, sub_type, d, value))
        else:
            con.execute("UPDATE SENSOR_VALUES SET VALUE = ?, TIMESTAMP = ? WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?",(value, d, node_id, sub_type, child_id))

    else:
        con.execute("INSERT INTO SENSOR_VALUES (NODE_ID, CHILD_ID, SUB_TYPE, TIMESTAMP, VALUE) VALUES(?,?,?,?,?)",(node_id, child_id, sub_type, d, value))

    # Set min max values for these sub types
    if sub_type == hs.V_TEMP or sub_type == hs.V_HUM or sub_type == hs.V_PRESSURE:
        try:
            value = float(value)

            cursor = con.execute("SELECT COUNT(*) FROM MIN_MAX_VALUES WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?", (node_id, sub_type, child_id))

            if cursor.fetchone()[0] == 0:
                con.execute("INSERT INTO MIN_MAX_VALUES (NODE_ID, SUB_TYPE, CHILD_ID, MIN_VALUE, MAX_VALUE, CURRENT, TIMESTAMP) VALUES(?,?,?,?,?,?,?)", (node_id, sub_type, child_id, value, value, value, d))
            else:
                con.execute("UPDATE MIN_MAX_VALUES SET CURRENT = ?, TIMESTAMP = ? WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?", (value, d, node_id, sub_type, child_id))
                con.execute("UPDATE MIN_MAX_VALUES SET MIN_VALUE = ? WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ? AND MIN_VALUE > ?", (value, node_id, sub_type, child_id, value))
                con.execute("UPDATE MIN_MAX_VALUES SET MAX_VALUE = ? WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ? AND MAX_VALUE < ?", (value, node_id, sub_type, child_id, value))

        except ValueError:
            log.Writelog("Error parsing value to float", logger.ERROR)

    con.commit()
    con.close()


def getSensorValues(node_id, child_id, sub_type):
    con = sqlite3.connect(DBNAME)
    sub_type = int(sub_type)
    node_id = int(node_id)
    child_id = int(child_id)

    cursor = con.execute("SELECT NODE_ID, SUB_TYPE, CHILD_ID, TIMESTAMP, VALUE FROM SENSOR_VALUES WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?", (node_id, sub_type, child_id))
    rows = cursor.fetchall()

    con.commit()
    con.close()

    return rows


def getMinMaxValues(node_id, child_id, sub_type):
    con = sqlite3.connect(DBNAME)
    sub_type = int(sub_type)
    node_id = int(node_id)
    child_id = int(child_id)

    cursor = con.execute("SELECT MIN_VALUE, MAX_VALUE FROM MIN_MAX_VALUES WHERE NODE_ID = ? AND SUB_TYPE = ? AND CHILD_ID = ?", (node_id, sub_type, child_id))
    row = cursor.fetchone()

    con.commit()
    con.close()

    return row


def saveProtocol(node_id, protocol):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)
    protocol = str(protocol)

    cursor = con.execute("SELECT COUNT(NODE_ID) FROM SENSOR_PROTOCOLS WHERE NODE_ID = ?", (node_id,) )
    rows = cursor.fetchone()
    if rows[0] == 1:
        con.execute("UPDATE SENSOR_PROTOCOLS SET PROTOCOL = ? WHERE NODE_ID = ?", (protocol, node_id) )
    else:
        con.execute("INSERT INTO SENSOR_PROTOCOLS (NODE_ID, PROTOCOL) VALUES(?,?)", (node_id, protocol) )
    con.commit()
    con.close()

    log.Writelog("Save protocol information for node " + str(node_id), logger.DEBUG)


def getProtocol(node_id):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)

    cursor = con.execute("SELECT PROTOCOL, NAME, VERSION FROM SENSOR_PROTOCOLS WHERE NODE_ID = ?", (node_id,))
    row = cursor.fetchone()

    con.commit()
    con.close()

    return row


def saveSketchName(node_id, payload):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)
    payload = str(payload)

    cursor = con.execute("SELECT COUNT(NODE_ID) FROM SENSOR_PROTOCOLS WHERE NODE_ID = ?", (node_id,))
    rows = cursor.fetchone()
    if rows[0] == 1:
        con.execute("UPDATE SENSOR_PROTOCOLS SET NAME = ? WHERE NODE_ID = ?", (payload, node_id))
    else:
        con.execute("INSERT INTO SENSOR_PROTOCOLS (NODE_ID, NAME) VALUES(?,?)", (node_id, payload))
    con.commit()
    con.close()

    log.Writelog("Save name information for node " + str(node_id), logger.DEBUG)


def saveSketchVersion(node_id, payload):
    con = sqlite3.connect(DBNAME)
    node_id = int(node_id)
    payload = str(payload)

    cursor = con.execute("SELECT COUNT(NODE_ID) FROM SENSOR_PROTOCOLS WHERE NODE_ID = ?", (node_id,))
    rows = cursor.fetchone()
    if rows[0] == 1:
        con.execute("UPDATE SENSOR_PROTOCOLS SET VERSION = ? WHERE NODE_ID = ?", (payload, node_id))
    else:
        con.execute("INSERT INTO SENSOR_PROTOCOLS (NODE_ID, VERSION) VALUES(?,?)", (node_id, payload))
    con.commit()
    con.close()

    log.Writelog("Save version information for node " + str(node_id), logger.DEBUG)


def saveSensor(node_id, sub_type, protocol):
    node_id = int(node_id)
    sub_type = int(sub_type)
    protocol = str(protocol)
    con = sqlite3.connect(DBNAME)
    cursor = con.execute("SELECT COUNT(NODE_ID) FROM SUB_SENSORS WHERE NODE_ID = ? and SUB_TYPE = ?", (node_id, sub_type))
    row = cursor.fetchone()
    if row[0] == 1:
        con.execute("UPDATE SUB_SENSORS SET PROTOCOL = ? WHERE NODE_ID = ? and sub_type = ?", (protocol, node_id, sub_type))
    else:
        con.execute("INSERT INTO SUB_SENSORS (NODE_ID, SUB_TYPE, PROTOCOL) VALUES(?,?,?)", (node_id, sub_type, protocol))
    con.commit()
    con.close()

    log.Writelog("Save sub sensor information for node " + str(node_id) + ", " + str(sub_type), logger.DEBUG)


def getSensors(node_id=None):
    con = sqlite3.connect(DBNAME)

    if node_id is None:
        cursor = con.execute("SELECT NODE_ID, SUB_TYPE, PROTOCOL FROM SUB_SENSORS")
    else:
        node_id = int(node_id)
        cursor = con.execute("SELECT NODE_ID, SUB_TYPE, PROTOCOL FROM SUB_SENSORS WHERE NODE_ID = ?", (node_id,) )

    rows = cursor.fetchall()

    con.commit()
    con.close()

    return rows


def savePassword(user, password):
    hash = pbkdf2_sha256.encrypt(password, rounds=10000)

    con = sqlite3.connect(DBNAME)
    cursor = con.execute("SELECT COUNT(USER_ID) FROM USERS WHERE USER_ID = ?", (user,))
    rows = cursor.fetchone()
    if rows[0] == 1:
        # user already exists just change password
        con.execute("UPDATE USERS SET PASSWORD = ? WHERE USER_ID = ?", (hash, user))
    else:
        # new user
        con.execute("INSERT INTO USERS (USER_ID, PASSWORD) VALUES(?,?)", (user, hash))
    con.commit()
    con.close()


def verifyUser(user, password):
    con = sqlite3.connect(DBNAME)
    cursor = con.execute("SELECT PASSWORD FROM USERS WHERE USER_ID = ?", (user,))
    rows = cursor.fetchone()
    if rows is None:
        return False
    con.commit()
    con.close()
    return pbkdf2_sha256.verify(password, rows[0])


# Just for test
def removeUser(user):
    con = sqlite3.connect(DBNAME)
    con.execute("DELETE FROM USERS WHERE USER_ID = ?", (user,))
    con.commit()
    con.close()


# Just for test
def checkUser(user):
    con = sqlite3.connect(DBNAME)
    cursor = con.execute("SELECT COUNT(*) FROM USERS WHERE USER_ID = ?", (user,))
    numberOfRows = cursor.fetchone()[0]
    con.commit()
    con.close()
    if numberOfRows == 1:
        return True
    else:
        return False
