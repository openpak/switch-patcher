# Switch Patcher

OpenPak's Switch Patcher.

| | |
| --- | --- |
| Console | Switch (custom firmware, Atmosphère) |
| Kind | HOME menu title, shipped as NSP (`01FE000000000000`) |
| Download | [Releases](https://github.com/openpak/switch-patcher/releases) (`vX.Y.Z` tags); updates from the OpenPak eShop |
| Licence | AGPL-3.0-only, see [LICENSE](LICENSE) |

## What it does

- Switches a CFW Switch between Nintendo's servers and OpenPak's, and back.
- Writes a marked block of `dns_mitm` host rules for the domain families OpenPak claims. Selecting Nintendo removes it.
- Installs the OpenPak CA into the console's certificate store and selects a boot package that lets OpenPak eShop titles start.
- Installs the News and Save Data Cloud changes, plus the few per-title patches for games that pin their own certificate.

## Install

A first install needs the boot zip from the release. Updates then come from the OpenPak eShop.

1. Extract `OpenPak-Switch-Patcher-Boot-<tag>.zip` onto the SD card root. It needs hekate, Atmosphère 1.12.1 in `/atmosphere/package3`, and firmware 22.5.0, 23.0.0 or 23.0.1.
2. Boot **OpenPak (emuMMC)** from hekate's *More configs*.
3. Install `OpenPak-Switch-Patcher-<tag>.nsp` with an NSP installer (DBI, Goldleaf, Tinfoil and the like).
4. Start **OpenPak Switch Patcher** from HOME and select **OpenPak**.

Full steps are in [deploy](docs/deploy.md).

## Build

```sh
podman run --rm -v "$PWD":/src -w /src docker.io/devkitpro/devkita64 make
```

See [deploy](docs/deploy.md).

## Docs

- [Protocol](docs/protocol.md)
- [Evidence](docs/evidence.md)
- [Deploy](docs/deploy.md)
- [Notes](docs/notes.md)
- [Install trust](docs/install-trust.md)
- [Researched hosts](docs/researched-hosts.md)
- [Save Data Cloud](docs/save-data-cloud.md)
- [Docs index](docs/README.md)

## Licence

See [LICENSE](LICENSE).
