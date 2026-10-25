# Protocol: switch-patcher

## NAT check (2026-09-11)

The two Pia NAT-check names are in the managed list: `nncs1-lp1.n.n.srv.nintendo.net` goes
to the server and `nncs2-lp1.n.n.srv.nintendo.net` to the second responder on its own
address (the console requires two different public IPs). Both are answered by `nn-nncs`.

## News (2026-09-10)

Selecting **OpenPak** also installs the two News patches the News probe proved on hardware
(`news/tools/news-patch`): the BCAT verification key becomes OpenPak's, and the News catalog
download skips the Nintendo edge token. Both are keyed by the BCAT build id (HOS 22.5.0 and 23.0.x
today), so a console on another firmware simply ignores them. Selecting **Nintendo** removes
them. The News host `bcat-topics-lp1.cdn.nintendo.net` is in the managed host list. Re-select
OpenPak with this build, even if already active, then reboot.

Selecting OpenPak now also subscribes the News module to OpenPak's four channels and asks
it to receive (`SetSubscriptionStatus`, `RequestImmediateReception` on news:a). Patches and
host rules alone are not enough: the module only fetches channels it follows. Following a
channel sends subscription status **2** (subscribed) — on 22.5.0, status 1 means
*unsubscribed*, so the module never fetched our topics and refused to store their records.
Selecting Nintendo forgets those topics (status 0) and nothing else — the console's Nintendo
channels are never touched, and `ClearSubscriptionStatusAll` is never called.

The filter these commands take is a bare topic id (`[A-Za-z0-9_]{1,31}`); it is probed
read-only first, and only a filter naming an `openpak_` topic is ever written. If it is not
accepted the rest of the setup still applies.

A third News patch, `openpak_news_list_no_dauth`, joins the pair above: it lets the module's
list and titles/topics fetches proceed without a Nintendo edge token, the same way the
existing patch does for the memory download. All three are keyed by BCAT build id.
Untested on hardware as of 2026-09-23.

## Crash Team Racing key (2026-09-23)

Selecting **OpenPak** also installs `exefs_patches/openpak_ctr_key`: Crash Team Racing
Nitro-Fueled checks its Demonware login replies against a key in its own code, which no
console-level trust reaches, so this data-only IPS swaps that key for OpenPak's (the matching
private key signs on `servers/demonware`). It is one of the documented game-patch exceptions (see also D2R, PvZ and Duck Game below), keyed to
the final update's build id (`1C689518406930512C13DDF4217E7676`); details and evidence in
`servers/demonware/tools/ctr-key-patch`. Selecting Nintendo removes it. A patched CTR
rejects real Demonware's replies, so it only makes sense once the Demonware hostnames point at
OpenPak. Untested on hardware as of 2026-09-23.

## Among Us DTLS pin (2026-10-24)

Selecting **OpenPak** also installs `exefs_patches/openpak_among_us_dtls`. After the matchmaker
names a game server, every online game/auth path opens a Hazel DTLS session to it, and the client
accepts only the certificate its build pins by exact match (`serverCertificates.Contains`). The
pinned certificate is self-signed, so nothing without its private key can complete the handshake,
and neither `nn::ssl` nor the console certificate store is consulted. This data-only patch keeps
the exact-match pin but points it at OpenPak's own fixed DTLS certificate, and only it: a small
routine in the main's `.text` code cave fetches the presented certificate's DER and returns the
`Contains` result true only for an exact byte match against OpenPak's 843-byte certificate
(embedded read-only in `.rodata`); the reject branch and the handshake's signature check are
untouched, so the original certificate and any other certificate stay rejected. It is one of the
documented game-patch exceptions (owner-approved 2026-10-24, reconfirmed 2026-10-25), keyed to the
v3997696 update's build id (`19A77A3165441065F8B2B43A54A4F2AB`). The file comes from
`platforms/switch/games/among-us/tools/dtls-trust`; regenerate it there when the DTLS certificate
changes. Selecting Nintendo removes it. A patched client trusts only OpenPak's game server, so it
only makes sense with the `.among.us` family on OpenPak. Untested on hardware as of 2026-10-25.

