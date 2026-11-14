"""
Slurry bioprinter v2 - parametric printed parts.

All parts are built in the PUMP-BODY coordinate frame of the original
pump_body_main.STL (translated so its bounding box starts at 0,0,0):
    X = along the pump (0 = motor end / top, 247 = syringe end / bottom)
    Y = depth (0 = mounting face against the printer, 88 = front, syringe side)
    Z = width (0..72)
Building everything in one frame lets check_fit.py test every part against
the original body, the rods and each other. build_all.py exports each part
re-based to its own origin, in a sensible print orientation.

Requires: python 3.9+, numpy, trimesh, manifold3d  (pip install trimesh manifold3d numpy)
Measure YOUR syringe and load cell and edit the PARAMETERS block before printing.
"""
import numpy as np
import trimesh
from trimesh.creation import cylinder, box

# ------------------------------------------------------------------ PARAMETERS
# Measured from the authors' STL files (do not change unless you change the body)
ROD_Y, ROD_Z = 35.69, (9.5, 62.5)      # 6 mm guide rods
LEAD_Y, LEAD_Z = 36.84, 36.0           # M5 lead screw = motor axis
PLG_Y, PLG_Z = 52.2, 36.0              # syringe / plunger axis
MOTOR_HOLES = [(21.34, 20.5), (21.34, 51.5), (52.34, 20.5), (52.34, 51.5)]
MOTOR_PLATE_BOTTOM = 18.5              # underside of the motor plate

# Things YOU should measure
FLANGE_D = 24.0      # plunger thumb-flange diameter of your glass syringe
FLANGE_T = 4.0       # its thickness
PLUNGER_ROD_D = 10.0 # plunger rod diameter just below the flange
CELL_L, CELL_W = 80.0, 12.7            # bar load cell (10 kg, 80 x 12.7 x 12.7)
CELL_HOLE_PITCH = 15.0                 # 2 holes per end, 15 mm apart
CELL_HOLE_FROM_END = 6.5               # centre of first hole from cell end (made as +-2.5 mm slots)
COUPLER_L = 25.0                       # 5-5 mm rigid coupler length
CLEAR = 0.2                            # general print clearance

CARR_H = 30.0                          # carriage height along X
# ------------------------------------------------------------------ helpers
def bx(x0, x1, y0, y1, z0, z1):
    b = box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b

def cyl_x(d, x0, x1, y, z, sec=64):
    c = cylinder(radius=d / 2, height=x1 - x0, sections=sec)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation([(x0 + x1) / 2, y, z]); return c

def cyl_z(d, z0, z1, x, y, sec=64):
    c = cylinder(radius=d / 2, height=z1 - z0, sections=sec); c.apply_translation([x, y, (z0 + z1) / 2]); return c

def cyl_y(d, y0, y1, x, z, sec=64):
    c = cylinder(radius=d / 2, height=y1 - y0, sections=sec)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    c.apply_translation([x, (y0 + y1) / 2, z]); return c

def hex_x(af, x0, x1, y, z, rot=0.0):
    """hex prism along X; af = across flats; rot=0 -> flats face +-Z"""
    r = af / np.sqrt(3)
    c = cylinder(radius=r, height=x1 - x0, sections=6)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rot), [1, 0, 0]))
    c.apply_translation([(x0 + x1) / 2, y, z]); return c

def U(*ms): return trimesh.boolean.union(list(ms))
def D(a, *bs):
    for b in bs: a = a.difference(b)
    return a

def slot_x(d, x0, x1, y, z0, z1):
    """slot along Z for a hole running along X"""
    return U(cyl_x(d, x0, x1, y, z0), cyl_x(d, x0, x1, y, z1), bx(x0, x1, y - d / 2, y + d / 2, z0, z1))

def load_body():
    import os
    p = os.path.join(os.path.dirname(__file__), '..', '..', 'STLs', 'pump_body_main.STL')
    m = trimesh.load(p); m.apply_translation(-m.bounds[0]); return m

