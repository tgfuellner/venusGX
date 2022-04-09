#!/usr/bin/python

import sys
from datetime import datetime
from goecharger import (GoeCharger)

now = datetime.now()

goeCharger = GoeCharger('192.168.0.126')

status = goeCharger.requestStatus()
print("%s gerade geladen %.2fkWh    gesamt %.2fkWh mit %sA" % (now.strftime("%H:%M"), status['current_session_charged_energy'], status['energy_total'], status['charger_max_current']))

if len(sys.argv) == 2:
    current = int(sys.argv[-1])
    if current == 0:
        goeCharger.setAllowCharging(0)
        print("  Pausiere den Ladevorgang")
    else:
        goeCharger.setAllowCharging(1)
        status = goeCharger.setMaxCurrent(current)
        print("  %sA gesetzt, charger Temp=%sC" % (status['charger_max_current'], status['charger_temp']))
