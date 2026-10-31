# OpenHead – plan för nytt repo

2026-10-31 · Patrik

OpenHead är ett fristående, generiskt projekt: ett protokoll för att använda en telefon eller surfplatta som robothuvud, en iOS/iPadOS-klient, ett Python-bibliotek, en simulator och en MCP-server. Planen är skriven för en kodningsagent som skapar repot från noll.

## Beslut och antaganden

Planen utgår från följande val. De är Patriks att ändra; agenten ska inte avvika från dem utan besked.

| Fråga | Beslut |
| --- | --- |
| Vad är produkten | Protokollet. iOS-appen är första referensklienten, simulatorn den andra. |
| Huvudets kunskap om kroppen | Ingen. Huvudet rapporterar egen pose och egna detektioner; roboten äger kinematik och nacke. |
| Versionering | Protokollet följer semver från `0.1.0`. Robotrepot pekar på `main` tills `0.1.0` är taggad, därefter på taggar. |
| Ansiktsmotor | Webbaserad (HTML/Canvas/TypeScript) i en WKWebView. Samma motor körs i simulatorn och i Playwright-tester. |
| Säkerhet | Parkopplingskod på skärmen ger en token per klient; mDNS enbart för upptäckt; dev-funktioner kräver dev-läge. Ingen TLS i v0.1. |
| MCP | Tunn adapter ovanpå Python-klienten. Semantiska kommandon som verktyg, senaste värden som resurser. Inga högfrekventa strömmar via MCP. |
| Var MCP-servern kör | På värden (Jetson, PC), aldrig på enheten. stdio först, Streamable HTTP som tillval. |
| ROS 2 | Utanför repot. Robotrepot bygger sin bridge på `openhead`-biblioteket. |
| Minsta OS | iOS/iPadOS 17. Universell app, fullskärm på iPad. |
| Montering | Telefonen sitter i **landskapsläge** på roboten (beslutat 2026-10-31). Ansiktsmotorn, simulatorn och golden-bilderna utgår från iPhone 12 liggande (844 × 390 punkter); porträtt och iPad testas som sekundära format. |
| Språk | Kod, README och protokolldokumentation på engelska. Den här planen på svenska. |
| Namn | **OpenHead** (beslutat 2026-10-31). Repo `openhead`, Python-paket och CLI `openhead`, Swift-mål `OpenHead`, mDNS `_openhead._tcp`, MCP-resurser `openhead://`, Bundle ID `<omvänd domän>.openhead`. Kontrollera GitHub, PyPI och npm före första push; vid krock på PyPI publiceras paketet som `openhead-head` med oförändrat importnamn. Kontrollerat 2026-10-31: `openhead` ledigt på PyPI och npm, repot skapat som `PatrikBichis/openhead`. |
| Licens | Apache 2.0 från första commit. |
| CI och testning | All testning sker lokalt (`tools/check.py`, körs som pre-push-hook). GitHub Actions används bara för signerat iOS-bygge och uppladdning till TestFlight, startat manuellt, med så få macOS-minuter som möjligt (beslutat 2026-10-31). |

## Omfattning för v0.1

v0.1 är klar när en agent på en PC kan parkoppla med en iPhone, byta tema, sätta känsla, visa en bild, ta en skärmdump och läsa loggen via MCP, och när samma scenario går grönt mot simulatorn lokalt.

Ingår:

- Protokoll: hello/pair, subscribe, `face.*`, `display.show` (bild och webb), `system.status`, `system.screenshot`, `log`-topic, `imu`-topic, `status`-topic.
- Ansiktsmotor med tre teman: `cartoon`, `minimal`, `halloween`. Tio gemensamma uttryck. Envelope-driven mun.
- iOS-app: ansikte, parkopplingsvy, inställningar, statusrad, IMU-ström, skärmdump, logg. Universell layout.
- Python: klientbibliotek, simulator med fönster, MCP-server (stdio), exempel-skript, scenariokörare.
- Lokal verifiering: schemavalidering, Python-tester, Playwright-tester av motorn, Swift-modellkontroll (`tools/check.py`).
- GitHub Actions: endast signerat iOS-bygge och TestFlight-leverans.

Väntar till v0.2 och senare:

- `pose` (ARKit), `faces` (ansiktsdetektion), kameror, GPS, video och WebRTC.
- Teman pushade vid körning, Streamable HTTP för MCP, TLS.
- `look_at` i världsram (kräver pose).

