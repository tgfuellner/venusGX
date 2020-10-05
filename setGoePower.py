#!/usr/bin/python
# -*- coding: utf-8 -*-

# See https://github.com/victronenergy/velib_python/blob/master/examples/vedbusitem_import_examples.py

from dbus.mainloop.glib import DBusGMainLoop
from goecharger import (GoeCharger)
from datetime import datetime, timedelta
import argparse
import signal
import atexit
import sys
import time
import os
import dbus
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '/opt/victronenergy/vrmlogger/ext/velib_python/'))
from vedbus import VeDbusItemImport

# VenusGX Wifi
# GOE_IP='172.24.24.18'
GOE_IP='192.168.0.126'
iGoe = 6

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--battery_offset", help="Solar Battery Offset in Watt", type=int, default=0)
parser.add_argument("-s", "--solar_soc", help="Keep Solar Battery State of Charge in Percent", type=int, default=20)
parser.add_argument("-i", "--goe_ampere", help="Charge with given ampere", type=int, default=0)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

DBusGMainLoop(set_as_default=True)

goeCharger = GoeCharger(GOE_IP)

dbusConn = dbus.SystemBus()

def cleanup(*args):
    if iGoe > 20:
        # Besser fuer die Sicherung:
        print "Stelle Goe auf 15 Ampere ... Warte 10s"
        goeCharger.setMaxCurrent(15)
        time.sleep(10)

    if iGoe > 14:
        # Besser fuer die Sicherung:
        print "Stelle Goe auf 10 Ampere ... Warte 10s"
        goeCharger.setMaxCurrent(10)
        time.sleep(10)

    if iGoe > 10:
        print "Stelle Goe auf 6 Ampere ... Warte 10s"
        goeCharger.setMaxCurrent(6)
        time.sleep(10)

    try:
        GoeCharger(GOE_IP).setAllowCharging(1)
        print "Eingestellt auf Charging 6 Ampere"
    except Exception:
        print "Goe ist nicht erreichbar (1)"

    os._exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
atexit.register(cleanup)

def getBatteryOffsetFromFile():
    f = open("battery_offset")
    offset = int(f.read())
    f.close()
    return offset

def setAmpere(i):
    currentTime = (datetime.now() + timedelta(hours=2)).strftime("%H:%M:%S")
    if i < 6:
        try:
            if 'no vehicle' in goeCharger.requestStatus()['car_status']:
                goeCharger.setAllowCharging(1)
                if args.verbose:
                    print "Kein Auto angesteckt"
            else:
                goeCharger.setAllowCharging(0)
                print "Zu wenig Sonne, stoppe Laden um", currentTime
        except Exception:
            print "Goe ist nicht erreichbar!"
            return False
    else:
        try:
            goeCharger.setAllowCharging(1)
            status = goeCharger.setMaxCurrent(i)
            print i, "Ampere erfolgreich gesetzt um", currentTime
            return True
        except Exception:
            print "Nicht gesetzt!", i
            return False

iGoe_old = 0

while True:
    batteryOffset = args.battery_offset
    solarPower = VeDbusItemImport(dbusConn, 'com.victronenergy.system', '/Ac/PvOnGrid/L1/Power').get_value()
    if solarPower == None:
        solarPower = 0
    solarPower = int(solarPower)

    battery_soc = VeDbusItemImport(dbusConn, 'com.victronenergy.battery.ttyO2', '/Soc').get_value()

    batteryOffset += getBatteryOffsetFromFile()

    if args.goe_ampere > 0:
        iGoe = args.goe_ampere
    else:
        iGoe = (batteryOffset+solarPower)/230

    if iGoe < 6 and solarPower > 1200:
        iGoe = 6

    if args.verbose:
        print "PV=%iW: Bat Offset=%iW iGow=%iA SOC=%.2f%%" % (solarPower,batteryOffset,iGoe,battery_soc)

    if iGoe != iGoe_old:
        if setAmpere(iGoe):
            iGoe_old = iGoe

    if battery_soc != None and battery_soc < args.solar_soc:
        if args.verbose:
            print "Batterie bei weniger als", args.solar_soc, "%, stoppe Ladung"
        batteryOffset = -1000
        args.goe_ampere = 0
    else:
        BatteryHighModeOutPercent = 85
        if battery_soc != None and batteryOffset != args.battery_offset and battery_soc > args.solar_soc+20 and battery_soc < BatteryHighModeOutPercent:
            if args.verbose:
                print "Batterie bei mehr als", args.solar_soc+20, "%, restauriere alten Battery Offset"
            batteryOffset = args.battery_offset

        if battery_soc != None and battery_soc > 96:
            if args.verbose:
                print "Batterie bei mehr als 96%, entlade Solarbatterie"
            batteryOffset  = 1500

        if battery_soc != None and batteryOffset != args.battery_offset and battery_soc < BatteryHighModeOutPercent:
            if args.verbose:
                print "Batterie bei weniger als", BatteryHighModeOutPercent, "%, restauriere alten Battery Offset"
	    battery_offset = args.battery_offset

    time.sleep(10)
