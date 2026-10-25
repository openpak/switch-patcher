#!/usr/bin/env python3
# Host-side checks for the shipped IPS patch artifacts. No console needed. Run from the repo
# root (make test).
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BCAT_BUILD = "6D9772A733E2370B3F401EFEB7CA8F664309BD66000000000000000000000000"

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def parse_ips(path):
    """Return list of (offset, data) records, asserting a well-formed IPS."""
    b = open(path, "rb").read()
    assert b[:5] == b"PATCH", f"{path}: bad magic"
    assert b[-3:] == b"EOF", f"{path}: no EOF"
    i, recs = 5, []
    while i < len(b) - 3:
        off = int.from_bytes(b[i:i + 3], "big")
        size = int.from_bytes(b[i + 3:i + 5], "big")
        assert size != 0, f"{path}: RLE record unexpected"
        data = b[i + 5:i + 5 + size]
        assert len(data) == size, f"{path}: truncated record"
        recs.append((off, data))
        i += 5 + size
    assert i == len(b) - 3, f"{path}: trailing bytes before EOF"
    return recs


def parse_ips32(path):
    """Return list of (offset, data) records for an IPS32 patch (32-bit offsets)."""
    b = open(path, "rb").read()
    assert b[:5] == b"IPS32", f"{path}: bad magic"
    assert b[-4:] == b"EEOF", f"{path}: no EEOF"
    i, recs = 5, []
    while i < len(b) - 4:
        off = int.from_bytes(b[i:i + 4], "big")
        size = int.from_bytes(b[i + 4:i + 6], "big")
        assert size != 0, f"{path}: RLE record unexpected"
        data = b[i + 6:i + 6 + size]
        assert len(data) == size, f"{path}: truncated record"
        recs.append((off, data))
        i += 6 + size
    assert i == len(b) - 4, f"{path}: trailing bytes before EEOF"
    return recs


# 1. News list-fetch edge-token patch: two 8-byte records at the documented NSO
#    offsets, replacing the call site with 'strb wzr,[x0]; mov w0,wzr'.
list_ips = os.path.join(
    ROOT, "romfs/patches/exefs_patches/openpak_news_list_no_dauth", BCAT_BUILD + ".ips")
check(os.path.exists(list_ips), "news_list_no_dauth IPS missing")
if os.path.exists(list_ips):
    recs = parse_ips(list_ips)
    NEW = bytes.fromhex("1f00003 9e0031f2a".replace(" ", ""))
    want = {0x114098: NEW, 0x117380: NEW}  # titles/topics, list fetch
    got = {off: data for off, data in recs}
    check(got == want, f"news_list_no_dauth records {got!r} != {want!r}")

# 1b. The same patch for 23.0.0/23.0.1's bcat (same instruction shape, moved +0x3fd0).
BCAT_23 = "84EF6747BB15A01707B883B29A2A1CE5FC1734C2000000000000000000000000"
list23 = os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_news_list_no_dauth", BCAT_23 + ".ips")
check(os.path.exists(list23), "news_list_no_dauth 23.x IPS missing")
if os.path.exists(list23):
    got = {off: data for off, data in parse_ips(list23)}
    want = {0x118068: bytes.fromhex("1f000039e0031f2a"), 0x11b350: bytes.fromhex("1f000039e0031f2a")}
    check(got == want, f"news_list_no_dauth 23.x records {got!r} != {want!r}")
dauth23 = os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_news_no_dauth", BCAT_23 + ".ips")
check(os.path.exists(dauth23), "news_no_dauth 23.x IPS missing")
if os.path.exists(dauth23):
    recs = parse_ips(dauth23)
    check(recs == [(0x100074, bytes.fromhex("bf020039e0031f2a"))], f"news_no_dauth 23.x record unexpected: {recs!r}")