## Repostruktur

Monorepo med protokollet överst. Allt annat är klienter eller verktyg som beror på det.

```
openhead/
├── protocol/
│   ├── schema/                 # JSON Schema (draft 2020-12), en fil per meddelandetyp
│   │   ├── envelope.json       # type, ts, seq, id, protocol_version
│   │   ├── commands/           # face.set_emotion.json, display.show.json, …
│   │   ├── topics/             # imu.json, status.json, log.json, …
│   │   └── theme.schema.json   # validerar temapaket
│   ├── VERSION                 # 0.1.0
│   ├── CHANGELOG.md
│   └── docs/                   # genererad referens (json-schema-for-humans)
├── face/                       # ansiktsmotor, TypeScript + Canvas, byggs med Vite
│   ├── src/
│   ├── themes/                 # cartoon/ minimal/ halloween/
│   ├── tests/                  # Playwright: golden-bilder per tema × uttryck
│   └── dist/                   # byggd bundle; checkas INTE in, byggs lokalt och i iOS-workflowen
├── apps/ios/                   # SwiftUI-skal; project.yml för XcodeGen
│   ├── OpenHead/
│   │   ├── App/  Link/  Sensors/  Display/  Face/ (WKWebView-värd)  Settings/  Logging/
│   │   └── Resources/face/     # kopia av face/dist vid bygge
│   ├── OpenHeadTests/
│   ├── OpenHeadUITests/        # XCUITest med skärmdumpar
│   └── ExportOptions.plist
├── python/
│   ├── pyproject.toml          # ett paket, tre moduler, extras: [mcp], [sim]
│   └── src/openhead/
│       ├── client/             # asyncio-klient, modeller genererade från schema
│       ├── sim/                # simulator: server + fönster som kör face/dist
│       ├── mcp/                # MCP-server
│       └── cli/                # openhead pair|screenshot|logs|run|sim|mcp
├── scenarios/                  # YAML-scenarier, körs mot sim och enhet
├── examples/
├── docs/                       # ios.md (TestFlight), dev-loop.md, themes.md
├── tools/                      # protocol.py (validering, generering), check.py (alla lokala tester), apple_setup.py
├── .github/workflows/
│   └── ios-testflight.yml      # signerat bygge → TestFlight, startas manuellt
├── LICENSE                     # Apache 2.0
└── README.md
```

Regler:

- Python-modeller (pydantic) och Swift-modeller genereras från schema med `tools/protocol.py` och checkas in; pre-commit kontrollerar att de är aktuella. Handskrivna kopior är inte tillåtna. Generatorer: `datamodel-code-generator` för Python, en liten egen generator eller `quicktype` för Swift.
- `face/dist` byggs lokalt och av iOS-workflowen före `xcodegen`; appen får aldrig en inaktuell motor.
- Teman valideras mot `theme.schema.json` av `tools/protocol.py check` (pre-commit).
- `CHANGELOG.md` uppdateras i samma commit som en schemaändring; pre-commit-hooken stoppar committen annars.

## Protokollet

En WebSocket per klient, JSON-meddelanden, enheten är server. Varje meddelande har `type`, `ts` (ms, enhetens klocka), `seq` (per riktning). Kommandon har `id` och besvaras med `ack {id}` eller `error {id, code, message}`. Enheten kan ha flera klienter samtidigt; kommandon som påverkar skärmen vinner senaste-först.

Handskakning: `hello {client, protocol_version}` → `pair_required {code_hint}` eller `welcome {token, device, capabilities, themes}`. Klienten sparar token och skickar den i `hello` nästa gång. Versionsmatchning: major måste vara lika, enheten annonserar sin minor; klienten får inte använda fält som är nyare än enhetens minor.

Topics (prenumeration med `subscribe {topic, rate_hz, fields?}`; enheten klampar rate till vad den klarar och svarar med faktisk rate):

