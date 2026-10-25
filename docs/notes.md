# Notes: switch-patcher

Switches a CFW Nintendo Switch between Nintendo's servers and OpenPak's, and back. It is a
HOME menu title (`01FE000000000000`, shown as **OpenPak Switch Patcher**), shipped as an NSP
only and updated through the OpenPak eShop. Releases carry no NRO: the `openpak.nro` /
`openpak-console.nro` builds and their GitHub self-updater ended with v0.3.27, and an NRO
install from those releases does not update itself any more.

Written from scratch on libnx + SDL2 + SDL2_ttf; it ships no font, using the console's own
shared font instead. AGPL-3.0-only.