## Plants vs. Zombies: Battle for Neighborville CA (2026-10-24)

Selecting **OpenPak** also installs `exefs_patches/openpak_pvz_ca`. The title does all its EA
TLS (the gosredirector, the CA service, Blaze) through EA's DirtySDK, which trusts only a CA
list built into the game and never the console's certificate store, so no console-level trust
reaches it. It is the documented PvZ exception to "no game patches" (owner decision,
2026-10-24): a data-only IPS that replaces one entry of that list, EA's "GOS 2015 Certificate
Authority", with the OpenPak CA's name and public key, and leaves every instruction as shipped.
It is keyed to update v1.0.4's build id (`5AD255D6667B6EB5BDCF74B74BCD2602`); the file comes
from `platforms/switch/games/plants-vs-zombies/tools/pvz-ca`, regenerate it there when the CA
changes. Selecting Nintendo removes it. A patched game no longer trusts EA's GOS 2015
certificates, so it only makes sense with the `.ea.com` family on OpenPak. Untested on hardware
as of 2026-10-24.

## Diablo II: Resurrected (2026-09-20)

Four names join the managed list: `geo.battle.net` picks the region,
`telemetry-in.battle.net` takes the client's events, `account.battle.net` is the web login
that issues the session, and `*.actual.battle.net` is the bgs gateway on port 1119. The
wildcard covers both regions on purpose — geo decides which one the title dials, so a console
that geolocates to EU would otherwise reach nothing.

`prod.depot.battle.net` is the content depot, which the title resolves on every boot and
OpenPak serves nothing on. It used to be listed and deliberately off. The family covers it
now, so those requests fail to connect instead of failing against Blizzard — the same
trade every other unserved name under a claimed family makes.

The certificate this app already installs into the ssl sysmodule covers geo, telemetry,
account and the gateway, because the title puts all four through `nn::ssl`. It does **not**
cover the game-server connection. After GameJoin the title dials its game server on TCP 443
with its own OpenSSL and trusts only a CA bundle built into the game, which no console-side
certificate can extend. So selecting **OpenPak** also installs
`exefs_patches/openpak_d2r_trust`. It is the documented D2R exception to "no game patches"
(owner decision, 2026-09-30 and 2026-10-24): a data-only IPS that replaces that bundle with
OpenPak's CA and leaves every instruction as shipped. It covers two build ids: the base game
`4DE22400C997ED2373F0643E9FE9B079DB0E8D72` and the update v1.0.34
`DB0507F36B84200AC05F75D76ED5026F903E6C9`. The files come from
`platforms/switch/games/battlenet/tools/d2r-trust`; regenerate both there when the CA changes.
Installing also deletes the hand-copied `exefs_patches/openpak-d2r/` files from before this
release. Selecting Nintendo removes both. Untested on hardware through this app as of 2026-10-24.

## Failure reports

When this tool fails — an install or remove that stopped (hosts, CA, patch or system
writes), a display that will not start, a crash of the app itself — it saves a small
report under `/switch/openpak/reports/` (at most 8; the oldest go first) and asks before
sending it to `https://openpak.org/api/v1/crash-reports`: **A** Send, **B** Don't send,
**X** Always, **Y** Never. Always/Never are remembered in `/switch/openpak/reports.txt`
(`always`, `never` or `ask`). A report saved by an earlier run, e.g. before a crash, is
offered at the next launch. Nothing is ever sent without that yes.

A report is the app version (sent as `"source": "nro"`, the source the crash-report API
already accepts), firmware and Atmosphère version, what was being done and the
error text (for a crash: the exception type and the faulting offsets). No account token or
console identifier is sent. The pure half (JSON, multipart body, queue, setting) is
`source/report.c`, checked by `make test`; the console half is `source/crash.c`.