| Topic | Max Hz | Innehåll | Version |
| --- | --- | --- | --- |
| `imu` | 100 | `q[4]`, `gyro[3]`, `accel[3]`, `frame` | 0.1 |
| `status` | 1 | batteri, laddning, termiskt läge, aktiv vy, aktivt tema, aktiv känsla, länkkvalitet, uptime | 0.1 |
| `log` | händelsestyrt | `level`, `subsystem`, `message`, `seq_ref?` | 0.1 |
| `pose` | 60 | position, orientering, `tracking_state`, `frame: world` | 0.2 |
| `faces` | 15 | lista med `id`, `bearing`, `elevation`, `size`, `confidence` | 0.2 |
| `gps` | 1 | lat, lon, alt, noggrannhet | 0.2 |
| `env` | 10 | barometer, magnetometer, närhet | 0.2 |

Kommandon i v0.1:

| Kommando | Parametrar | Svar |
| --- | --- | --- |
| `face.set_theme` | `name`, `transition_ms?` | ack |
| `face.set_emotion` | `name`, `intensity 0–1`, `duration_ms?`, `blend: replace\|add` | ack |
| `face.look_at` | `frame: screen\|head`, `x`, `y` eller `yaw`, `pitch`, `duration_ms?` | ack |
| `face.blink` | – | ack |
| `face.envelope` | `level 0–1` (skickas som ström, ingen ack) | – |
| `face.list` | – | teman med uttryck och extra uttryck |
| `display.show` | `type: face\|image\|web`, `source` (url/base64), `overlay: none\|face-corner`, `duration_ms?` | ack |
| `display.clear` | – | ack |
| `system.status` | – | samma som `status`-topic |
| `system.screenshot` | `scale?` | `{url}` eller base64 PNG |
| `system.logs` | `n`, `level?` | senaste raderna |
| `system.diagnostics` | – | krasch, behörigheter, termik, ARKit-läge |
| `system.settings` | `get` / `set {key, value}` | värden |

Felkoder: `unauthorized`, `unsupported`, `busy`, `invalid_params`, `dev_mode_required`, `rate_limited`. Alla kommandon är idempotenta utom `camera.capture` (v0.2).

Mediaöverföring: bilder till enheten skickas som URL (enheten hämtar) eller base64 under 1 MB. Skärmdumpar och foton levereras som URL till enhetens inbyggda HTTP-server på samma port + 1, giltig i 60 s, token i header.

## Ansiktsmotor och teman

Motorn är en fristående webbapp (TypeScript, Canvas 2D, inga ramverk) som exponerar ett litet JavaScript-API: `setTheme(theme)`, `setEmotion(name, intensity, blend)`, `setGaze(x, y)`, `setEnvelope(level)`, `blink()`, `tick(dt)`. iOS-skalet och simulatorn anropar samma API; Playwright testar den direkt. Motorn vet inget om WebSocket.

Parametermodell (motorns interna tillstånd, blandas varje bildruta):

| Grupp | Parametrar | Område |
| --- | --- | --- |
| Ögon | `open_l`, `open_r`, `tilt_l`, `tilt_r`, `pupil`, `gaze_x`, `gaze_y`, `squint` | 0–1 resp. −1–1 |
| Mun | `open`, `width`, `curve`, `asym`, `teeth` | 0–1 resp. −1–1 |
| Globalt | `head_tilt`, `breath_rate`, `blink_rate`, `jitter` | normaliserade |

Uttryck är parametervektorer; aktiva uttryck blandas med vikter och övergångar tweenas (default 250 ms). Envelope adderas på `open` med temats egen kurva. Idle-beteende (blink, mikroblick, andning) ligger i temat så att halloween kan ha långsamma tunga blinkningar och cartoon snabba.

Temapaket:

```
face/themes/halloween/
├── theme.json        # name, version, palette, shapes, idle, render
├── expressions.json  # per uttrycksnamn: parametervektor; extra: { "cackle": {...} }
└── assets/           # valfria PNG/SVG för öga, mun, bakgrund, overlay
```

`theme.json` i korthet: `palette` (bg, sclera, iris, pupil, lid, mouth, teeth, accent), `shapes.eye` och `shapes.mouth` som antingen `preset` (`round`, `almond`, `slit`, `pixel`, `line`) eller `path` (SVG-bana i normaliserade koordinater) eller `image` (referens till assets, med ankare och skalning), `render` (stroke, glow, scanlines, pixelate), `idle` (blink_interval, saccade, breath).

