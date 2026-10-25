# Evidence: switch-patcher

## First install without the zip

Why not install the NSP without the zip: on stock Atmosphère the install goes through but the
title cannot start (FS rejects the NCA header signature, Loader the ACID). A console whose
sigpatches also patch Loader's ACID check (sys-patch does) may start it anyway; that is not a
supported path. `tools/build-boot-zip.py` builds the zip (no keys needed; CI attaches it).

## Version 0.3.0 activation

Version 0.3.0 attempted to replace the active package and failed on this console.
Version 0.3.1 replaces that activation method. Existing recovery copies from
0.3.0 can remain on SD; they are not used to select the boot package.
