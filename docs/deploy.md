# Deploy: switch-patcher

## First install

A stock Atmosphère console cannot launch the NSP yet: its program id is in OpenPak's `0x01FE…`
store range with a self-signed ACID and NCA header, which only OpenPak's boot package accepts
([docs/install-trust.md](install-trust.md)). The app is what normally installs that
package, so a first install starts from the boot zip on the same release:

1. Needs hekate, the official **Atmosphère 1.12.1** in `/atmosphere/package3` and firmware
   22.5.0, 23.0.0 or 23.0.1.
2. Extract `OpenPak-Switch-Patcher-Boot-<tag>.zip` onto the SD card root. It adds
   `/atmosphere/package3-openpak` (byte for byte what the app's OpenPak selection builds from
   that official package), `/bootloader/ini/openpak.ini` (hekate entries **OpenPak (emuMMC)**
   and **OpenPak (sysMMC)** under *More configs*) and its Atmosphère source notes under
   `/switch/openpak/boot-package/`. `hekate_ipl.ini` is not touched.
3. Boot **OpenPak (emuMMC)** from hekate's *More configs*.
4. Install `OpenPak-Switch-Patcher-<tag>.nsp` with an NSP installer (DBI, Goldleaf, Tinfoil
   and the like; it is a plain no-rights-ID application, no ticket).
5. Start **OpenPak Switch Patcher** from HOME and select **OpenPak**: from then on your own
   hekate entries boot OpenPak's package, and the bootstrap entry can be deleted.

## Updates

Updates come from the OpenPak eShop: the store serves each release as the update
`01fe000000000800` of the same title, and HOME offers it like any other software update.
There is no in-app update check.

**Enable** writes a marked block of `dns_mitm` host rules into
`/atmosphere/hosts/default.txt` and `/atmosphere/hosts/emummc.txt`, pointing the domain
families OpenPak claims at your server. **Disable** removes that block and leaves
the files exactly as they were — anything you had in them is preserved, and running enable
twice replaces the block instead of stacking copies. Both writes go through a temp file and
a rename, so an interrupted write can never strand the console between networks.

The server address lives in `/switch/openpak/server.txt` and is editable on the console with
the system keyboard (X). Changes take effect after a reboot, since `dns_mitm` reads the hosts
files at boot.

## Store installs and the firmware gate (0.3.15, 23.x in 0.3.18)

OpenPak targets system firmware **22.5.0, 23.0.0 and 23.0.1**. Everything it installs —
host rules, the browser/system CA, the News patches and the boot package —
is derived from those firmwares, so selecting OpenPak on any other version is
refused before a single file is written, with a message naming the version the
console actually runs. Selecting **Nintendo** removes cleanly on *any* firmware,
so a console updated after installing can always clean up; a console left on
OpenPak after an update is warned at launch and pointed at that fix.

Selecting OpenPak also makes OpenPak eShop titles launch. The store serves homebrew
as self-built NSPs with **no rights ID** (no ticket, so ES is not involved) and
program ids `0x01FE…`. Two console checks stop those, and OpenPak's boot package
`/atmosphere/package3-openpak` changes both:

- **Loader**: an Atmosphère 1.12.0 Loader that accepts an invalid NPDM ACID
  signature for program ids `0x01FE000000000000`–`0x01FEFFFFFFFFFFFF` only.
- **FS**: an Atmosphère 1.12.0 fusee with one compiled-in `nop` over the branch that
  acts on the NCA header-signature verdict, in the stock FS KIPs fusee identifies by
  hash as 22.5.0 (`0x26938`, FAT32 and exFAT) and 23.0.0 (`0x279A8`, exFAT `0x279B8`).
  Any other FS is left alone. The 23.0.0 offsets are not yet checked against the
  decrypted KIP or on hardware.

The News patches and the browser CA patch are keyed by module build id, so on 23.x they
wait for 23.x builds; the system CA patch has its 23.0.0 row.