Gemensamma uttrycksnamn, obligatoriska i varje tema (utökat från tio till 28 den 2026-10-31): `neutral`, `happy`, `curious`, `thinking`, `surprised`, `sad`, `angry`, `sleepy`, `scared`, `mischievous`, `confused`, `shocked`, `excited`, `bored`, `skeptical`, `worried`, `disgusted`, `embarrassed`, `proud`, `determined`, `relieved`, `annoyed`, `suspicious`, `laughing`, `disappointed`, `focused`, `nervous`, `smug`. Saknas ett faller motorn på `neutral` och loggar en varning. Teman får lägga till egna; `face.list` rapporterar dem.

Layout: motorn renderar i valfri aspekt och placerar ögon och mun relativt en enhet som är kortaste sidan, men som på breda skärmar får växa till 1,35 × höjden, så att ansiktet fyller en liggande telefon (huvudfallet) och ändå har samma proportioner i porträtt, på iPad och i simulatorfönstret. Teman kan ange per-aspekt-justeringar men behöver inte.

Tre teman i v0.1: `cartoon` (runda ögon, tydlig mun, varm palett), `minimal` (två ljusstreck och en linje, mörk bakgrund, låg strömförbrukning) och `halloween` (bildbaserade ögon, spruckna, grön glöd, extra uttrycket `cackle`). Halloween finns för att bevisa att bildspåret fungerar, inte bara vektorspåret.

## iOS-appen

Appen är ett tunt skal: den äger länken, sensorerna, kamerorna och skärmen, och värdar ansiktsmotorn i en WKWebView. Ingen ansiktslogik i Swift.

Moduler:

- `Link`: WebSocket-server (Network.framework, `NWListener`), mDNS-annonsering `_openhead._tcp`, parkoppling och token-lager (Keychain), prenumerationsregister med rate-klampning, kommandorouter som validerar mot genererade modeller.
- `Face`: WKWebView med `face/dist`, brygga via `WKScriptMessageHandler` åt båda håll. Envelope och gaze skickas som `evaluateJavaScript` i batch per bildruta, inte per meddelande.
- `Display`: vyväxlare mellan ansikte, bild, webb och overlay-läge. Bildcache på disk.
- `Sensors`: `CMMotionManager` för IMU i enhetens ram med konfigurerbar monteringsoffset; v0.2: ARKit (`ARWorldTrackingConfiguration` med `userFaceTrackingEnabled` på A12+), Vision för ansikten på enheter utan TrueDepth, CoreLocation.
- `Logging`: OSLog-kategorier per modul, ringbuffert om 2 000 rader, utspelning till `log`-topic. Varje inkommande kommando loggas med `seq_ref`.
- `Settings`: anslutning (port, namn), dev-läge, monteringsoffset, temaval för frånkopplat läge, prenumerationsöversikt.
- `Screenshot`: `UIGraphicsImageRenderer` över rotvyn plus `WKWebView.takeSnapshot` för webbinnehållet; sammansatt PNG via den inbyggda HTTP-servern.

Lägen (`mode.set`): `sensing` (ARKit äger kamerorna, v0.2), `capture` (fri AVCapture, v0.2), `idle` (inga kameror; standard i v0.1).

Universell app:

- `TARGETED_DEVICE_FAMILY = 1,2`, `UIRequiresFullScreen = YES`, alla orienteringar på iPad, landskap (vänster och höger) på iPhone.
- Layouten är motorns ansvar; skalet ger den hela ytan och rapporterar `safeAreaInsets`.
- Statusrad och inställningar använder size classes; inga hårdkodade mått.

Drift på robot: `isIdleTimerDisabled = true`, rekommenderad guidad åtkomst, varning i UI när termiskt läge är `serious` eller högre. Appen återansluter inte själv, den är server; klienterna återansluter.

Begränsningar att dokumentera i `docs/ios.md`: appen måste vara i förgrunden; ingen Wi-Fi-Direct, enheten och värden måste dela nät; Lightning/USB-C-ljud används inte i v0.1.

## Python-paket

Ett paket `openhead` (Python 3.11+, asyncio, pydantic v2, websockets). Extras `[mcp]` och `[sim]`.

**Klient** (`openhead.client`): `Head.discover()`, `Head.connect(host, token=None)`, `await head.pair(code)`, `head.subscribe("imu", 100)` som async-iterator, `await head.face.set_emotion(...)`, `await head.system.screenshot()` som returnerar bytes. Modeller genererade från schema; en handskriven tunn fasad ovanpå. Automatisk återanslutning med backoff. Det här biblioteket är det enda robotrepot ska bero på.

