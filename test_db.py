# -*- coding: utf-8 -*-

# Test all functions in db.py

# import datetime
import db
import sqlite3
import hemmastatic as hs


def test_cond(value_one, value_two):
    if value_one != value_two:
        print str(type(value_one)) + ", " + str(value_one)
        print str(type(value_two)) + ", " + str(value_two)
        return False
    else:
        return True


def testSaveProtocol():
    node_id = 999
    protocol = "Test protocol"
    name = "name"
    version = "v1"
    db.saveProtocol(node_id, protocol)

    if not test_cond(db.getProtocol(node_id)[0], protocol):
            print "testSaveProtocol() 1 Failed to get protocol from db"
            return False

    db.saveProtocol(node_id, protocol)
    if not test_cond(db.getProtocol(node_id)[0], protocol):
            print "testSaveProtocol() 2 Failed to get protocol from db"
            return False

    db.saveSketchName(node_id, name)
    if not db.getProtocol(node_id)[1] == name:
        print "testSaveProtocol() 3 Failed to get name from db"
        return False

    db.saveSketchVersion(node_id, version)
    if not db.getProtocol(node_id)[2] == version:
        print "testSaveProtocol() 4 Failed to get version from db"
        return False

    return True


def testSaveSensor():
    node_id = 999
    protocol = "Test protocol"
    sub_type = 1

    db.saveSensor(node_id, sub_type, protocol)

    row_one = [(node_id, sub_type, protocol)]
    if not db.getSensors(999) == row_one:
        print "testSaveSensor() 1 Failed to get sensors"
        return False

    if not db.getSensors() == row_one:
        print "testSaveSensor() 2 Failed to get sensors"
        return False

    sub_type_two = 2
    node_id_two = 998
    db.saveSensor(node_id_two, sub_type_two, protocol)

    row_two = [(node_id_two, sub_type_two, protocol)]

    if not db.getSensors(998) == row_two:
        print "testSaveSensor() 3 Failed to get sensors"
        return False

    row_three = [(node_id, sub_type, protocol),(node_id_two, sub_type_two, protocol)]
    if not db.getSensors() == row_three:
        print "testSaveSensor() 4 Failed to get sensors"
        return False

    return True


def testSaveValue():
    node_id = 999
    child_id = 1
    sub_type = hs.V_TEMP
    value = '1.23'

    db.saveValue(node_id, child_id, sub_type, value)

    if not db.getSensorValues(node_id, child_id, sub_type)[0][4] == value:
        print "testSaveValue() 1 Failed to get value"
        return False

    db.saveValue(node_id, child_id, sub_type, value)
    if not len(db.getSensorValues(node_id, child_id, sub_type)) == 2:
        print "testSaveValue() 2 Failed to get values"
        return False

    child_id_two = 2
    sub_type_two = hs.V_TRIPPED
    db.saveValue(node_id, child_id_two, sub_type_two, 1)
    if not db.getSensorValues(node_id, child_id_two, sub_type_two)[0][4] == "1":
        print "testSaveValue() 3 faile to get value"
        return False

    db.saveValue(node_id, child_id_two, sub_type_two, 0)
    if not len(db.getSensorValues(node_id, child_id_two, sub_type_two)) == 1:
        print "testSaveValue() 4 failed to get value"
        return False

    if not db.getMinMaxValues(node_id, child_id, sub_type) == (float(value), float(value)):
        print "testSaveValue() 5 failed to get min max values"
        return False

    value_three = 99.99
    db.saveValue(node_id, child_id, sub_type, value_three)
    if not db.getMinMaxValues(node_id, child_id, sub_type) == (float(value), value_three):
        print "testSaveValue() 6 failed to get min max values"
        return False

    if not db.getAvailableSensorId() == (node_id + 1):
        print "testSaveValue() 7 failed to get next sensor_id"
        return False

    return True


def testSaveBattery():
    node_id = 999
    payload = "50.0"

    db.saveBatteryLevel(node_id, payload)

    if not db.getBatteryLevel(node_id)[1] == int(float(payload)):
        print "testSaveBattery() 1 failed to get battery value"
        return False

    payload = 78
    db.saveBatteryLevel(node_id, payload)
    if not db.getBatteryLevel(node_id)[1] == int(float(payload)):
        print "testSaveBattery() 2 failed to get battery value"
        return False

    return True


def testPassword():
    user = 'Test'
    password = 'ChangeMe'
    wPassword ="Wrong"

    db.savePassword(user, password)

    if not db.checkUser(user):
        print "testPassword() 1 Failed to find user in database."
        return False

    if not db.verifyUser(user, password):
        print "testPassword() 2 Failed to verify password"
        return False

    if db.verifyUser(user, wPassword):
        print "testPassword() 3 Verification passed with wrong password"
        return False

    password = 'cHANGEmE2'

    #Try to change pasword
    db.savePassword(user, password)

    if not db.verifyUser(user, password):
        print "testPassword() 4 Failed to verify password"
        return False

    if db.verifyUser(user, wPassword):
        print "testPassword() 5 Verification passed with wrong password"
        return False

    db.removeUser(user)

    if db.checkUser(user):
        print "testPassword() 6 Failed to remove user from db"
        return False

    return True


def cleandb():
        con = sqlite3.connect(db.DBNAME)
        con.execute("DELETE FROM SENSOR_PROTOCOLS WHERE NODE_ID = 999")
        con.execute("DELETE FROM SUB_SENSORS WHERE NODE_ID IN (998, 998)")
        con.execute("DELETE FROM SENSOR_VALUES WHERE NODE_ID IN (999)")
        con.execute("DELETE FROM MIN_MAX_VALUES WHERE NODE_ID IN (999)")
        con.commit()
        con.close()


def main():
    errors = 0
    tests = [testSaveProtocol, testSaveSensor, testSaveValue, testSaveBattery, testPassword]

    for testFunc in tests:
        if testFunc():
            print str(testFunc.func_name) + " OK"
        else:
            print "Error in " + str(testFunc.func_name)
            errors += 1

    print "Total number of tests: " + str(len(tests))+", passed: " + str(len(tests) - errors) + ", failed: " + str(errors)

    cleandb()


if __name__ == "__main__":
    main()