# ------------------------------------------------------------------ 1. thrust bracket
def thrust_bracket(body=None):
    """Takes the plunger push load off the motor bearings.
    Bolts under the motor plate with the 4 motor screws (M3 x 30).
    Holds a 625ZZ ball bearing (5x16x5). Two locked M5 nuts on the lead screw sit on it."""
    x0 = MOTOR_PLATE_BOTTOM + CLEAR
    x_cpl_end = 22 - COUPLER_L / 2 + COUPLER_L      # shaft tip ~x22, coupler centred on joint
    x_nut_end = x_cpl_end + 0.5 + 8.0               # two M5 nuts
    x_brg0 = x_nut_end + 1.0                         # washer
    x_brg1 = x_brg0 + 5.2
    x1 = x_brg1 + 3.0
    cy, cz = LEAD_Y, LEAD_Z
    b = bx(x0, x1, cy - 21, cy + 21, cz - 21, cz + 21)
    cut = [cyl_x(21.5, x0 - 1, x_brg0, cy, cz),                # coupler + nuts
           cyl_x(16.2, x_brg0 - 0.01, x_brg1, cy, cz),          # 625ZZ pocket
           cyl_x(7.0, x_brg1 - 0.01, x1 + 1, cy, cz),           # lead screw
           bx(x0 + 2, x_brg0 - 1, cy, cy + 22, cz - 6, cz + 6)] # window to reach coupler grub screws
    for y, z in MOTOR_HOLES:
        cut += [cyl_x(3.4, x0 - 1, x1 + 1, y, z, 24), cyl_x(6.4, x0 + 7.5, x1 + 1, y, z, 24)]
    b = D(b, *cut)
    if body is not None:                                   # conform to the printed body
        b = b.difference(body)
    return b

THRUST_BRACKET_BOTTOM = None
def bracket_bottom():
    x_cpl_end = 22 - COUPLER_L / 2 + COUPLER_L
    return x_cpl_end + 0.5 + 8.0 + 1.0 + 5.2 + 3.0

# ------------------------------------------------------------------ 2. carriage v2
def carriage_v2(x0=80.0):
    """Rides both guide rods on LM6UU bearings (or printed bushings),
    carries the fixed M5 nut + a spring-loaded second nut (no separate keeper),
    and holds the fixed end of the bar load cell. Top face at x0."""
    H = CARR_H; x1 = x0 + H
    parts = [cyl_x(19, x0, x1, ROD_Y, z) for z in ROD_Z]
    parts.append(bx(x0, x1, 27.0, 45.0, ROD_Z[0], ROD_Z[1]))                  # web
    cz_hi = PLG_Z + CELL_L / 2
    parts.append(bx(x0, x1, PLG_Y - CELL_W / 2 - 1, PLG_Y + CELL_W / 2 + 1,
                    cz_hi - 2 * CELL_HOLE_PITCH - 3, min(cz_hi, 72.0)))       # load-cell pad
    parts.append(bx(x0, x1, 40, PLG_Y - CELL_W / 2, 50, 70))                  # tie pad to web
    c = U(*parts)
    cut = []
    for z in ROD_Z:
        cut += [cyl_x(7.5, x0 - 1, x1 + 1, ROD_Y, z), cyl_x(12.15, x1 - 19.5, x1 + 1, ROD_Y, z)]
    # drive nut 1: trapped, inserted from the back
    n0, n1 = x0 + 3.0, x0 + 7.4
    cut += [cyl_x(6.0, x0 - 1, x1 + 1, LEAD_Y, LEAD_Z),
            hex_x(8.3, n0, n1, LEAD_Y, LEAD_Z, rot=0),
            bx(n0, n1, 20, LEAD_Y, LEAD_Z - 8.3 / 2, LEAD_Z + 8.3 / 2)]
    # spring + nut 2 channel (rotated 30 deg so nut 1 cannot drop in), open at the bottom
    cut.append(hex_x(8.6, n1 - 0.01, x1 + 1, LEAD_Y, LEAD_Z, rot=30))
    # load cell fixed-end bolts (M5), heads from the top in counterbores
    for k in range(2):
        zc = cz_hi - CELL_HOLE_FROM_END - k * CELL_HOLE_PITCH
        cut += [slot_x(5.4, x0 - 1, x1 + 1, PLG_Y, zc - 2.5, zc + 2.5),
                slot_x(9.5, x0 - 1, x1 - 8, PLG_Y, zc - 2.5, zc + 2.5)]
    return D(c, *cut)