**Simulator** (`openhead.sim`): samma server-API som iOS-appen, implementerat i Python. Kör `face/dist` i Chromium via Playwright, både med fönster och headless (ändrat från `pywebview` 2026-10-31: samma kod för fönster och tester, och skärmdumpar fungerar i båda lägena). Syntetisk IMU (konfigurerbar rörelse eller inspelad fil), syntetisk status. Stöder parkoppling med fast kod `0000` i dev-läge. Allt ett protokolltest behöver utan hårdvara.

**MCP-server** (`openhead.mcp`): byggd på det officiella Python-SDK:t för MCP, stdio i v0.1. Håller en klientanslutning mot vald enhet och exponerar:

| MCP | Underliggande |
| --- | --- |
| Tool `list_themes` | `face.list` |
| Tool `set_theme(name)` | `face.set_theme` |
| Tool `set_emotion(name, intensity, duration_ms)` | `face.set_emotion` |
| Tool `look_at(frame, x, y)` | `face.look_at` |
| Tool `show_image(url_or_path, overlay)` | `display.show type=image` (lokal fil serveras via tillfällig HTTP) |
| Tool `show_web(url)` | `display.show type=web` |
| Tool `show_face()` | `display.show type=face` |
| Tool `take_screenshot()` → image | `system.screenshot` |
| Tool `tail_logs(n, level)` | `system.logs` |
| Tool `get_status()` | `system.status` |
| Tool `get_diagnostics()` | `system.diagnostics` |
| Tool `wait_for(topic, predicate, timeout_s)` | prenumeration som avslutas vid träff; för `status`- och `log`-händelser i v0.1, `faces` i v0.2 |
| Tool `run_scenario(path)` | scenariokörare, returnerar rapport och skärmdumpar |
| Resource `openhead://status`, `openhead://themes`, `openhead://logs` | senaste cachade värde |

Ingen `imu` eller `envelope` via MCP. Envelope hör till värdens TTS-pipeline som använder klienten direkt.

**CLI** (`openhead`): `discover`, `pair <code>`, `screenshot -o fil.png`, `logs -f`, `emotion <name>`, `theme <name>`, `show <url>`, `run scenarios/x.yaml`, `sim [--headless]`, `mcp [--device host]`.

Tester: pytest mot simulatorn för hela protokollet; kontraktstester som laddar varje schema och verifierar att klientmodellerna serialiserar exempelmeddelanden identiskt.

## Utvecklings- och valideringsslinga

Målet är att kodningsagenten kan verifiera en ändring själv, i tre nivåer med ökande kostnad, och att samma scenario går att köra på alla tre.

**Nivå 1: motor och protokoll på PC, sekunder.** Playwright kör `face/dist` headless: för varje tema × uttryck tas en bild och jämförs mot golden-bilder i `face/tests/golden/` med tolerans. Pytest kör protokollscenarier mot `openhead sim --headless`. Inga enheter, inga minuter på macOS.

**Nivå 2: enhet på skrivbordet, minuter.** En iPhone eller iPad står laddad med senaste TestFlight-bygget, appen i förgrunden, dev-läge på, parkopplad med agentens maskin. TestFlight ställs på automatisk uppdatering så att nya byggen når enheten utan handpåläggning. Agenten kör `openhead run scenarios/x.yaml --device head-01.local` eller använder MCP-verktygen direkt: `take_screenshot` för att se, `tail_logs` för att förstå, `get_diagnostics` när något är fel. Det här är enda sättet att verifiera ARKit, kameror, prestanda och termik utan en Mac.

**Nivå 3: TestFlight-bygge, kvartar.** `ios-testflight.yml` startas manuellt (`gh workflow run ios-testflight.yml`), bygger signerat och laddar upp. Jobbet väntar inte på Apples processning, för att spara macOS-minuter; agenten följer status till Ready to Test lokalt via App Store Connect API. Inga tester körs i GitHub Actions; iOS-skalet verifieras på enheten (nivå 2).

**Scenariospråk** (`scenarios/*.yaml`):

```yaml
name: halloween-scared
steps:
  - set_theme: halloween
  - set_emotion: { name: scared, intensity: 1.0 }
  - wait_ms: 600
  - screenshot: halloween-scared.png
  - expect_log: { level: info, contains: "theme=halloween" }
  - expect_status: { theme: halloween, emotion: scared }
```