key23 = os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_bcat_key", BCAT_23 + ".ips")
check(os.path.exists(key23), "bcat_key 23.x IPS missing")
if os.path.exists(key23):
    k22 = parse_ips(os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_bcat_key", BCAT_BUILD + ".ips"))
    k23 = parse_ips(key23)
    check(len(k23) == 1 and k23[0][0] == 0x225254 and k23[0][1] == k22[0][1],
          "bcat_key 23.x must write the same OpenPak modulus at 0x225254")

# 2. News memory-download patch still there and well-formed (gating unchanged).
dauth_ips = os.path.join(
    ROOT, "romfs/patches/exefs_patches/openpak_news_no_dauth", BCAT_BUILD + ".ips")
check(os.path.exists(dauth_ips), "news_no_dauth IPS missing")
if os.path.exists(dauth_ips):
    recs = parse_ips(dauth_ips)
    check(len(recs) == 1 and recs[0][0] == 0xfc8a4 and len(recs[0][1]) == 8,
          f"news_no_dauth record unexpected: {recs!r}")

# 2b. Duck Game NEX heap patch (owner-approved 2026-10-25): one record, 'mov x8,#0' at IPS offset
#     0xED9B18 (NSO text 0xED9A18; was 'mov x8,#0xc800' = 08 00 99 d2), build id of the v1.0.4 update.
DUCK_BUILD = "D5446193E5BC2E4C17F552597E14DDB7" + "0" * 32
duck_ips = os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_duck_game_nex_heap", DUCK_BUILD + ".ips")
check(os.path.exists(duck_ips), "duck_game_nex_heap IPS missing")
if os.path.exists(duck_ips):
    check(parse_ips(duck_ips) == [(0xED9B18, bytes.fromhex("080080d2"))],
          "duck_game_nex_heap must be exactly 'mov x8,#0' at 0xED9B18")

# 2c. Among Us DTLS trust patch (owner-approved 2026-10-24, reconfirmed 2026-10-25): an IPS32
#     patch that re-pins the title's Hazel DTLS trust to OpenPak's certificate, and only it.
#     Verified structurally so a re-generated per-update file still passes: exactly three records
#     (OpenPak's DER into .rodata, the pinning routine into the .text code cave, and the redirected
#     Contains call), the 843-byte DER record must be OpenPak's exact certificate, and the 4-byte
#     record must be a BL whose target is the cave record (Contains -> OpenPak pin).
AMONG_BUILD = "19A77A3165441065F8B2B43A54A4F2AB" + "0" * 8
# SHA-256 of OpenPak's DTLS certificate DER (O=OpenPak, CN=OpenPak Among Us DTLS).
AMONG_DER_SHA256 = "f69ce61d6bfc2ceb001852b3548bfaea9b7b4a53911e8c70699d33e264bacc84"
among_ips = os.path.join(ROOT, "romfs/patches/exefs_patches/openpak_among_us_dtls", AMONG_BUILD + ".ips")
check(os.path.exists(among_ips), "among_us_dtls IPS missing")
if os.path.exists(among_ips):
    recs = parse_ips32(among_ips)
    check(len(recs) == 3, f"among_us_dtls must have 3 records, got {len(recs)}")
    der = [d for _, d in recs if len(d) == 843]
    check(len(der) == 1 and hashlib.sha256(der[0]).hexdigest() == AMONG_DER_SHA256,
          "among_us_dtls must embed OpenPak's exact 843-byte DTLS certificate DER")
    cave = [(o, d) for o, d in recs if 8 <= len(d) <= 256 and len(d) % 4 == 0 and len(d) != 4]
    bl = [(o, d) for o, d in recs if len(d) == 4]
    check(len(cave) == 1 and len(bl) == 1, "among_us_dtls must have one cave record and one 4-byte BL")
    if len(cave) == 1 and len(bl) == 1:
        bl_off, bl_data = bl[0]
        word = int.from_bytes(bl_data, "little")
        check((word >> 26) == 0b100101, "among_us_dtls patched call must be a BL")
        imm = word & 0x03FFFFFF
        if imm & 0x02000000:
            imm -= 0x04000000
        target = bl_off + imm * 4
        check(target == cave[0][0], "among_us_dtls BL must target the code-cave routine")

# 3. The store-trust FS change is compiled into OpenPak's fusee (romfs/system/fusee-1.12.1.bin,
#    docs/install-trust.md). Atmosphere's fusee (1.11.2, 1.12.0) reads no /atmosphere/kip_patches, so no
#    kip_patches payload may ship: it would look installed and do nothing.
check(not os.path.exists(os.path.join(ROOT, "romfs/patches/kip_patches")),
      "romfs/patches/kip_patches must not ship (fusee never reads it)")

if fails:
    print("patch/payload checks FAILED:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("patch artifacts: all checks passed")