There is no SD patch file: this fusee reads no `/atmosphere/kip_patches`. A Loader
KIP in `/atmosphere/kips` (Horizon OC's `hoc.kip`, for example) is loaded ahead of
OpenPak's; enable names it in a warning and leaves it alone. Proven on hardware
2026-10-04 (JKSV installed from the eShop and ran). See
[`docs/install-trust.md`](install-trust.md) for the derivation, the package
layout, upgrading from the `ams_mitm`-only package, and recovery.

## The Album opens the Album (0.3.16)

OpenPak is a HOME-menu title now (`01FE000000000000`, from its own eShop), so the Homebrew
Menu stops being the everyday launcher. Atmosphère opens the Homebrew Menu in place of the
Album (`010000000000100D`) unless R is held. Selecting **OpenPak** turns that round: the Album
opens the Album, and holding **R** while opening it gives the Homebrew Menu. The message
line says so after enable.

What changes is one key of `/atmosphere/config/override_config.ini`, section `[hbl_config]`:
`override_key_0` goes from `!R` (Atmosphère's default, "hbmenu unless R") to `R` ("hbmenu
only while R"). An existing `override_key_0`/`override_key` value is edited in place; a
missing one is added at the end of `[hbl_config]` (or a `[hbl_config]` section is added);
every other line, section, comment and line ending stays as it was. With no file at all,
one is created: `[hbl_config]`, `program_id_0=010000000000100D`, `override_key_0=R`. The
file as found (or the fact that there was none) is kept in `/switch/openpak/system`
(`album.original`, `album.absent`, `album.managed`); selecting **Nintendo** puts those exact
bytes back, or deletes the file OpenPak created.

The file is read the way Atmosphère's Loader reads it (inih: comments, inline `;` comments,
`=` or `:`, any case, continuation lines, last value wins, `program_id`/`override_key` as
slot 0). If it sends another title to the Homebrew Menu in slot 0, puts the Album in another
slot, or uses a key other than `!R`/`R`, it is somebody's choice: left as it is, with a note,
and the rest of OpenPak still applies. A file changed after OpenPak edited it is likewise
kept, by enable and disable alike. The Loader rereads the file at every launch, so enable
takes effect at once; after disable Atmosphère keeps what it last read until the reboot
offered there.

## Save Data Cloud

On firmware **23.0.0/23.0.1**, selecting OpenPak also lets the console's FS accept save-transfer
key-seed packages signed by OpenPak's saves server: hekate swaps FS's KeySeedPackage-signing
modulus (`.rodata` `0x5550`, 256 bytes) for OpenPak's at every boot. Two edits do it:
OpenPak's `[FS:34383ee799926340]`/`[FS:fdaf163288e10805]` sections in
`bootloader/patches.ini` (appended; everything else in the file kept byte for byte), and
`kip1patch=openpak_ksp` in the hekate launch entries that boot the MMC the app runs on (never a
`stock=1` entry). hekate checks the retail bytes before writing and skips any other FS, and this
works under stock Atmosphère too. Selecting **Nintendo** removes both. Every change is logged to
`/switch/openpak/system/save-data-cloud.log`. Starting with v0.3.22, the default build applies
the patch when selecting OpenPak; reboot through the matching hekate entry to activate it.
v0.3.23 corrects the retail key slot; update and reapply if using v0.3.22 or earlier.
An empty `/switch/openpak/save-data-cloud.dry-run` file, or a build compiled with
`OPENPAK_KSP_DRY_RUN=1`, makes it log only. v0.3.21 always ran dry and needs an update and
reapply to install the patch. Select Nintendo before a firmware update, or hekate stops at
*Failed to apply 'openpak_ksp'* (POWER continues). See
[`docs/save-data-cloud.md`](save-data-cloud.md) for the derivation, the safety checks and
recovery from a PC card reader.

## Hosts updater: openpak-fetchd (unreleased)

Selecting **OpenPak** also installs `openpak-fetchd` (source: `console/openpak-fetchd`), a boot2
sysmodule (title `01FE000000000F00`) that keeps the OpenPak block of `/atmosphere/hosts/default.txt`
and `emummc.txt` current without opening the app: about 20 s after the network is up, then every
6 h of uptime, it fetches the signed ceiling and the switch profile from openpak.org, rewrites
only the marked block and tells dns_mitm to reload. Trust is the app's: the ceiling must verify
under the pinned Ed25519 key, its version may never go down (floor = the higher of
`/atmosphere/openpak-fetchd/ceiling.version` and the app's `/switch/openpak/ceiling.version`), a
host outside the signed families is dropped, and a failed fetch or check changes nothing. It never
creates a block: the app writes the hosts files first (the app is authoritative on select), fetchd
only refreshes what is there, and keeps the previous file as `<file>.openpak-prev`.

Files written on select, in this order, nothing else, and only when `romfs:/system/openpak-fetchd.nsp`
has the sha256 recorded in `source/fetchd_asset.h` (a fresh install that fails midway is rolled back):

- `/atmosphere/contents/01FE000000000F00/exefs.nsp` (temp file, read back, renamed in);
- `/atmosphere/contents/01FE000000000F00/flags/boot2.flag` (empty: starts it at boot);
- `/atmosphere/openpak-fetchd.auto` (empty, last: arms the hosts writes).

Selecting **Nintendo** deletes the title folder, every `/atmosphere/openpak-fetchd*` entry (`.auto`,
`.write`, `.enable`, `.dry`, `.running`, `.stop`, the log and `.log.1`, the `openpak-fetchd/` state
folder) and the hosts files' `.openpak-prev`/`.openpak-tmp` backups; afterwards no boot2 module of
ours exists. A copy still running keeps running until the reboot the tool offers, and may write its
log or `dry-block.txt` once more before it; it cannot recreate a hosts block. The new binary is
built by `tools/build-fetchd.sh` (devkitA64, under the build flock), which copies it to
`romfs/system/openpak-fetchd.nsp` and records its sha256 and the source tree's in
`source/fetchd_asset.h`; `--check` verifies both. `tools/test-system.py` fails if nsp and header
disagree. The app's "OpenPak updated the redirects, re-apply" notice is not shown while fetchd is
installed, armed and its log was touched in the last 12 h (it is then keeping the block current).

## Choosing a network

Two entries, one choice:

```
  Nintendo                       Active
  OpenPak
```

Up/Down, **A** to pick, **B** to leave. The change is written the moment you select it and
the reboot that applies it is offered right there. The server address is built in — nobody
has to look one up — and can still be overridden with `-DOPENPAK_SERVER="HOST_IP"` at build
time or a line in `/switch/openpak/server.txt`.

Choosing **OpenPak** writes the rules and comments out anyone else's redirect for the same
hostnames (an `#openpak-off#` prefix), so the choice actually decides where the console goes
instead of falling through to another tool's leftovers.

## Building

```sh
podman run --rm -v "$PWD":/src -w /src docker.io/devkitpro/devkita64 make   # switch-patcher.nro
make test                     # host-side checks, no console needed
make nsp OUT=<dir>            # workstation only: build, then wrap as the NSP (hbstore-tools)
python3 tools/build-boot-zip.py --out <zip>   # the first-install boot zip
```

`switch-patcher.nro` is the program inside the NSP (hbstore-tools' loader runs it from
`/switch/.openpak/openpak.nro`, the path installed copies already use); it is not shipped on
its own. Drawn straight to the framebuffer with FreeType text: no SDL, no EGL, no mesa.
`make nsp` needs hbstore-tools set up and the console keys in `~/.switch/hbp.keys`; it is a
development build without the registry-verified network bundle.

## Releasing

1. Tag `vX.Y.Z` and push the tag. CI tests, builds the program with the verified bundle (run
   artifact `switch-patcher-nro`, kept 90 days), and creates the release with the boot zip and
   the network lockfile.
2. On the workstation, in hbstore-tools: `./run-hb.sh openpak-update vX.Y.Z` packages that
   artifact as the eShop update and then attaches `OpenPak-Switch-Patcher-vX.Y.Z.nsp` (the base
   NSP for first installs) to the release. `python3 hb2nsp.py openpak-nsp vX.Y.Z` attaches the
   NSP alone.

## System certificate support (0.3.1)

Select **OpenPak**, accept the reboot, and launch the game normally. Selecting
**Nintendo** restores the original system setup and offers the same reboot.
Stardew's executable is unchanged. Native Stardew online was confirmed working
with this system change; the revised installer needs a hardware round-trip.

This build supports the official **Atmosphere 1.12.0** package at
`/atmosphere/package3` with standard `pkg3` or `fss0` entries in
`/bootloader/hekate_ipl.ini`. Enable verifies the original package's complete
SHA-256, builds `/atmosphere/package3-openpak` with the replacement `ams_mitm`
(and, since 0.3.15, the store-trust Loader and fusee above), and updates those
entries automatically. A `package3-openpak` an earlier build wrote (including the
1.11.2 ones from 0.3.1–0.3.17) is replaced; any other file there stops setup. Update the SD
card to Atmosphère 1.12.0 first, then select OpenPak again, then update the firmware. The original package and autoboot
selection remain untouched. No extra installation or manual boot selection is
required. The active package can remain open while the app changes the boot
configuration. Unknown configurations produce a setup error.

The app reads the console's certificates through SSL and constructs a
certificate-store file, replacing expired certificate 1033 with the bundled
OpenPak CA. No Nintendo certificate archive is bundled. The original boot
configuration and any pre-existing certificate overlay are backed up in
`/switch/openpak/system`. Disable restores them. The inactive OpenPak package
is retained because it may still be open by the current boot; re-enable reuses
an identical package without rewriting it. Independently changed configuration
files, and a certificate overlay OpenPak did not write, are preserved, with setup stopped for
review. An overlay that carries the OpenPak CA is OpenPak's own whatever its layout — an
older build wrote it from the live certificate list rather than the CertStore file — so
re-applying replaces it instead of stopping. Writes are
staged and read back before activation. Do not delete the backup folder while
OpenPak is enabled.

Build the bundled open-source components (`ams_mitm`, Loader, fusee) with
`TMPDIR=<workspace dir> flock /tmp/openpak-build.lock bash tools/build-system-module.sh`.
Their source revision and local patches are listed in `romfs/system/SOURCE.txt`.
Run `make test` for host-side checks, and use
`python3 tools/test-system.py --package3 /path/to/official/package3` for the full
install/reapply/rollback, interrupted-activation and upgrade tests, and the check that the
store-trust package is byte for byte the one proven on hardware (add
`--store-package3 <package3-openpak-store>` to compare against that file too). Those inputs
are local and not distributed in this repository; `make test` picks them up from the
workspace's `private notes` when present and skips those tests otherwise.
