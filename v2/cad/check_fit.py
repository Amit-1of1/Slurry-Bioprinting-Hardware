"""Collision check: v2 parts vs the original pump body, rods, lead screw and each other.
Run: python check_fit.py   (prints overlap volumes; anything > 1 mm^3 needs a look)"""
import numpy as np
from parts_v2 import *

def vol(a, b):
    try:
        i = a.intersection(b); return 0.0 if i.is_empty else abs(i.volume)
    except Exception: return float('nan')

body = load_body()
print('body bounds', np.round(body.bounds, 2))
rods = U(*[cyl_x(6.0, 0, 205, ROD_Y, z) for z in ROD_Z])
lead = cyl_x(5.0, 22, 200, LEAD_Y, LEAD_Z)
tb = thrust_bracket(body)
print('thrust bracket: vs body %.2f  vs rods %.2f  vs lead %.2f' % (vol(tb, body), vol(tb, rods), vol(tb, lead)))
xb = bracket_bottom()
# find how far down the carriage+cup assembly can travel before hitting the body
results = []
for x0 in np.arange(xb + 0.5, 200, 5.0):
    c = carriage_v2(x0); cell = load_cell_dummy(x0); cup = plunger_cup(x0)
    r = dict(x0=x0, carr_body=vol(c, body), carr_rods=vol(c, rods), carr_lead=vol(c, lead),
             cell_body=vol(cell, body), cup_body=vol(cup, body), cup_lead=vol(cup, lead),
             cup_cell=vol(cup, cell), carr_cell=vol(c, cell), carr_tb=vol(c, tb))
    results.append(r)
    bad = {k: round(v, 1) for k, v in r.items() if k != 'x0' and v > 1.0}
    print('x0=%6.1f %s' % (x0, bad if bad else 'OK'))
ok = [r['x0'] for r in results if all(v <= 1.0 for k, v in r.items() if k != 'x0')]
if ok:
    print('collision-free carriage top positions: %.1f .. %.1f  -> stroke about %.0f mm' % (min(ok), max(ok), max(ok) - min(ok)))
