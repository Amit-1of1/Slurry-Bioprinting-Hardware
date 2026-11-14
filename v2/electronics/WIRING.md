# Wiring: sensor box to the computer you already use with the printer

There is **no Raspberry Pi** in v2. The Ender 3 is already plugged into a computer
(old laptop or desktop, Windows or Linux). That computer runs OctoPrint and the
watchdog. The sensor box is one more USB cable into the same computer.

```
            USB                         USB
 ENDER 3  <=====>  YOUR COMPUTER  <=====>  SENSOR BOX (Arduino Nano)
 (stock Marlin)    OctoPrint                 |-- HX711 --- bar load cell (under carriage)
                   bioprinter_watchdog.py    |-- D4  end switch on the guide rod
                   webcam (USB)              |-- D5  needle probe wire (plate -> GND)
                                             |-- D6  door reed switch (optional)
                                             |-- D7  UV relay module (optional)
                                             '-- D8  buzzer
```

| From | To (Nano) | Notes |
|---|---|---|
| HX711 VCC / GND | 5V / GND | |
| HX711 DT (DOUT) | D2 | |
| HX711 SCK | D3 | |
| Load cell red / black / white / green | HX711 E+ / E- / A- / A+ | if force reads negative when pushing, swap A+ and A- |
| End switch COM / NO | GND / D4 | lever faces the carriage, clamp on a guide rod |
| Probe wire (crocodile clip on the metal Luer needle hub) | D5 | |
| Copper plate (probe holder) | GND | the slurry is conductive: keep the plate OUTSIDE the dish |
| Door reed switch | D6 and GND | magnet on the door; closed door = LOW |
| Relay module IN / VCC / GND | D7 / 5V / GND | relay switches the UV lamp's low-voltage supply only |
| Active buzzer + / - | D8 / GND | |

Notes
- Ender 3 USB "backpowering": when the printer is off, the computer's USB can power the
  printer board weakly. A small piece of tape over the 5 V pin of the USB plug (printer end) stops it.
- Use a powered USB hub if the laptop has few ports. Cheap 4-port hubs work.
- Put the HX711 inside the sensor box; run the 4 load-cell wires in a twisted bundle
  and tie them to the carriage with slack for the full 85 mm stroke.
- Mains UV lamps: do not switch 230 V with a hobby relay unless you know how to do it safely.
  Use a 5 V or 12 V UV LED strip instead (it is cheaper anyway).
