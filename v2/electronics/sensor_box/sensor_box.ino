/*
  Slurry bioprinter v2 - SENSOR BOX (Arduino Nano / Nano clone with CH340)

  Plugs into the SAME computer that already runs the Ender 3 (USB).
  It does not move the printer. It only measures and reports; the
  watchdog program on the computer decides when to pause the print.

  Wiring (see ../WIRING.md):
    HX711  DOUT -> D2   SCK -> D3   VCC -> 5V   GND -> GND
    End switch (KW12, NO)   D4 -> switch -> GND   (pressed = LOW)
    Needle probe            D5 -> wire to the metal Luer needle;
                            copper probe plate -> GND (touch = LOW)
    Door reed switch (NO)   D6 -> reed -> GND     (door closed = LOW)
    UV relay module IN      D7  (HIGH = UV on; module powered from 5V)
    Buzzer (active, 5 V)    D8

  Serial 115200 baud. Every 100 ms it prints one line:
    S,<millis>,<force_g>,<end>,<probe>,<door_closed>,<uv>
  Commands (end with newline):
    T          tare (zero the load cell, do it with the plunger free)
    C<grams>   calibrate with a known weight on the cup, e.g.  C500
    U1 / U0    UV on / off (UV is refused and forced off if the door is open)
    B          short beep
    ?          print status / calibration factor

  Library: "HX711 Arduino Library" by Bogdan Necula (Arduino Library Manager).
*/
#include <HX711.h>
#include <EEPROM.h>

const uint8_t PIN_DOUT = 2, PIN_SCK = 3, PIN_END = 4, PIN_PROBE = 5, PIN_DOOR = 6, PIN_UV = 7, PIN_BUZ = 8;
const int EE_ADDR = 0;
const uint32_t EE_MAGIC = 0xB10B0001UL;

HX711 cell;
float scaleFactor = 420.0;   // counts per gram; replaced by C<grams>
bool uvOn = false;
unsigned long lastTx = 0, beepUntil = 0;
float lastG = 0;

struct Cal { uint32_t magic; float scale; long offset; };

void saveCal() { Cal c = { EE_MAGIC, scaleFactor, cell.get_offset() }; EEPROM.put(EE_ADDR, c); }
void loadCal() {
  Cal c; EEPROM.get(EE_ADDR, c);
  if (c.magic == EE_MAGIC && c.scale != 0 && !isnan(c.scale)) { scaleFactor = c.scale; cell.set_offset(c.offset); }
  cell.set_scale(scaleFactor);
}
void beep(unsigned ms) { digitalWrite(PIN_BUZ, HIGH); beepUntil = millis() + ms; }
bool doorClosed() { return digitalRead(PIN_DOOR) == LOW; }
void setUV(bool on) {
  if (on && !doorClosed()) { Serial.println(F("E,UV refused: door open")); beep(300); on = false; }
  uvOn = on; digitalWrite(PIN_UV, on ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_END, INPUT_PULLUP); pinMode(PIN_PROBE, INPUT_PULLUP); pinMode(PIN_DOOR, INPUT_PULLUP);
  pinMode(PIN_UV, OUTPUT); digitalWrite(PIN_UV, LOW);
  pinMode(PIN_BUZ, OUTPUT); digitalWrite(PIN_BUZ, LOW);
  cell.begin(PIN_DOUT, PIN_SCK);
  loadCal();
  Serial.println(F("I,slurry sensor box v2 ready"));
  beep(80);
}

void handle(String s) {
  s.trim(); if (!s.length()) return;
  char c = toupper(s[0]);
  if (c == 'T') { cell.tare(20); saveCal(); Serial.println(F("I,tared")); }
  else if (c == 'C') {
    float g = s.substring(1).toFloat();
    if (g <= 0) { Serial.println(F("E,use C<grams>, e.g. C500")); return; }
    cell.set_scale(1.0); long raw = cell.get_value(20);
    scaleFactor = raw / g; cell.set_scale(scaleFactor); saveCal();
    Serial.print(F("I,scale=")); Serial.println(scaleFactor, 4);
  }
  else if (c == 'U') setUV(s.length() > 1 && s[1] == '1');
  else if (c == 'B') beep(150);
  else if (c == '?') { Serial.print(F("I,scale=")); Serial.print(scaleFactor, 4); Serial.print(F(",offset=")); Serial.println(cell.get_offset()); }
}

void loop() {
  // hard interlock in firmware: door opened -> UV off at once, whatever the computer says
  if (uvOn && !doorClosed()) { setUV(false); Serial.println(F("E,door opened, UV off")); beep(500); }
  if (beepUntil && millis() > beepUntil) { digitalWrite(PIN_BUZ, LOW); beepUntil = 0; }
  if (cell.is_ready()) lastG = cell.get_units(1);
  if (Serial.available()) handle(Serial.readStringUntil('\n'));
  if (millis() - lastTx >= 100) {
    lastTx = millis();
    Serial.print(F("S,")); Serial.print(lastTx); Serial.print(',');
    Serial.print(lastG, 1); Serial.print(',');
    Serial.print(digitalRead(PIN_END) == LOW); Serial.print(',');
    Serial.print(digitalRead(PIN_PROBE) == LOW); Serial.print(',');
    Serial.print(doorClosed()); Serial.print(',');
    Serial.println(uvOn);
  }
}
