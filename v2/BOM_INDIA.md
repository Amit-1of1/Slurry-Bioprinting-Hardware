# Bill of materials: India (v2)

Prices are in INR and were checked on 14 Nov 2026 where a link is given.
Lines marked **approx.** are typical Indian online prices, not checked live:
check before you buy. Prices change and stock runs out, so search by the
part name in the "What to search for" column.

Shops that ship all over India: Robu.in, Robocraze, ElectronicsComp, Zbotic,
Probots, Indian Hobby Center, ThinkRobotics, Amazon.in, Flipkart, IndiaMART
(bulk / lab supplies). For nuts and bolts, any local hardware shop
(Lamington Road Mumbai, SP Road Bengaluru, Lajpat Rai Market / Nehru Place Delhi,
Ritchie Street Chennai, Chandni Chowk Kolkata) is cheaper than online.

## A. The printer (the biggest cost: buy it used)

| Item | New | Used / cheap route | Notes |
|---|---|---|---|
| Creality Ender 3 (or Ender 3 V2 / Pro / any clone with a 2020 frame and USB) | about ₹18,400 (Robocraze, often sold out) | **₹6,000 to ₹18,000 on OLX / Facebook Marketplace / Quikr** (most listings ₹10k to 16k) | The hotend is removed, so a printer with a dead hotend or a worn nozzle is fine. Check: all 3 axes move, the bed moves smoothly, USB connects. A broken screen does not matter, the computer drives it. |
| Computer | you already have one | any old laptop / desktop, Windows 10/11 or Linux, 4 GB RAM | runs OctoPrint + the watchdog. Used office PCs on OLX: ₹5,000 to 8,000 |

**Used-printer checklist (take this to the seller):**
1. Power on, home all axes (Prepare > Auto home). Every axis must move and stop at its switch.
2. Move X, Y and Z by hand from the menu 10 mm each; no grinding, no skipped steps.
3. Plug in a laptop by USB; it must show a new COM port (Windows) or /dev/ttyUSB0 (Linux).
4. Bed must not wobble (tighten the eccentric nuts if it does; free fix).
5. Hotend, heated bed and screen are NOT needed for bioprinting. Use them to bargain.

## B. Syringe pump (bought parts)

