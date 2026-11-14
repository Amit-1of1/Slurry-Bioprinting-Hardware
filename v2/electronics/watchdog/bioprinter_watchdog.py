#!/usr/bin/env python3
"""
Slurry bioprinter v2 - WATCHDOG
Runs on the computer that is already connected to the Ender 3.
It reads the Arduino sensor box over USB and talks to OctoPrint
(running on the same computer) through its REST API.

    python bioprinter_watchdog.py                 # watch prints, log force, pause on faults
    python bioprinter_watchdog.py tare            # zero the load cell
    python bioprinter_watchdog.py calibrate 500   # calibrate with a 500 g weight
    python bioprinter_watchdog.py probe           # find Z=0 by touching the needle on the plate
    python bioprinter_watchdog.py uv 30           # UV on for 30 s (only if the door is closed)
    python bioprinter_watchdog.py monitor         # just print sensor readings

Needs: pip install pyserial requests
"""
import configparser, csv, os, sys, time
import requests, serial
from serial.tools import list_ports

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
cfg.read([os.path.join(HERE, 'watchdog.ini'), os.path.join(HERE, 'watchdog_local.ini')])


# ----------------------------------------------------------------- sensor box
class SensorBox:
    def __init__(self):
        port = cfg.get('sensor_box', 'port', fallback='auto')
        if port == 'auto':
            port = self.find_port()
        self.ser = serial.Serial(port, cfg.getint('sensor_box', 'baud', fallback=115200), timeout=0.2)
        time.sleep(2.0)                       # Nano resets when the port opens
        self.state = dict(t=0, g=0.0, end=False, probe=False, door=False, uv=False)
        print('sensor box on', port)

    @staticmethod
    def find_port():
        for p in list_ports.comports():
            d = (p.description or '') + (p.manufacturer or '')
            if any(k in d for k in ('CH340', 'CH341', 'USB-SERIAL', 'Arduino', 'FT232')):
                # the Ender 3 board itself also shows as CH340 on some versions:
                # if both appear, set the port by hand in watchdog_local.ini
                return p.device
        raise SystemExit('Sensor box not found. Set [sensor_box] port in watchdog_local.ini')

    def send(self, s):
        self.ser.write((s + '\n').encode())

    def poll(self):
        """read all waiting lines, return the newest state"""
        while True:
            line = self.ser.readline().decode(errors='ignore').strip()
            if not line:
                return self.state
            if line.startswith('S,'):
                p = line.split(',')
                if len(p) == 7:
                    try:
                        self.state = dict(t=int(p[1]), g=float(p[2]), end=p[3] == '1', probe=p[4] == '1',
                                          door=p[5] == '1', uv=p[6] == '1')
                    except ValueError:
                        pass
            else:
                print('[box]', line)


# ----------------------------------------------------------------- OctoPrint
class OctoPrint:
    def __init__(self):
        self.url = cfg.get('octoprint', 'url').rstrip('/')
        self.h = {'X-Api-Key': cfg.get('octoprint', 'api_key')}

    def job_state(self):
        try:
            r = requests.get(self.url + '/api/job', headers=self.h, timeout=3)
            return r.json().get('state', 'Unknown') if r.ok else 'Offline'
        except requests.RequestException:
            return 'Offline'

    def pause(self, why):
        print('PAUSE:', why)
        requests.post(self.url + '/api/job', headers=self.h, json={'command': 'pause', 'action': 'pause'}, timeout=5)
        self.gcode(['M117 PAUSED: ' + why[:20]])

    def gcode(self, cmds):
        requests.post(self.url + '/api/printer/command', headers=self.h, json={'commands': cmds}, timeout=5)

    def z_pos(self):
        r = requests.get(self.url + '/api/printer', headers=self.h, timeout=3)
        return r.json()


