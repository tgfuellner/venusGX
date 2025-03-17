#!/usr/bin/env python3

import dbus
import time


# === CONFIG ===

# refresh delay in seconds between each DBus querying
# _RefreshSleep = 0.5 # 500ms
_RefreshSleep = 20.0


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

        if vbat < 54.4: newPower = 4000
        elif vbat < 54.45: newPower = 3000
        elif vbat < 54.5: newPower = 2500
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

        soc = dbus_getvalue(bus, "com.victronenergy.system", "/Dc/Battery/Soc")
        if soc > 50:
            newPower = 5000
        else:
            newPower = 2500

        dischargePower = dbus_getvalue(
            bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxDischargePower"
        )
        if dischargePower != newPower:
            dbus_setvalue(
                bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxDischargePower", newPower
            )
            print(time.asctime(), "Setting DischargePower:", newPower, "SOC:", soc)

        time.sleep(_RefreshSleep)

    except Exception as e:
        print(e)