Köraren rapporterar pass/fail per steg, sparar skärmdumpar och loggutdrag i en katalog och, mot simulatorn, jämför skärmdumpar mot golden. Samma fil körs lokalt mot simulatorn, i nivå 2 och via MCP-verktyget `run_scenario`.

**Vad agenten ska göra vid varje ändring**: kör `tools/check.py` lokalt (nivå 1: motor, Playwright, pytest, scenarier, Swift-modeller); vid ändringar i iOS-skalet starta `ios-testflight.yml` och verifiera på enheten (nivå 2); vid ändringar som rör sensorer eller prestanda kör scenariot mot enheten (nivå 2) och bifoga skärmdump och loggutdrag i PR-beskrivningen. Dokumenteras i `docs/dev-loop.md` och i repots `AGENTS.md`.

## Säkerhet

Hotbilden i v0.1 är enkel: ingen på samma Wi-Fi ska kunna ta över skärmen, kameran eller läsa loggen utan att ha sett enhetens skärm.

- Parkoppling: enheten visar en sexsiffrig kod i 60 s när en okänd klient ansluter. Rätt kod ger en slumpad 32-bytes token knuten till klientens namn; token lagras i Keychain på enheten och i `~/.openhead/tokens.json` på värden. Max 5 felförsök, sedan 5 minuters spärr.
- Alla kommandon och prenumerationer kräver giltig token. `hello` utan token ger bara `pair_required`.
- Dev-läge: `system.screenshot`, `system.logs`, `system.diagnostics` och `settings.set` svarar bara när dev-läge är påslaget i appens inställningar på enheten. Standard av. Dev-läge syns som en ikon i statusraden.
- mDNS annonserar namn och port, inte token eller capabilities.
- Den inbyggda HTTP-servern för skärmdumpar och foton kräver token i header och ger URL:er som går ut efter 60 s.
- Ingen TLS i v0.1; nätet antas vara privat. TLS med självsignerat certifikat och pinning i klienten är planerat för v0.2 och finns med i protokollets `capabilities` redan nu så att klienter kan upptäcka det.
- Klienter kan återkallas i inställningarna; listan visar namn och senaste anslutning.
- Inget i protokollet transporterar ljud; mikrofon används inte av appen.

MCP-servern ärver detta: den är en klient som alla andra och behöver sin egen token. En agent kan inte göra mer via MCP än via WebSocket.

## CI/CD

Ett enda workflow. All testning sker lokalt (`tools/check.py`, pre-push-hook); GitHub Actions används bara för det som kräver macOS: signerat bygge och uppladdning.

| Workflow | Runner | Trigger | Gör |
| --- | --- | --- | --- |
| `ios-testflight.yml` | macos-15 | endast `workflow_dispatch` (manuellt, `gh workflow run`) | bygg motor, `xcodegen`, signerat arkiv, export, uppladdning till TestFlight; väntar inte på processning, skriver version och byggnummer i summeringen |

Ingen körning vid push och inget schema. TestFlight-byggen går ut efter 90 dagar; ett nytt bygge startas manuellt vid behov.

Apple-uppsättning, görs av Patrik en gång (detaljer i `docs/ios.md`):

1. Apple Developer Program-konto; notera Team ID.
2. App ID med explicit Bundle ID (t.ex. `<omvänd domän>.openhead`).
3. Apple Distribution-certifikat (CSR via OpenSSL på Linux), exporterat till `.p12`.
4. App Store Connect-distributionsprofil för App ID:t.
5. App i App Store Connect med Bundle ID; intern TestFlight-grupp med Patrik och testenheterna.
6. App Store Connect API-nyckel (Admin, krävs för att skapa certifikat och profiler); Key ID, Issuer ID, `.p8`. Steg 2–4 och secrets görs av `tools/apple_setup.py --github`.

Secrets i GitHub: `APPLE_DIST_CERT_P12_B64`, `APPLE_DIST_CERT_PASSWORD`, `APPLE_PROVISIONING_PROFILE_B64`, `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY`, `KEYCHAIN_PASSWORD`. Variables: `APPLE_TEAM_ID`, `IOS_BUNDLE_ID`, `IOS_SCHEME`.

