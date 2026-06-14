# mecer-32l81f-remote

IR remote codes for the **Mecer 32L81F** LCD TV (MStar TSUMV56 chipset, KTC board
`V56T4C1`, firmware `201809201125`). Recovered by reverse-engineering the firmware
dump when no physical remote was available.

The TV uses **NEC** with two customer codes:

| Customer code | Used for |
|---|---|
| `0x4040` | normal user keys |
| `0x4141` | engineer / service keys |

The same key code does different things depending on the customer code, because the
firmware branches on it.

## What's here

- **`mecer_remote.py`** — a small Flask web remote. Buttons POST to a Tasmota IR
  blaster on the LAN, which transmits the NEC frame. Open it on your phone.
- **`mecer_32l81f.lircd.conf`** — LIRC config (two remotes: user + service) for use
  with a Linux IR transmitter / `irsend`.

## Web remote (Tasmota blaster)

```bash
pip install flask requests
# edit BLASTER at the top of mecer_remote.py to point at your blaster
python3 mecer_remote.py
# open http://<this-host>:5000 on your phone
```

Each press sends a Tasmota `IRSend` with a 32-bit NEC frame.

## LIRC

```bash
sudo cp mecer_32l81f.lircd.conf /etc/lirc/lircd.conf.d/
sudo systemctl restart lircd
irsend SEND_ONCE mecer_32l81f KEY_POWER
irsend SEND_ONCE mecer_32l81f_service KEY_INTERNALINFO
```

## Code map

Vendor `0x40` (user) unless noted. Each frame is bit-reversed per byte on the wire
(standard NEC); the Tasmota `Data` value is the full reversed 32-bit frame.

| Key | cmd | | Key | cmd |
|---|---|---|---|---|
| POWER | `0x0A` | | INFO | `0x16` |
| MENU / BACK | `0x40` | | PREV (last ch) | `0x18` |
| EXIT | `0x20` | | CH LIST | `0x1D` |
| UP / DOWN | `0x0B` / `0x0E` | | SOURCE | `0x41` |
| LEFT / RIGHT | `0x10` / `0x11` | | TV | `0x4B` |
| OK | `0x0D` | | HDMI | `0xF7` |
| VOL + / − | `0x15` / `0x1C` | | AV | `0x4E` |
| MUTE | `0x0F` | | PC | `0xF5` |
| CH + / − | `0x1F` / `0x1E` | | TTX | `0x12` |
| 1–9 | `0x01`–`0x09` | | PAL/NTSC | `0x46` |
| 0 | `0x45` | | FREEZE | `0x00` |
| PIC MODE | `0x42` | | SLEEP | `0x17` |
| COLOR TEMP | `0x43` | | | |
| ASPECT / ZOOM | `0x19` | | | |
| SOUND MODE | `0x1A` | | | |

### Service (customer code `0x4141`)

| Key | cmd | Notes |
|---|---|---|
| FACTORY1 | `0x4F` @ `0x40` | limited factory menu (user vendor) |
| FACTORY2 | `0xB6` @ `0x41` | factory menu via service vendor |
| FACTORY3 | `0xEF` @ `0x41` | factory / adjust twin |
| INTERNAL INFO | `0xBA` @ `0x41` | internal information screen |
| HDCP | `0xBD` @ `0x41` | HDCP service OSD |

## Notes

- **Power-on-when-AC-applied**: set via `u8PowerOnMode` / `bDCOnOff` in the factory
  block — normally reachable from the factory menu, or by editing the SPI flash dump
  directly.
- The service keys are diagnostic / engineering functions. Use at your own risk.

## License

Codes are facts about the hardware. Use freely. No warranty.
