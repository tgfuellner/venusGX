#!/usr/bin/env python3

import dbus
import time


# === CONFIG ===

# refresh delay in seconds between each DBus querying
# _RefreshSleep = 0.5 # 500ms
_RefreshSleep = 30.0


# === =========================== ===
# === NO CHANGES AFTER THIS POINT ===
# === =========================== ===


def dbus_getvalue(bus, service, object_path):
    object = bus.get_object(service, object_path)
    return object.GetValue()


def dbus_setvalue(bus, service, object_path, value):
    object = bus.get_object(service, object_path)
    object.SetValue(value)


# === MAIN ===
bus = dbus.SystemBus()


# step through config services
while True:
    try:
        vbat = dbus_getvalue(bus, "com.victronenergy.system", "/Dc/Battery/Voltage")

        if vbat < 54.0: newPower = 4000
        elif vbat < 54.2: newPower = 2500
        elif vbat < 54.4: newPower = 1500
        elif vbat < 54.6: newPower = 1000
        else:
            newPower = 500

        chargePower = dbus_getvalue(
            bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxChargePower"
        )

        if newPower != chargePower:
            dbus_setvalue(
                bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxChargePower", newPower
            )
            print(time.asctime(), "Setting ChargePower:", newPower, "vBat:", vbat)


        time.sleep(_RefreshSleep)

    except Exception as e:
        print(e)