def cell_x(x0): return x0 + CARR_H                     # top face of load cell
def load_cell_dummy(x0=80.0):
    xc = cell_x(x0)
    return bx(xc, xc + CELL_W, PLG_Y - CELL_W / 2, PLG_Y + CELL_W / 2, PLG_Z - CELL_L / 2, PLG_Z + CELL_L / 2)

# ------------------------------------------------------------------ 3. plunger cup
def plunger_cup(x0=80.0):
    """Hangs from the free end of the load cell and grips the plunger flange on
    BOTH faces, so the pump can push and pull back (retract)."""
    xc = cell_x(x0) + CELL_W                     # underside of the load cell
    z_lo = PLG_Z - CELL_L / 2                    # free end of the cell
    pad_z1 = z_lo + CELL_HOLE_FROM_END + CELL_HOLE_PITCH + 6
    roof0 = xc + 1.5; slot0 = roof0 + 3.0; slot1 = slot0 + FLANGE_T + 0.6; lip1 = slot1 + 3.5
    y0, y1 = 41.5, PLG_Y + FLANGE_D / 2 + 4
    z1 = PLG_Z + FLANGE_D / 2 + 5
    c = U(bx(roof0, lip1, y0, y1, z_lo, z1),
          bx(xc, roof0 + 0.01, PLG_Y - CELL_W / 2, PLG_Y + CELL_W / 2, z_lo, pad_z1))   # contact pad
    cut = [U(cyl_x(FLANGE_D + 1, slot0, slot1, PLG_Y, PLG_Z), bx(slot0, slot1, PLG_Y, y1 + 1, PLG_Z - (FLANGE_D + 1) / 2, PLG_Z + (FLANGE_D + 1) / 2)),
           U(cyl_x(PLUNGER_ROD_D + 1, slot1 - 0.01, lip1 + 1, PLG_Y, PLG_Z), bx(slot1 - 0.01, lip1 + 1, PLG_Y, y1 + 1, PLG_Z - (PLUNGER_ROD_D + 1) / 2, PLG_Z + (PLUNGER_ROD_D + 1) / 2))]
    for k in range(2):
        zc = z_lo + CELL_HOLE_FROM_END + k * CELL_HOLE_PITCH
        cut += [slot_x(4.4, xc - 1, lip1 + 1, PLG_Y, zc - 2.5, zc + 2.5),
                slot_x(7.8, slot0, lip1 + 1, PLG_Y, zc - 2.5, zc + 2.5)]
    return D(c, *cut)

# ------------------------------------------------------------------ 4. printed bushing (LM6UU size)
def bushing_6mm():
    b = D(cyl_z(12.0, 0, 19, 0, 0), cyl_z(6.25, -1, 20, 0, 0, 48))
    for a in range(3):   # oil grooves, less friction
        g = bx(-0.8, 0.8, 2.6, 3.6, -1, 20); g.apply_transform(trimesh.transformations.rotation_matrix(a * 2 * np.pi / 3, [0, 0, 1])); b = b.difference(g)
    return b

# ------------------------------------------------------------------ 5. thumb knob (replaces a bought M5 knob)
def thumb_knob_m5():
    k = cyl_z(24, 0, 10, 0, 0, 96)
    for a in range(12):
        n = cyl_z(3.2, -1, 11, 12.6, 0, 16); n.apply_transform(trimesh.transformations.rotation_matrix(a * np.pi / 6, [0, 0, 1])); k = k.difference(n)
    hexp = cylinder(radius=8.2 / np.sqrt(3), height=4.6, sections=6); hexp.apply_translation([0, 0, 10 - 2.3 + 0.01])
    return D(k, cyl_z(5.3, -1, 11, 0, 0, 32), hexp)

# ------------------------------------------------------------------ 6. syringe-empty switch clamp
def endstop_clamp():
    """Clamps on a 6 mm guide rod at any height; holds a KW12 micro switch
    (holes 2.3 mm, 9.5 mm apart) with its lever facing the carriage."""
    ring = D(cyl_z(15, 0, 10, 0, 0), cyl_z(6.2, -1, 11, 0, 0, 48), bx(-1, 1, 0, 9, -1, 11))
    ears = D(bx(-5, 5, 6, 13, 0, 10), bx(-1, 1, 0, 14, -1, 11), cyl_x(3.4, -6, 6, 10, 5, 24))
    arm = bx(-1.5, 1.5, -24, -6, 0, 10)
    plate = bx(-1.5, 1.5, -40, -20, 0, 10)
    m = U(ring, ears, arm, plate)
    for y in (-35.0, -25.5):
        m = m.difference(cyl_x(2.1, -3, 3, y, 5, 24))
    return m