# ----------------------------------------------------------------- modes
def watch(box, op):
    lim = cfg.getfloat('rules', 'clog_limit_g'); t_clog = cfg.getfloat('rules', 'clog_seconds')
    low = cfg.getfloat('rules', 'min_print_g'); t_low = cfg.getfloat('rules', 'empty_seconds')
    os.makedirs(os.path.join(HERE, cfg.get('log', 'folder')), exist_ok=True)
    fn = os.path.join(HERE, cfg.get('log', 'folder'), time.strftime('force_%Y%m%d_%H%M%S.csv'))
    f = open(fn, 'w', newline=''); w = csv.writer(f); w.writerow(['time_s', 'force_g', 'end', 'probe', 'door', 'uv', 'job'])
    print('logging to', fn, ' (Ctrl+C to stop)')
    hi_since = lo_since = None; job = 'Unknown'; last_job = 0; t0 = time.time(); paused_for = None
    while True:
        s = box.poll(); now = time.time()
        if now - last_job > 1.0:
            job = op.job_state(); last_job = now
        printing = job.startswith('Printing')
        if not printing:
            paused_for = None
        w.writerow(['%.2f' % (now - t0), s['g'], int(s['end']), int(s['probe']), int(s['door']), int(s['uv']), job])
        if printing and paused_for is None:
            hi_since = (hi_since or now) if s['g'] > lim else None
            lo_since = (lo_since or now) if s['g'] < low else None
            why = None
            if hi_since and now - hi_since > t_clog:
                why = 'clog %.0f g' % s['g']
            elif lo_since and now - lo_since > t_low:
                why = 'no pressure (empty/air?)'
            elif s['end'] and cfg.getboolean('rules', 'pause_on_end_switch'):
                why = 'syringe empty'
            elif not s['door'] and cfg.getboolean('rules', 'pause_on_door_open'):
                why = 'door open'
            if why:
                op.pause(why); box.send('B'); paused_for = why
        sys.stdout.write('\r%-12s force %7.1f g  end:%d probe:%d door:%d uv:%d   ' %
                         (job[:12], s['g'], s['end'], s['probe'], s['door'], s['uv'])); sys.stdout.flush()
        time.sleep(0.1)


def probe(box, op):
    """Lower the nozzle in steps until the needle touches the copper plate, then set Z."""
    if op.job_state().startswith('Printing'):
        raise SystemExit('Printer is busy')
    thick = cfg.getfloat('probe', 'plate_thickness_mm'); maxd = cfg.getfloat('probe', 'max_travel_mm')
    print('Put the probe plate under the needle. Needle must be metal and clean. Starting in 3 s...')
    time.sleep(3)
    if box.poll()['probe']:
        raise SystemExit('Probe already reads "touching": check wiring, wipe the needle')
    op.gcode(['G91'])
    for step in (cfg.getfloat('probe', 'coarse_step_mm'), cfg.getfloat('probe', 'fine_step_mm')):
        moved = 0.0
        while moved < maxd:
            op.gcode(['G1 Z-%.3f F120' % step, 'M400']); time.sleep(0.35 + step)
            moved += step
            if box.poll()['probe']:
                break
        else:
            op.gcode(['G90']); raise SystemExit('No contact within %.0f mm, stopped' % maxd)
        if step != cfg.getfloat('probe', 'fine_step_mm'):
            op.gcode(['G1 Z1 F300', 'M400']); time.sleep(1.5)      # back off, then approach slowly
    op.gcode(['G90', 'G92 Z%.3f' % thick, 'G1 Z%.3f F300' % (thick + 5), 'M117 Z set by needle probe'])
    box.send('B'); print('Contact. Z set to the plate thickness (%.2f mm) and lifted 5 mm.' % thick)


def uv(box, seconds):
    box.send('U1'); t_end = time.time() + seconds
    while time.time() < t_end:
        s = box.poll()
        if not s['door']:
            print('door opened, UV off'); break
        time.sleep(0.2)
    box.send('U0'); print('UV off')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'watch'
    box = SensorBox()
    if mode == 'tare':
        box.send('T'); time.sleep(3); box.poll()
    elif mode == 'calibrate':
        g = float(sys.argv[2]); input('Tare done? Put %.0f g on the cup and press Enter' % g)
        box.send('C%.1f' % g); time.sleep(3); box.poll()
    elif mode == 'monitor':
        while True:
            print(box.poll()); time.sleep(0.5)
    elif mode == 'uv':
        uv(box, float(sys.argv[2]))
    elif mode == 'probe':
        probe(box, OctoPrint())
    else:
        watch(box, OctoPrint())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nstopped')
