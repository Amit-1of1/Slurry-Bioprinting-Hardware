# Build guide (v2): from nothing to a first print

Work through the phases **in order**. Every phase ends with a **CHECK**.
Do not start the next phase until the check passes. Each phase can be done in one evening.

```
0 Source parts -> 1 Print parts -> 2 Sub-assemblies -> 3 Pump -> 4 Prepare printer
 -> 5 Mount pump -> 6 Electronics -> 7 Software -> 8 Calibrate -> 9 First print
```
Level 0 (a working pump, no sensors) = phases 0 to 5, 7, 8, 9 (skip 6).
Level 1 (sensors + auto-pause + needle probe) = all phases.

---

## Phase 0. Source the parts (1 to 2 weeks)
Use [BOM_INDIA.md](BOM_INDIA.md). Buy the printer first: everything else is cheap.
- Do the used-printer checklist with the seller.
- Order online parts in one cart (Robu or Robocraze) to save shipping.
- Hardware-shop list: M5 rod 170 mm, 4 × M5 nuts, 4 × M3×30, 2 × M5×12, 2 × M4×25 + nuts, 3 × M5 bolts + nylocks, a small spring.

**CHECK:** lay everything out on a table and tick each line of the BOM. Measure your glass syringe:
flange diameter, flange thickness, plunger rod diameter. Write the numbers down.

## Phase 1. Print the parts (1 to 2 days of printing)
1. If your syringe numbers differ from `FLANGE_D = 24`, `FLANGE_T = 4`, `PLUNGER_ROD_D = 10`,
   edit them in `cad/parts_v2.py` and run `python cad/build_all.py` (needs `pip install trimesh manifold3d numpy matplotlib`).
   If you cannot run Python, print as is and test-fit (step 3 below).
2. Print the original body `STLs/pump_body_main.STL` (PETG, 40% infill, 4 walls, supports on build plate only).
3. Print `stl/03_plunger_cup.stl` FIRST (15 minutes). Slide your syringe flange in. It should slide in with light force and not rattle. If not, change FLANGE_* and reprint.
4. Print the rest, in this order: 01, 02, then 04 to 12 as needed. Settings are in [stl/PRINT_LIST.md](stl/PRINT_LIST.md).
   Orientation is already correct in the files: do not rotate them.

**CHECK:** a 6 mm rod slides through the carriage's rod holes; an M5 nut drops into the side slot of the carriage;
the 625ZZ bearing presses into the thrust bracket with thumb pressure.

## Phase 2. Sub-assemblies (1 hour)
**2a. Carriage** (`02_carriage_v2`)
1. Press the 2 LM6UU bearings (or printed bushings) into the round pockets from the bottom.
2. Push drive nut 1 into the side slot until it lines up with the centre hole.
3. Drop the spring, then nut 2, into the hex channel from the bottom.
4. Screw the M5 rod in from the top through nut 1, compress the spring a little, and catch nut 2.
   The spring pushes the two nuts apart: this removes backlash (the "dead zone" when the pump reverses).

**2b. Load cell**
5. Bolt the FIXED end of the load cell (the end with the cable) under the carriage pad with 2 × M5×12. The arrow on the cell points DOWN (towards the syringe).

**2c. Plunger cup**
6. Bolt `03_plunger_cup` to the FREE end of the load cell with 2 × M4×25 and nuts. The cup must not touch the cell anywhere else (there is a 1.5 mm gap: check with paper).

**CHECK:** turn the rod by hand: the carriage moves smoothly with no click when you reverse direction.

## Phase 3. Pump assembly (1 hour)
1. Push the two 6 mm rods into the body.
2. Slide the carriage assembly onto the rods.
3. **Thrust bracket:** on the lead screw, thread 2 × M5 nuts, then the 625ZZ bearing (in the bracket). Tighten the two nuts against each other (lock them) touching the bearing.
4. Put the 5-5 coupler on the motor shaft. Put the motor on top of the body, the bracket under the motor plate, and push the lead screw into the coupler.
5. Fix motor + bracket with 4 × M3×30 through the bracket. Tighten the coupler grub screws through the bracket's side window.
6. Thread the printed knob + M5 nut on the bottom end of the rod (manual jog).

**CHECK:** turn the knob: the carriage goes the full 85 mm without binding. Push hard on the cup with your thumb:
the lead screw must NOT move up and down (the bearing takes the load, not the motor).

## Phase 4. Prepare the printer (30 minutes)
1. Power off and unplug. Take a photo of the hotend wiring first.
2. Remove the hotend (heater block, fan shroud). **Leave the thermistor plugged in**: Marlin stops with "MINTEMP" without it. Tape it out of the way.
3. Unplug the extruder motor cable at the motor (the pump motor will use this cable). If you are reusing the extruder motor for the pump, remove it and its gear now.
4. Remove the Bowden tube and extruder lever.

**CHECK:** power on. The screen shows room temperature for the hotend (no error). Homing still works.

## Phase 5. Mount the pump (30 minutes)
1. Hold the pump body against the Ender's X carriage plate with the syringe pointing down.
   The mount tab has three 5.3 mm holes; line them up with the carriage plate holes/wheel bolts (see the v1 guide note N6: this is not documented by the authors, so check yours).
2. Use M5 bolts with nylock nuts. Measure the stack (tab 6 mm + plate + spacer) and buy bolts 5 mm longer.
3. Plug the extruder cable into the pump motor.
4. Tie the cable to the frame with slack for full X and Z travel.

