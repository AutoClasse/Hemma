# -*- coding: utf-8 -*-

#create tables for Hemma controler

import sqlite3

DBNAME = 'hemma.db'

con = sqlite3.connect(DBNAME)
con.execute('''CREATE TABLE SENSOR_PROTOCOLS
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NODE_ID     INTEGER            NOT NULL,
    PROTOCOL    TEXT            NOT NULL);''')


con.execute('''CREATE TABLE USERS
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USER_ID     TEXT            NOT NULL,
    PASSWORD    TEXT            NOT NULL);''')


con.execute('''CREATE TABLE SUB_SENSORS
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NODE_ID     INTEGER         NOT NULL,
    SUB_TYPE    INTEGER         NOT NULL,
    PROTOCOL    TEXT            NOT NULL);''')

con.execute('''CREATE TABLE SENSOR_VALUES
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NODE_ID     INTEGER         NOT NULL,
    CHILD_ID    INTEGER         NOT NULL,
    SUB_TYPE    INTEGER         NOT NULL,
    TIMESTAMP   TEXT            NOT NULL,
    VALUE       TEXT            NOT NULL);''')

con.execute('''CREATE INDEX INDEX_VALUES
    ON SENSOR_VALUES
    (NODE_ID, TIMESTAMP);''')

con.execute('''CREATE TABLE MIN_MAX_VALUES
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NODE_ID     INTEGER         NOT NULL,
    CHILD_ID    INTEGER         NOT NULL,
    SUB_TYPE    INTEGER         NOT NULL,
    MIN_VALUE    FLOAT           NOT NULL,
    MAX_VALUE    FLOAT           NOT NULL);''')

con.execute('''CREATE INDEX NODE_INDX
    ON MIN_MAX_VALUES
    (NODE_ID);''')

con.commit()
con.close()