## Where the host list comes from

Not from this repository any more. The block is generated from the signed v2 platform
bundle the release pipeline fetches and verifies, and the console reads it at runtime:
a downloaded bundle on the SD card if there is one, otherwise the bundle this app
shipped with, otherwise a short list compiled in as a last resort. Adding a forwarder
is a server deploy, not a new app release.

`source/hosts.c` still carries that last resort, and it is deliberately frozen. It
mirrors what the bundle emits so that a console falling back to it does not quietly
behave differently from one that did not.

### Signed redirect ceiling (live profile)

When the tool opens with a connection it fetches, from `openpak.org` only, the signed
redirect ceiling (`/api/v1/network/ceiling`) and the Switch network profile
(`/api/v1/network/profile?platform=switch`); the contract is
[signed redirect ceiling](https://docs.openpak.org/contributors/signed-ceiling/). The ceiling is verified with Ed25519
against the pinned key (TweetNaCl, verify only, `source/ed25519.c`), cached under
`/switch/openpak/ceiling.json` exactly as received, and accepted only if its version is at
least the highest one ever accepted (`ceiling.version`). Every profile name outside the
verified ceiling is left out on its own and logged to `/switch/openpak/network.log`; the
rest become the rule set that selecting OpenPak installs, written the same way as a
bundle's (`*.family` plus the apex, overrides last). Without a verified ceiling the
families of the frozen list stand in for it.

Order of sources: the saved profile (just fetched, or from an earlier launch), then the
downloaded bundle, the bundled one, the frozen list. Nothing on the console changes in
the background: when OpenPak is installed and the effective set it would install differs
from the installed one (a digest recorded at install in `redirects.digest`, or read back
from the hosts block), the tool shows "OpenPak updated the Switch's network redirects.
Re-apply OpenPak and reboot to use them." Consoles using OpenPak DNS need none of this.

A bundle this build cannot fully apply is refused whole rather than applied in part —
an unknown schema version, another console's projection, an unrecognised rule action, a
capability this release does not implement. The interface names the source and revision
of the rules in force, so a console running the frozen fallback does not look current.

## What gets redirected

Everything the console reaches, as whole families with their apexes:

```
  Nintendo      .nintendo.net  .nintendo.com  .nintendowifi.net
  Served        .battle.net  .among.us  .photonengine.io  .exitgames.com
  Not yet       .demonware.net  .epicgames.dev  .ea.com  .xboxlive.com
                .live.com  .mojang.com  .microsoft.com
```

plus the NAT check's second responder on its own address.

**A console on OpenPak reaches OpenPak for all of it** — system updates, the eShop CDN,
telemetry, the browser, the connection test, and every third party a title dials. Names
nothing of ours answers on yet fail to connect rather than reaching a service that would
refuse the console: each of those services asks Nintendo to vouch for a token an OpenPak
console does not have. This tool is for banned, jailbroken and emulated consoles, so that
refusal was certain; the console now never talks to them at all.

The per-host record behind each third-party family — which title, which run, what was
seen — is in [`docs/researched-hosts.md`](researched-hosts.md).

Choosing **OpenPak** also comments out anyone else's redirect for a name in these
families (an `#openpak-off#` prefix), so the choice decides where the console goes.

Choosing **Nintendo** is a full revert: our block goes, every line we commented comes back
exactly as it was, and if the hosts file contained nothing but our own additions it is
deleted. The console is left as if this tool had never run. Nintendo's own addresses are
never written down — they rotate, and DNS resolves them correctly once nothing overrides
them.

## Game invitations (0.3.1)

The game-invitation service `*.five.nintendo.net` is included in the managed hosts
list. Earlier builds omitted it, preventing the native invitation applet from
reaching OpenPak in configurations that block Nintendo hosts.