**CHECK:** home X, Y, Z from the screen. Nothing hits the frame. Move Z to the top: the syringe clears the gantry.
Then send `M302 P1` (allow cold extrusion) and `G1 E1 F60`: the carriage moves DOWN about 1 mm. If it goes up, swap the two wires of ONE coil in the motor cable (for example pins 1 and 2 at the motor end). This is free and needs no firmware change.

## Phase 6. Electronics (1 to 2 hours, Level 1 only)
Follow [electronics/WIRING.md](electronics/WIRING.md).
1. Solder or plug the HX711 to the Nano (D2, D3), mount both in `11_sensor_box`.
2. Install the Arduino IDE on your printer computer, add library "HX711 Arduino Library" (Bogdan Necula), open `electronics/sensor_box/sensor_box.ino`, choose Board "Arduino Nano", Processor "ATmega328P (Old Bootloader)" for most clones, upload.
3. Clamp `06_endstop_clamp` on a guide rod so the switch is pressed when the plunger is 1 mm from the bottom of the syringe.
4. Put a copper-clad PCB piece in `07_probe_holder`, solder a wire to it, wire to GND. Crocodile clip on the needle hub to D5.

**CHECK:** open the Serial Monitor at 115200. You see `S,...` lines. Press the end switch: the 4th number becomes 1.
Touch the needle to the plate: the 5th number becomes 1. Push the cup with your finger: the force number rises.

## Phase 7. Software on your computer (1 hour)
1. Install OctoPrint:
   - Windows: the OctoPrint Windows installer (by jneilliii), linked from https://octoprint.org/download/
   - Linux: `python3 -m venv op && op/bin/pip install octoprint && op/bin/octoprint serve`
2. Open http://localhost:5000, connect to the printer's port at 115200. In Settings > API create an API key.
3. `pip install pyserial requests`, copy `electronics/watchdog/watchdog.ini` to `watchdog_local.ini`, paste the key, set the Nano's port.
   (Both the printer and the Nano can show as "CH340". If so, unplug the Nano, note the printer's port, plug it back: the new port is the Nano.)
4. Run `python bioprinter_watchdog.py monitor`.

**CHECK:** the readings print in the terminal, and OctoPrint shows the printer as "Operational".
If you only use Pronterface/Repetier and not OctoPrint: the sensor box still beeps and logs, but the watchdog cannot pause the print, because only one program can own the printer's port.

## Phase 8. Calibrate (1 to 2 hours)
1. **Load cell:** with nothing touching the cup, `python bioprinter_watchdog.py tare`. Then hang a known weight (a 500 g packet of something, weighed on a kitchen scale) from the cup and run `calibrate 500`.
2. **Volume (E steps), by weighing water:** fill a plastic syringe with water, put a cup on a kitchen scale (0.01 g type, approx. ₹300), send `M83`, `G1 E10 F60`. Weigh. 1 g of water = 1 mL. With M92 E3720, `G1 E10` moves the plunger about 9.3 mm (an M5 rod at 1/16 microstepping is 4000 steps per mm); work out your syringe's mL per mm (barrel area) and correct the value. The supplied G-code files set `M92 E3720` at the start, so change that line in each file (or remove it and use `M92 E<new>` + `M500`). Repeat 3 times.
3. **Needle Z zero:** put the probe holder on the bed, glass syringe with metal needle loaded, `python bioprinter_watchdog.py probe`. The script lowers Z until the needle touches the plate and sets Z.
4. **Clog limit:** print a short test line in the slurry, look at the log in `watchdog/logs/`. Set `clog_limit_g` to about 2 × the normal printing force.

**CHECK:** three water dispenses of 1.00 mL weigh 1.00 g ± 0.03. The probe stops within 0.1 mm of where a sheet of paper just drags.

## Phase 9. First print
1. Use the no-heat G-code in `gcode/` (heater commands removed, so no waiting for temperature).
2. Put `08_dish_ring_90mm` on the bed, dish inside, run the probe routine on the plate next to the dish (never inside: the slurry is conductive), then lift.
3. Start `python bioprinter_watchdog.py` (watch mode), then start the print from OctoPrint.

**CHECK:** the watchdog shows "Printing" and a steady force. Pinch the needle tubing (or block the needle) on a test print: the print pauses and the box beeps within about 2 seconds.

---

## What changed from the original design and why
| Problem in v1 | v2 fix | Part |
|---|---|---|
| Plunger push load went straight into the motor's bearings | 625ZZ thrust bearing + locked nuts take the load | 01 thrust bracket |
| Backlash when the pump reverses (retraction did little) | spring-loaded second nut built into the carriage | 02 carriage |
| Carriage only pushes; retraction can leave the plunger behind | cup grips the flange on both faces | 03 plunger cup |
| No idea what pressure the slurry needs, or when it clogs | load cell between carriage and plunger | 02 + 03 + sensor box |
| Z height set by eye | needle-touch probe on a copper plate | 07 probe holder + watchdog |
| Running out of slurry goes unnoticed | end switch on the guide rod | 06 endstop clamp |
| Raspberry Pi that connected to nothing | uses the computer already driving the printer, one USB Nano | electronics/ |
| Expensive or imported parts | printed bushings and knob; reused extruder motor; India sources | BOM_INDIA.md |

## Not tested yet
These parts were designed and checked in CAD for fit against the original body (see `cad/check_fit.py`:
no collisions over 85 mm of carriage travel) but have **not been printed or run**.
Measure and adjust before trusting them:
- your syringe flange (FLANGE_D, FLANGE_T, PLUNGER_ROD_D)
- your load cell's hole spacing (CELL_HOLE_PITCH, CELL_HOLE_FROM_END; slots allow ±2.5 mm)
- the coupler length (COUPLER_L)
- the Ender mount bolts (phase 5)
