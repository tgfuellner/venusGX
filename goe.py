#!/usr/bin/python

from goecharger import (GoeCharger)

status = GoeCharger('192.168.0.126').requestStatus()
print("gerade geladen %.2f    gesamt %.2f" % (status['current_session_charged_energy'], status['energy_total']))