| Qty | Item | What to search for | Price (₹) | Source / used route |
|---|---|---|---|---|
| 1 | NEMA17 stepper, 5 mm shaft, 1.7 to 4 kg-cm | "NEMA17 42HS40" | 763 (42HS40-0406) | [Robu](https://robu.in/). **Used: take the extruder motor off the Ender 3**, since the hotend is removed (free). Or any NEMA17 from a dead 3D printer / scrap CNC on OLX. |
| 2 | 6 mm × 200 mm hardened rod | "6mm linear shaft 200mm" | 314 each | Robocraze (EN-31). Used: the 6 mm rods inside old inkjet/laser printers and CD/DVD writers (many are 6 mm; check with a vernier) |
| 2 | LM6UU linear bearing | "LM6UU" | 67 each | ElectronicsComp. **Or print 04_bushing_6mm.stl (free)** |
| 1 | M5 × 0.8 threaded rod, 170 mm (stainless if possible) | "M5 threaded rod 1 m" | approx. 60 to 120 per metre | hardware shop; cut with a hacksaw, file the end |
| 4 | M5 nuts (2 drive nuts, 2 lock nuts on the bearing) | | approx. 2 each | hardware shop |
| 1 | small spring, about 6 mm OD × 10 mm (anti-backlash) | "compression spring 6mm" | approx. 5 | hardware shop, or from a ball pen |
| 1 | 625ZZ bearing 5 × 16 × 5 | "625ZZ" | approx. 40 to 60 (pack of 4 approx. 150) | [Robocraze 625ZZ](https://robocraze.com/products/radial-ball-bearing-625zz-for-3d-printer), Zbotic. Used: Ender 3 wheels use 625ZZ, so a dead V-wheel gives you one |
| 1 | 5 mm to 5 mm rigid coupler (aluminium) | "5mm to 5mm rigid coupling" | approx. 80 to 150 | Robocraze, Probots, Zbotic. A flexible coupler also works but gives a little lag |
| 4 | M3 × 30 socket screws (motor) | | approx. 3 each | hardware shop |
| 3 | M5 bolts + nylock nuts, length to suit (pump body to Ender X carriage) | | approx. 4 each | the body's mount tab has three 5.3 mm holes; measure the stack before buying, see BUILD_GUIDE phase 5 |
| 2 | M5 × 12 screws (load cell to carriage) | | approx. 3 each | |
| 2 | M4 × 25 screws + nuts (plunger cup to load cell) | | approx. 3 each | |
| 1 | M5 nut for the printed knob | | 2 | (replaces a bought M5 knob) |

## C. Syringe and needles

| Qty | Item | Price (₹) | Notes |
|---|---|---|---|
| 2 | 10 mL glass syringe with METAL Luer lock | approx. 300 to 800 each | Flipkart / Amazon (KISC, "Glass syringe Luer lock 10ml"), IndiaMART lab suppliers, or your college lab store. Metal Luer is needed for the needle probe. Measure the flange and set FLANGE_D / FLANGE_T in cad/parts_v2.py before printing the cup. |
| 1 pack | blunt Luer-lock dispensing needles 22G to 26G | 2,200 for 40 (cart2india); approx. 150 to 300 for a mixed pack of 20 on Amazon.in | buy the stainless, blunt type |
| | Plastic syringes (practice) | approx. 10 each at any chemist | for water tests before you use glass |

## D. Sensors and electronics (Level 1)

| Qty | Item | Price (₹) | Notes |
|---|---|---|---|
| 1 | Arduino Nano (CH340 clone) + USB cable | 249 | Indian Hobby Center, Robu, Robocraze |
| 1 | 10 kg bar load cell + HX711 board | 165 (kit) | Robocraze. 10 kg is right: the plunger force is about 1.5 to 8 kg |
| 1 | KW12 micro switch with lever (syringe-empty) | approx. 10 to 20 | Used: the old Z end switch of the printer works too |
| 1 | copper-clad PCB, single side, small piece (probe plate) | approx. 30 to 60 | electronics shop |
| 1 | reed switch + magnet (door, optional) | approx. 20 to 40 | |
| 1 | 5 V relay module (UV, optional) | approx. 40 to 70 | |
| 1 | active buzzer 5 V | approx. 10 | |
| | jumper wires, 4-core cable 1 m, crocodile clip | approx. 100 | |
| 1 | USB webcam | 0 to 800 | any old webcam; used ones on OLX are approx. 300 |
| 1 | 5 V or 12 V UV LED strip, 365 to 405 nm (only if your ink needs it) | approx. 300 to 600 | the paper's slurry does NOT need UV |

## E. Filament for the printed parts

| Item | Price (₹) | Notes |
|---|---|---|
| PETG 1.75 mm, about 250 g needed | approx. 1,100 to 1,600 per kg | Numakers, eSun, Orange (Robu, Zbotic, Indian Hobby Center). If you cannot print yourself, a local 3D printing service charges approx. ₹3 to ₹8 per gram: the pump parts are about 200 g. PLA is fine for everything except 01, 02, 03. |

## Rough totals

| Build | Approx. total (₹) |
|---|---|
| Level 0 pump only, reusing the Ender extruder motor, printed bushings, used printer around ₹12k | **about ₹13,500** |
| Level 0 with all new pump parts and a new printer | about ₹21,500 |
| Add Level 1 sensors (Nano, load cell, switches, plate, buzzer) | + about ₹700 |
| Add webcam (used) | + about ₹300 |

## Printed instead of bought (saves money and waiting)

| Printed part | Replaces | Saving |
|---|---|---|
| 04_bushing_6mm (×2) | 2 × LM6UU | about ₹135; slightly more friction, oil with sewing-machine oil |
| 05_thumb_knob_m5 | M5 knob | about ₹50 |
| 08 / 09 dish rings | lab dish holders | |
| 07 probe holder + PCB scrap | commercial Z probe | about ₹1,500 (BLTouch clone) |
| 11 / 12 sensor box | project enclosure | about ₹150 |