# ------------------------------------------------------------------ 7. needle probe plate holder
def probe_holder():
    """Holds a 30 x 40 mm piece of copper-clad PCB board (cheap probe plate)."""
    t = bx(0, 50, 0, 40, 0, 4)
    return D(t, bx(4.75, 45.25, 4.75, 35.25, 2.3, 5), cyl_z(3.4, -1, 5, 2.4, 20), bx(0.8, 4, 17, 23, 3, 5))

# ------------------------------------------------------------------ 8/9. dish ring and 4-dish bed plate
def dish_ring(id_=91.2, wall=5.0, h=6.0):
    r = D(cyl_z(id_ + 2 * wall, 0, h, 0, 0, 160), cyl_z(id_, -1, h + 1, 0, 0, 160))
    for a in range(4):
        n = bx(id_ / 2 + wall - 1.5, id_ / 2 + wall + 1, -1, 1, -1, h + 1)
        n.apply_transform(trimesh.transformations.rotation_matrix(a * np.pi / 2, [0, 0, 1])); r = r.difference(n)
    return r

def bed_plate_4dish():
    """Four dish rings tied together, fits the 220 x 220 mm Ender 3 print area."""
    rings = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = dish_ring(wall=3.0, h=5.0); r.apply_translation([sx * 55, sy * 55, 0]); rings.append(r)
    bars = [bx(-110, 110, -3, 3, 0, 2), bx(-3, 3, -110, 110, 0, 2), bx(-110, 110, 52, 58, 0, 2), bx(-110, 110, -58, -52, 0, 2),
            bx(52, 58, -110, 110, 0, 2), bx(-58, -52, -110, 110, 0, 2)]
    m = U(*rings, *bars)
    # keep the dish floor area open (dishes sit on the bed)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = m.difference(cyl_z(91.2, -1, 7, sx * 55, sy * 55, 160))
    return m

# ------------------------------------------------------------------ 10. webcam clip for 2020 extrusion
def webcam_clip_2020():
    c = D(bx(0, 26, 0, 20, 0, 26), bx(3, 23.4, -1, 21, 3, 23.4 + 10))
    lips = [bx(3, 6.9, 0, 20, 23.4, 26), bx(19.5, 23.4, 0, 20, 23.4, 26)]
    arm = bx(-60, 0, 0, 20, 0, 4)
    m = U(c, *lips, arm)
    return m.difference(cyl_z(6.4, -1, 5, -50, 10, 32))   # 1/4-inch camera screw

# ------------------------------------------------------------------ 11. sensor box (Arduino Nano + HX711)
def sensor_box():
    L, Wd, Ht, t = 86.0, 60.0, 32.0, 2.4
    b = D(bx(0, L, 0, Wd, 0, Ht), bx(t, L - t, t, Wd - t, t, Ht + 1))
    for (x, y) in [(5, 5), (L - 5, 5), (5, Wd - 5), (L - 5, Wd - 5)]:
        b = U(b, D(cyl_z(7, 0, Ht, x, y, 32), cyl_z(2.6, 3, Ht + 1, x, y, 24)))
    b = D(b, bx(-1, t + 1, 22, 34, 6, 14))                  # USB to the computer
    for i, y in enumerate((10, 22, 34, 46)):               # 4 cable holes: load cell, end switch, probe, door/relay
        b = b.difference(cyl_x(5.0, L - t - 1, L + 1, y + 2, Ht - 10, 24))
    return b

def sensor_box_lid():
    L, Wd = 86.0, 60.0
    lid = bx(0, L, 0, Wd, 0, 2.4)
    for (x, y) in [(5, 5), (L - 5, 5), (5, Wd - 5), (L - 5, Wd - 5)]:
        lid = lid.difference(cyl_z(3.4, -1, 3, x, y, 24))
    return lid