Signeringsflöde: manuell signering med importerad `.p12` och profil i tillfällig nyckelring; `CURRENT_PROJECT_VERSION = github.run_number`; `MARKETING_VERSION` följer protokollets `VERSION`-fil så att app och protokoll alltid har samma versionsnummer. `ITSAppUsesNonExemptEncryption = NO` och alla usage-strängar sätts i `project.yml`.

Budget: macOS-minuter räknas 10×. Målet är under 10 minuter per bygge: cache för npm och SwiftPM, ingen väntan på Apples processning, inga tester i jobbet, och bara manuellt startade byggen.

## Arbetsordning

Varje steg har ett acceptanskriterium som agenten verifierar innan nästa påbörjas. Steg 1–5 kräver ingen Apple-uppsättning och inga macOS-minuter.

1. **Repo-skelett.** Mappstruktur, LICENSE, README (från utkastet), `AGENTS.md` med arbetsreglerna i den här planen, `.editorconfig`, `pre-commit` med schemavalidering. *Klart när schemavalideringen (`tools/protocol.py check`) är grön lokalt.*
2. **Protokoll v0.1.** Alla schema för v0.1, exempelmeddelanden per typ, genererade Python-modeller, genererad referens. *Klart när exempelmeddelandena validerar och docs byggs.*
3. **Ansiktsmotor.** Parametermodell, blandare, renderer, temat `cartoon`, sedan `minimal` och `halloween`. Playwright-tester med golden-bilder. *Klart när alla 3 × 10 kombinationer har golden-bilder och Playwright är grön lokalt.*
4. **Simulator och klient.** Server-implementation, parkoppling, prenumerationer, kommandon; klientbibliotek; CLI. *Klart när `scenarios/smoke.yaml` går grönt mot headless-sim lokalt (`tools/check.py`).*
5. **MCP-server.** Verktyg och resurser enligt tabellen; `--selftest` som kör mot sim. *Klart när Claude Code kan köra `set_theme`, `take_screenshot` och `tail_logs` mot simulatorn via stdio.*
6. **Apple-uppsättning.** Patrik gör stegen i CI/CD-avsnittet och lägger in secrets. Agenten förbereder `project.yml`, `ExportOptions.plist` och `ios-testflight.yml` under tiden.
7. **iOS-skal, del 1.** Länk, parkoppling, WKWebView med motorn, statusrad, inställningar, logg, skärmdump. *Klart när första TestFlight-bygget är Ready to Test och Patrik ser cartoon-ansiktet på iPhone, iPad mini och iPad.*
8. **Enhet i slingan.** Parkoppla skrivbordsenheten med agentens maskin; kör `smoke.yaml` mot enheten; verifiera skärmdump och logg via MCP. *Klart när samma scenario är grönt mot sim och enhet.*
9. **IMU och envelope.** `imu`-topic med monteringsoffset; envelope-driven mun; latensmätning skärmdump-till-skärmdump. *Klart när envelope på 25 Hz ger synlig munrörelse utan hack på iPhone 12.*
10. **Tagga 0.1.0.** CHANGELOG, release-notes, robotrepot byter från `main` till taggen.
11. **v0.2-spår** (ordning efter behov): ARKit-pose och lägen, ansiktsdetektion, kameror, teman vid körning, Streamable HTTP, TLS.

Steg 3–5 kan drivas parallellt av flera agentinstanser; steg 7 beror på 2–4 och 6.

## Öppna frågor

Agenten kör på antagandena ovan tills Patrik säger annat. Dessa påverkar ägande och bör avgöras före steg 6.

- [x] GitHub-organisation: personligt konto (beslutat 2026-10-31).
- [x] Apple-konto: privat (beslutat 2026-10-31). Omvänd domän för Bundle ID återstår.
- [x] Apache 2.0, publikt repo (beslutat 2026-10-31).
- [ ] Ska Python-paketet publiceras på PyPI vid 0.1.0, eller installeras från Git-tagg?
- [x] ROS 2: inget ROS-specifikt i det här repot. En brygga byggs separat senare vid behov (beslutat 2026-10-31).
- [x] Nivå 2-testenheter: iPhone 12 (baslinje, tekniknivån låses hit) och iPhone 18 Pro (verifiering). iPad i mån av tillgång. Android/ARCore kan komma senare; protokoll och motor hålls plattformsneutrala.
- [x] Halloween-temats bilder tas fram av agenten programmatiskt (beslutat 2026-10-31).
