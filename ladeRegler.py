#!/usr/bin/env python3

import dbus
import time
import sys
import os

# Regelung von MaxChargePower und MaxDischargePower
# In /data/rc.local:
#    nohup /data/home/root/ladeRegler.py >/data/home/root/ladeRegler.log&

# Um den Prozess einfach killen zu können
print(os.getpid())

# === CONFIG ===

# refresh delay in seconds between each DBus querying
# _RefreshSleep = 0.5 # 500ms
_RefreshSleep = 10.0

# Parameter für den PID-Regler
Kp = 1300.0  # Proportionalverstärkung
Ki = 200.0  # Integralverstärkung
Kd = 1 #0.1 # Derivative Verstärkung
print("Kp =",Kp, " Ki =",Ki, " Kd =",Kd)

setpoint = 54.6  # Zielspannung (V)
min_output = 500 # Minimale Ladeleistung (W)
max_output = 4000 # Maximale Ladeleistung (W)
dt = 0.1  # Zeitintervall (s)

# === =========================== ===
# === NO CHANGES AFTER THIS POINT ===
# === =========================== ===

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint, min_output, max_output):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.min_output = min_output
        self.max_output = max_output
        self.previous_error = 0
        self.integral = 0

    def update(self, process_variable, dt):
        error = self.setpoint - process_variable
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        output = max(min(output, self.max_output), self.min_output) # Begrenzung des Ausgangs

        self.previous_error = error
        return output


def dbus_getvalue(bus, service, object_path):
    object = bus.get_object(service, object_path)
    return object.GetValue()


def dbus_setvalue(bus, service, object_path, value):
    object = bus.get_object(service, object_path)
    object.SetValue(value)


# === MAIN ===
bus = dbus.SystemBus()

# Initialisierung des PID-Reglers
pid = PIDController(Kp, Ki, Kd, setpoint, min_output, max_output)

# step through config services
while True:
    try:
        vbat = dbus_getvalue(bus, "com.victronenergy.system", "/Dc/Battery/Voltage")

        newPower = pid.update(vbat, dt)

        chargePower = dbus_getvalue(
            bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxChargePower"
        )
        # print(vbat, newPower, chargePower, abs(newPower - chargePower))

        if abs(newPower - chargePower) > 10:
            dbus_setvalue(
                bus, "com.victronenergy.settings", "/Settings/CGwacs/MaxChargePower", newPower
            )
            print(time.asctime(), f"Setting MaxCharge: {newPower:.1f}W vBat:{vbat:.2f}V")
            sys.stdout.flush()

        soc = dbus_getvalue(bus, "com.victronenergy.system", "/Dc/Battery/Soc")
        if soc > 40:
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
            print(time.asctime(), "Setting MaxDischarge:", newPower, "SOC:", soc)
            sys.stdout.flush()

        time.sleep(_RefreshSleep)

    except Exception as e:
        print(e)
