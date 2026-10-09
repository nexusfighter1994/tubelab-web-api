# TubeLab Web API — Referenz

Stand: 8. Oktober 2026. Eigener Dienst für das eigene TubeLab-Webkonto.

**Basis-URL:** `https://tubelab.example.org`

**Live-Doku:** `https://tubelab.example.org/docs`  
**Live-OpenAPI:** `https://tubelab.example.org/openapi.json`

Die API verwendet die angemeldete TubeLab-Websitzung auf dem Server. Ein offizieller TubeLab-API-Key ist dafür nicht erforderlich. Zum Zugriff wird der **eigene Schlüssel dieses Dienstes** benötigt. Das Pro-Konto war bei der Prüfung verbunden; zehn gemappte Funktionen und 15 gleichzeitige echte Outlier-Jobs wurden erfolgreich geprüft. Die noch offenen Funktionen stehen unten.

## 1. Authentifizierung

Bei jedem `/v1`-Aufruf einen dieser Header senden:

```http
Authorization: Api-Key <eigener-api-key>
```

Alternativ `Authorization: Bearer <eigener-api-key>` oder `X-API-Key: <eigener-api-key>`. Keinen Schlüssel in Queryparametern übertragen. Den Wert aus der separat gelieferten `data/api-key` als Secret bzw. Umgebungsvariable `TUBELAB_API_KEY` bereitstellen; diese Dokumentation und das Connect-Paket enthalten keine Zugangsdaten.

`/docs` und `/openapi.json` akzeptieren dieselben Header. Beim Öffnen im normalen Browser: Benutzer `admin`, konfiguriertes Admin-Passwort. Ohne `ADMIN_PASSWORD` oder private Datei `data/admin-password` dient der eigene API-Key als Passwort. Basic-Auth ist kein Ersatz für die Header-Authentifizierung der übrigen REST-Endpunkte.

## 2. Verbindung prüfen

Linux/macOS-Beispiele setzen voraus, dass `TUBELAB_API_KEY` bereits sicher gesetzt ist:

```bash
curl -sS https://tubelab.example.org/health

curl -sS -H "Authorization: Api-Key ${TUBELAB_API_KEY}" \
  https://tubelab.example.org/v1/session

curl -sS -H "Authorization: Api-Key ${TUBELAB_API_KEY}" \
  https://tubelab.example.org/v1/capabilities
```

`/health` ist öffentlich und bestätigt nur die Erreichbarkeit. `/v1/session` bestätigt die Provider-Anmeldung mit `authenticated:true`. Es kann auch **HTTP 200 mit `authenticated:false`** zurückkommen; dann muss Manuel den TubeLab-Login erneuern. Eine gültige eigene API-Authentifizierung bestätigt nicht automatisch eine gültige TubeLab-Sitzung.

Capabilities nennen je Funktion `available`, `liveTested`, `schemaCompatibility` und `missingFields`, außerdem die Queue-Konfiguration. `available:false` bedeutet nicht nutzbar. `liveTested` gilt für erfolgreiche Aufrufe seit dem letzten Start des Dienstes und ist kein dauerhafter Testbericht.

## 3. Endpunkte

Alle folgenden Pfade beziehen sich auf die Basis-URL. Unterstützte Provider-Leseanfragen können sowohl **HTTP 200** als auch **HTTP 202** liefern; bei 202 Abschnitt 5 beachten.

| Methode und Pfad | Eingabe / Zweck | Stand |
| --- | --- | --- |
| GET `/v1/search/channels` | `query`, `language`, `from`, `size` und Kanalfilter | Live geprüft |
| GET `/v1/search/channels/related` | `relatedChannelId=UC…` erforderlich | Live geprüft |
| GET `/v1/search/outliers` | `query`, `language`, `type=video` oder `short` und Outlier-Filter | Live geprüft |
| GET `/v1/search/outliers/related` | Mindestens `videoId`, `thumbnailVideoId`, `relatedChannelId` oder `title` | Live geprüft mit Video und Thumbnail |
| GET `/v1/search/trending-formats` | Titelmuster, z. B. `language=en&size=3` | Live geprüft |
| GET `/v1/channel/videos/{id}` | YouTube-Kanal-ID; Web-Stichprobe | Live geprüft; teilweise andere Felder |
| GET `/v1/channel/shorts/{id}` | YouTube-Kanal-ID; Web-Stichprobe | Live geprüft; teilweise andere Felder |
| GET `/v1/video/{id}` | YouTube-Video-ID | Live geprüft; teilweise andere Felder |
| GET `/v1/video/comments/{id}` | YouTube-Video-ID | Live geprüft; teilweise andere Felder |
| GET `/v1/credits/balance` | Keine Queryparameter; Antwort enthält `balance` | Live geprüft |
| GET `/v1/scan/{id}` | Vorhandene TubeLab-Prozess-ID | Gemappt, noch nicht live bestätigt |
| GET `/v1/video/transcript/{id}` | YouTube-Video-ID | Aktuell HTTP 501 |
| POST `/v1/scan` | Allgemeinen Scan starten | Aktuell HTTP 501 |
| GET `/v1/session` | Provider-Anmeldung prüfen | Sofortige Antwort |
| GET `/v1/capabilities` | Funktionen, Filter, Queue und Grenzen | Sofortige Antwort |
| GET `/v1/jobs` | Jobs; `state`, `limit=1..100`, `offset` | Queue-Verwaltung |
| GET `/v1/jobs/{id}` | Status eines Queue-Jobs | Queue-Verwaltung |
| GET `/v1/jobs/{id}/result` | Ursprüngliches Ergebnis oder gespeicherter Fehler | 200 / 202 / Fehlerstatus |
| GET `/v1/scans` | Lokal protokollierte Scan-Submissions; `limit`, `offset`, `state` | Kein Provider-Verlauf; aktuell keine neuen Scans möglich |

Die YouTube-Kanal-ID hat die Form `UC` plus 22 Zeichen; eine YouTube-Video-ID hat 11 Zeichen. Queue-Job-IDs sind UUIDs. Prozess-IDs und Queue-Job-IDs gehören zu unterschiedlichen Endpunkten.

## 4. Suche und Filter

Pagination: `from=0`, `size=1..40`. Nächste Seite beispielsweise `from=3&size=3`. Ohne Angabe verwendet der Dienst 20 Ergebnisse, für Titelmuster 12.

Arrayfilter als wiederholte Parameter übertragen:

```text
query=cooking&query=grilling&language=en&language=de
```

`language` ist bei Trending-Formaten ein einzelner Wert. Filter unterscheiden sich je Endpunkt: keine frei erfundenen Parameter senden. Die vollständigen Listen mit Typen und Auswahlwerten stehen in OpenAPI. Booleanwerte sind `true` oder `false`. Numerische Unter- und Obergrenzen müssen ein gültiges Intervall bilden.

Outlier-Sortierung: `sortBy=views|zScore|averageViewsRatio|publishedAt|revenue|rpm`, `sortOrder=asc|desc`. Datumsfilter wie `publishedAtFrom` akzeptieren die dokumentierten relativen Werte, z. B. `month`, oder ISO-Zeitstempel. Ein Datum mit `+` in der Zeitzone URL-encodieren.

### Beispiel: Outlier suchen

```bash
curl -sS --get \
  -H "Authorization: Api-Key ${TUBELAB_API_KEY}" \
  -H "Prefer: respond-async" \
  --data-urlencode 'query=engineering' \
  --data-urlencode 'language=en' \
  --data-urlencode 'type=video' \
  --data-urlencode 'from=0' \
  --data-urlencode 'size=3' \
  https://tubelab.example.org/v1/search/outliers
```

### Weitere gültige Aufrufpfade

```text
/v1/search/channels?query=cooking&language=en&size=3
/v1/search/channels/related?relatedChannelId=UCGHVuQpZRp_iz_Z6IB6gfLg&size=3
/v1/search/outliers/related?videoId=tWmxp1-Yqk4&size=3
/v1/search/outliers/related?thumbnailVideoId=tWmxp1-Yqk4&size=3
/v1/search/trending-formats?language=en&size=3
/v1/video/tWmxp1-Yqk4
/v1/video/comments/tWmxp1-Yqk4
```

Die IDs sind Beispiele aus der Live-Prüfung und keine Vorgabe für deine Recherche. Eigene gültige IDs oder IDs aus Suchergebnissen verwenden.

## 5. Queue und Polling

Jede unterstützte Provider-Leseanfrage wird als eigener Job gespeichert. Standard: ein Worker, mindestens eine Sekunde zwischen Starts, bis zu 1.000 offene Jobs. Ein normaler Request wartet bis zu 20 Sekunden. Für Agenten ist `Prefer: respond-async` praktisch: der Dienst bestätigt sofort mit HTTP 202.

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "status": "queued",
  "queuedAt": "2026-10-07T10:00:00.000Z",
  "statusUrl": "/v1/jobs/11111111-1111-4111-8111-111111111111",
  "resultUrl": "/v1/jobs/11111111-1111-4111-8111-111111111111/result"
}
```

Die obige UUID ist nur ein Schema-Beispiel. Verwende immer die vom aktuellen Request zurückgegebene URL.

1. `resultUrl` mit demselben API-Header abrufen, jeweils an derselben Basis-URL.
2. Bei 202 weiterhin dieselbe Ergebnis-URL pollen. `Retry-After` ist eine Anzahl Sekunden; aktuell üblicherweise 2.
3. Bei 200 enthält die Antwort das ursprüngliche Ergebnis, ohne zusätzliche Job-Hülle.
4. Bei einem Fehlerstatus den gespeicherten Fehler auswerten und das Polling beenden.

**Den ursprünglichen Suchrequest während des Pollings nicht wiederholen.** Das würde einen weiteren Job erzeugen. `Location` verweist auf die Status-URL; dort wird das große Ergebnis nicht ausgegeben. Jobstatuswerte sind `queued`, `running`, `succeeded`, `failed`.

`Prefer: wait=0` entspricht sofortiger Annahme; `Prefer: wait=60` erlaubt bis zu 60 Sekunden direktes Warten. Ein Provider-Cooldown kann auch früher zu 202 führen.

Bei TubeLab-429 kümmert sich der Server um bis zu fünf Wiederholungen und einen globalen Cooldown. Ein ausdrückliches Provider-Retry-After wird bis 24 Stunden berücksichtigt. Bei langer Wartezeit die Job-ID/Ergebnis-URL speichern und später weiter pollen. Ein Client-Timeout storniert den gespeicherten Job nicht.

Zielgrenzen fertiger Ergebnisse: sieben Tage, 1.000 abgeschlossene Jobs oder 256 MiB Ergebnisdaten; deshalb keine unbegrenzte Archivierung erwarten. Gelöschte Jobs liefern 404. Unterbrochene Lesejobs werden nach einem Dienstneustart wieder aufgenommen.

## 6. Ergebnisse lesen

Suchantworten enthalten `hits`. Die Payloads folgen den tatsächlichen Webdaten. Video-Details enthalten unter anderem `videoId` und `title`; Kommentare liegen in `items`. Guthaben liegt in `balance`. Kanal-Videos folgen der Webantwort mit `item.videos`; Kanal-Shorts liegen in `shorts`.

`_meta.source` ist `tubelab-web`. `_meta.fetchedAt`, `_meta.schemaCompatibility` und `_meta.missingFields` beschreiben Herkunft und bekannte Abweichungen. Fehlende Felder nicht erfinden. Die offizielle API und dieser Webdienst haben teilweise unterschiedliche Antwortfelder; `channel/videos` und `channel/shorts` sind Stichproben, kein garantierter vollständiger Export.

## 7. Fehler behandeln

Typische Fehlerantwort:

```json
{
  "status": "error",
  "error": {"code": "SESSION_EXPIRED", "message": "Please renew the TubeLab session."}
}
```

| HTTP / Code | Vorgehen |
| --- | --- |
| 401 `UNAUTHORIZED` | Eigenen API-Key und Header prüfen |
| 401 `SESSION_REQUIRED` / `SESSION_EXPIRED` | Den Kontoinhaber um erneute TubeLab-Anmeldung bitten; nicht endlos neu einreichen |
| 402 `INSUFFICIENT_CREDITS` | Provider-Guthaben reicht nicht; Den Kontoinhaber informieren |
| 404 `JOB_NOT_FOUND` | Ergebnis abgelaufen oder falsche ID; ursprünglichen Request nicht automatisch erneut senden |
| 404 `RESOURCE_NOT_FOUND` | Provider lieferte die Ressource nicht |
| 422 `INVALID_INPUT` / `INVALID_ID` / `UNSUPPORTED_FILTER` | Eingabe mit Referenz/OpenAPI abgleichen und korrigieren |
| 429 `RATE_LIMITED` | Bei einem vorhandenen Job seine Status- und Ergebnis-URL verwenden; Server-Cooldown respektieren |
| 501 `UNSUPPORTED_WEB_OPERATION` | Funktion ist nicht verfügbar; kein automatischer Retry |
| 503 `QUEUE_FULL` | Noch kein Job angenommen; mit Abstand erneut versuchen und Kapazität berücksichtigen |
| 502 Providerfehler | Fehler melden bzw. aktuellen Job prüfen; keine erfolgreiche Antwort behaupten |

Bei einem Verbindungsabbruch während der Erstanfrage kann unklar sein, ob bereits ein Job angelegt wurde. `/v1/jobs` prüfen; keine blinde Schleife zum erneuten Absenden. Bei einem Polling-Abbruch kann derselbe Ergebnisabruf erneut erfolgen.

## 8. Python-Client und Hermes

`tubelab_client.py` braucht nur Python und die Standardbibliothek. Der Schlüssel wird aus `TUBELAB_API_KEY` gelesen. Der Client verwendet `Prefer: respond-async` und pollt automatisch, standardmäßig höchstens zehn Minuten.

```bash
python3 tubelab_client.py --query engineering --language en --size 3
```

Für andere Endpunkte in Python:

```python
import os
from tubelab_client import get_result

base = "https://tubelab.example.org"
key = os.environ["TUBELAB_API_KEY"]
result = get_result(base, key, "/v1/search/channels?query=cooking&language=en&size=3")
```

Wird das Pollingbudget erreicht, bleibt der Job verfügbar; die Timeoutmeldung nennt seine Ergebnis-URL. HTTP-Fehler werden als Fehler weitergegeben. Hinweise für den Agenten stehen im separaten Hermes-Guide.

## 9. TubeLab-Login erneuern

Die normale Recherche braucht nur den eigenen API-Key. Cookies, Login-Passwörter und E-Mail-Tokens müssen nicht auf den Hermes-Rechner kopiert werden.

Für eine erneute Anmeldung kann ein autorisierter Aufruf von `POST /v1/login-ticket` einen einmaligen Handy-Link erzeugen. Die JSON-Antwort enthält `url` und `expiresAt`. Den Link nur Manuel zeigen; nicht in öffentliche Logs, Agenten-Ergebnisse oder Dokumentation schreiben. Linkgültigkeit 24 Stunden, Browserzugang nach Öffnen zwei Stunden.

Manuel meldet sich im Serverbrowser normal an. Bei E-Mail-Anmeldung kann er den vollständigen Bestätigungslink im Dashboard einfügen und **Bestätigungslink öffnen** drücken. Danach **Sitzung übernehmen**. Anschließend `/v1/session` erneut prüfen.

## 10. Grenzen und Paket

### Gemessene Credit-Kosten

Am 7. Oktober wurden alle fünf offiziell kostenpflichtigen Suchfunktionen mit jeweils zwei unterschiedlichen Anfragen geprüft: zehn erfolgreiche Antworten, Guthaben vor/nachher **456 → 456**, gemessener Verbrauch **0 Credits**. Nachprüfungen bis etwa 73 Sekunden nach den Aufrufen zeigten ebenfalls keine Abbuchung. Details stehen im Credit-Testbericht.

Die am 7. Oktober geprüfte [offizielle Preistabelle](https://tubelab.net/docs/api/pricing) nannte je Suchanfrage 1–5 Credits und für neue Scans 50 bzw. 100. Unsere Scan-Aufrufe werden weiterhin lokal mit 501 abgelehnt. Der Test bestätigt keinen kostenfreien erfolgreichen Scan und ist keine dauerhafte Preisgarantie; Provider-Cache und spätere Buchungen können nicht vollständig ausgeschlossen werden.

Transkripte und allgemeine neue Scans sind ausdrücklich nicht verfügbar. Das Lesen eines bestehenden Scans braucht eine TubeLab-Prozess-ID und ist noch nicht live bestätigt. Vollständige offizielle Feldparität und vollständiger UI-Ergebnisvergleich sind nicht bestätigt. Die 14,4 Sekunden für 15 Live-Jobs sind eine Messung und keine zugesicherte Dauer.

Das Connect-Paket enthält diese Referenz, einen kurzen Hermes-Guide, den Python-Client und einen OpenAPI-Snapshot. Im Snapshot ist die öffentliche Basis-URL für Importer ergänzt; Admin-/Login-Routen werden im Text beschrieben. Der Snapshot enthält keine Zugangsdaten. Das Live-Schema ist für den jeweils aktuellen Stand maßgeblich.


## 11. Alle Befehle zum direkten Aufrufen

Diese Beispiele sind für Bash/Linux und Hermes. `TUBELAB_API_KEY` muss bereits als Secret gesetzt sein. `CHANNEL_ID` und `VIDEO_ID` aus Suchergebnissen übernehmen; `JOB_ID` aus einer202-Antwort. `PROCESS_ID` bezeichnet einen vorhandenen TubeLab-Prozess.

```bash
BASE='https://tubelab.example.org'
api() { curl --silent --show-error -H "Authorization: Api-Key ${TUBELAB_API_KEY}" "$@"; }

# Erreichbarkeit, Sitzung und Funktionen
curl --silent --show-error "$BASE/health"
api "$BASE/v1/session"
api "$BASE/v1/capabilities"

# Kanal-Suche
api --get "$BASE/v1/search/channels" --data-urlencode 'query=engineering' --data-urlencode 'language=en' --data-urlencode 'size=3'

# Ähnliche Kanäle: relatedChannelId erforderlich
api --get "$BASE/v1/search/channels/related" --data-urlencode "relatedChannelId=$CHANNEL_ID" --data-urlencode 'size=3'

# Outlier-Suche und ähnliche Videos/Thumbnails
api --get "$BASE/v1/search/outliers" --data-urlencode 'query=engineering' --data-urlencode 'language=en' --data-urlencode 'type=video' --data-urlencode 'size=3'
api --get "$BASE/v1/search/outliers/related" --data-urlencode "videoId=$VIDEO_ID" --data-urlencode 'size=3'
api --get "$BASE/v1/search/outliers/related" --data-urlencode "thumbnailVideoId=$VIDEO_ID" --data-urlencode 'size=3'
api --get "$BASE/v1/search/outliers/related" --data-urlencode "relatedChannelId=$CHANNEL_ID" --data-urlencode 'size=3'
api --get "$BASE/v1/search/outliers/related" --data-urlencode 'title=How bridges are built' --data-urlencode 'size=3'

# Titelmuster / Trending-Formate
api --get "$BASE/v1/search/trending-formats" --data-urlencode 'language=en' --data-urlencode 'size=3'

# Kanal- und Videodaten: keine weiteren Queryfilter
api "$BASE/v1/channel/videos/$CHANNEL_ID"
api "$BASE/v1/channel/shorts/$CHANNEL_ID"
api "$BASE/v1/video/$VIDEO_ID"
api "$BASE/v1/video/comments/$VIDEO_ID"
api "$BASE/v1/credits/balance"

# Bestehender TubeLab-Prozess; noch nicht live bestätigt
api "$BASE/v1/scan/$PROCESS_ID"

# Queue: Status und ursprüngliches Ergebnis
api --get "$BASE/v1/jobs" --data-urlencode 'limit=25' --data-urlencode 'offset=0'
api --get "$BASE/v1/jobs" --data-urlencode 'state=failed' --data-urlencode 'limit=100'
api "$BASE/v1/jobs/$JOB_ID"
api "$BASE/v1/jobs/$JOB_ID/result"

# Lokale Scan-Historie, kein TubeLab-Kontoverlauf
api --get "$BASE/v1/scans" --data-urlencode 'limit=50' --data-urlencode 'offset=0'

# Dokumentation und Dashboard; API-Header funktioniert hier ebenfalls
api "$BASE/docs"
api "$BASE/openapi.json"
api "$BASE/dashboard"
api "$BASE/dashboard/data?httpLimit=25&jobLimit=25"
api "$BASE/dashboard/data?httpErrors=true&jobErrors=true&httpLimit=100&jobLimit=100"

# Anmeldung erneuern: Link nur privat öffnen, niemals in Logs/Chats veröffentlichen
api -X POST "$BASE/v1/login-ticket"

# Derzeit NICHT unterstützt: beide antworten501
api "$BASE/v1/video/transcript/$VIDEO_ID"
api -X POST "$BASE/v1/scan" -H 'Content-Type: application/json' --data '{"query":["engineering"],"mode":"fast","findBy":"query"}'
```

Die Beispiele mit Provider-Daten können202 zurückgeben. Dann immer die zurückgegebene `resultUrl` pollen, wie in Abschnitt5 beschrieben. Der Befehl `api "$BASE/dashboard"` liefert HTML; zum Ansehen die Dashboard-URL im Browser mit `admin` und dem gesonderten Admin-Passwort öffnen.

**REST verwenden:** Ein GET-Aufruf hat URL/Queryparameter und keinen JSON-Body mit `arguments`. Es gibt hier keinen generischen Tool-Broker-Endpunkt. `get_video_transcript` ist kein REST-Pfad; die Transkript-Route ist oben ausdrücklich501.

## 12. Alle Verwaltungs-, Dashboard- und Login-Routen

API-Header = eigener Dienstschlüssel. Admin Basic = `admin` und gesondertes Admin-Passwort. Mobiler Cookie = die vom `/connect`-Portal ausgestellte Sitzung; ein API-Key ersetzt diesen Cookie nicht.

| Methode / Pfad | Zugang | Eingabe / Antwort |
| --- | --- | --- |
| GET `/` | Öffentlich | Weiterleitung zu `/docs` |
| GET `/health` | Öffentlich | `{"status":"ok"}` |
| GET `/docs` | API-Header oder Admin Basic | HTML-Dokumentation |
| GET `/openapi.json` | API-Header oder Admin Basic | Live-OpenAPI der Recherche-API |
| GET `/dashboard` | API-Header oder Admin Basic | HTML-Logansicht |
| GET `/dashboard/data` | API-Header oder Admin Basic | JSON: `session`, `capabilities`, `activity`, `queue`, `timestamp`, `uptimeMs`, `timezone` |
| GET `/session/import` | API-Header oder Admin Basic | Browserformular und CSRF-Token |
| POST `/v1/session/import` | API-Header oder Admin Basic | JSON: `curl` ODER `cookies`, optional `userAgent`; mit Basic zusätzlich korrekter Origin/CSRF erforderlich |
| POST `/v1/login-ticket` | API-Header | Kein Body nötig. Antwort `url`, `expiresAt`; privater einmaliger24h-Link |
| GET `/connect` | Öffentliches Portal | Entfernt Ticketfragment aus URL; Portal verwaltet CSRF und Anmeldung |
| POST `/connect/redeem` | Ticket plus Portal-Origin/CSRF | JSON `ticket`, `csrf`; setzt2h-Cookie `__Secure-tubelab-login` |
| GET `/connect/status` | Mobiler Cookie | TubeLab-Sitzungsstatus |
| POST `/connect/verify` | Mobiler Cookie plus Origin/CSRF | JSON `link`, `csrf`; öffnet den TubeLab-E-Mail-Link, Antwort `opened:true` |
| POST `/connect/capture` | Mobiler Cookie plus Origin/CSRF | JSON nur `csrf`; übernimmt unabhängige Serverbrowser-Sitzung |
| GET / HEAD `/connect/desktop/{assetPath}` | Mobiler Cookie | Browseroberfläche/Assets; Bedienung über das Portal |
| WebSocket `/connect/desktop/websockify` | Mobiler Cookie plus exakter Origin | Geschützter Desktop-Tunnel; kein normaler REST-Befehl |

### Dashboard-Filter

Alle optional. Andere Parameter werden422 abgewiesen.

| Parameter | Typ / Grenze | Standard |
| --- | --- | --- |
| `httpLimit` | Ganzzahl1..100 |25 |
| `httpOffset` | Ganzzahl0..1000000 |0 |
| `httpErrors` | `true` / `false` |false |
| `jobLimit` | Ganzzahl1..100 |25 |
| `jobOffset` | Ganzzahl0..1000000 |0 |
| `jobErrors` | `true` / `false` |false |

HTTP-Logdaten:7Tage/10000Einträge. Jobs folgen der eigenen Queue-Aufbewahrung. Routen/Fehlercodes sind bereinigt; Ergebnisse, Header und Roh-Querystrings stehen nicht im Dashboard.

### Sitzungsimport mit dem API-Header

Nur erforderlich, wenn eine neue Provider-Sitzung importiert werden muss. Der Normalbetrieb braucht diesen Aufruf nicht. Inhalt privat halten.

```bash
# Datei enthält JSON {"curl":"<erfolgreicher TubeLab-Copy-as-cURL-Request>"}
api -X POST "$BASE/v1/session/import" -H 'Content-Type: application/json' --data-binary @tubelab-session-import.json
```

Alternativ JSON `{"cookies":[{"name":"<Name>","value":"<Wert>","domain":"<TubeLab-Domain>","path":"/","secure":true}],"userAgent":"<Browser-User-Agent>"}`. Unterstützte Cookiefelder: `name`, `value`, `domain`, optional `path`, `secure`, `httpOnly`, `expires` oder `expirationDate` (Unixsekunden), `hostOnly`, `sameSite`. Nur eigene zulässige TubeLab-Cookies verwenden. Browser-Basic-Import benötigt den vom Formular ausgegebenen `csrf` und den Origin `https://tubelab.example.org`.

Der Bestätigungslink im Portal muss HTTPS, Host `client.subgraph.tubelab.net`, Pfad `/auth/magiclogin/callback` und genau einen nichtleeren `token`-Parameter haben. Portalaktionen über dessen Buttons ausführen; Tokens und Cookies nicht an einen Recherche-Agenten weitergeben.

### Ressourcenfehler

Seit8.10.2026 wird ein expliziter TubeLab-GraphQL404 korrekt als `404 RESOURCE_NOT_FOUND` weitergegeben. Ein syntaktisch gültiger Kanal kann beim Provider trotzdem unbekannt sein. Zusätzliche Rechte des eigenen API-Keys lösen das nicht. Alte502-Logeinträge werden nicht nachträglich geändert.

## 13. Vollständige Suchparameter pro Endpunkt

Die folgenden Tabellen wurden direkt aus dem aktuellen Live-OpenAPI exportiert. Das JSON-Schema zeigt auch Enums, Mindest-/Höchstwerte und Arraytypen. Wiederholte Arraywerte mit mehrfach gleichem Querynamen senden, nicht als kommagetrennte Liste. Format-Sprache entsprechend ihrem Schema senden.

Gemeinsame zusätzliche Regeln: maximal100 Arraywerte, einzelne Arraytexte maximal300 Zeichen; nur dokumentierte Namen. Numerische `From`-Grenze muss bei gleichzeitig gesetztem `To` kleiner sein. Datums-`From` akzeptiert je Feld ISO-Datumzeit bzw. `month`, `trimester`, `semester`, `year`, `all`; Datums-`To` braucht eine gültige UTC-ISO-Datumzeit. `channels/related` braucht `relatedChannelId`; `outliers/related` mindestens einen der vier oben genannten Bezugswerte. Werte URL-kodieren.

### GET `/v1/search/channels`

| Parameter | Pflicht | Vollständiges Werteschema |
| --- | --- | --- |
| `from` | nein | `{"type":"integer","minimum":0}` |
| `size` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `sortBy` | nein | `{"type":"string","enum":["subscribers","averageViews","avgViewsToSubscribersRatio","viewVariationCoefficient","revenueMonthly","rpm","foundAt","recency","monetizationChangedAt"]}` |
| `sortOrder` | nein | `{"type":"string","enum":["asc","desc"]}` |
| `query` | nein | `{"type":"array","items":{"type":"string"}}` |
| `seed` | nein | `{"type":"string"}` |
| `filterBy` | nein | `{"type":"string","enum":["video","short"]}` |
| `contentKind` | nein | `{"type":"string","enum":["video","short","long-form","short-form"]}` |
| `publishedAtFrom` | nein | `{"type":"string"}` |
| `publishedAtTo` | nein | `{"type":"string"}` |
| `averageViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `averageViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `medianViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `medianViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `language` | nein | `{"type":"array","items":{"type":"string"}}` |
| `avgViewsToSubscribersRatioFrom` | nein | `{"type":"number","minimum":0}` |
| `avgViewsToSubscribersRatioTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `subscribersFrom` | nein | `{"type":"integer","minimum":0}` |
| `subscribersTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `videosCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `videosCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `viewVariationCoefficientFrom` | nein | `{"type":"number","minimum":0}` |
| `viewVariationCoefficientTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `revenueMonthlyEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `revenueMonthlyEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `rpmEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `rpmEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `avgDurationFrom` | nein | `{"type":"integer","minimum":0}` |
| `avgDurationTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `monetizationAdsense` | nein | `{"type":"boolean"}` |
| `monetizationSponsored` | nein | `{"type":"boolean"}` |
| `monetizationChanged` | nein | `{"type":"boolean"}` |
| `excludeNiche` | nein | `{"type":"array","items":{"type":"string"}}` |
| `referenceId` | nein | `{"type":"string"}` |
| `classificationQuality` | nein | `{"type":"string","enum":["negative","neutral","positive"]}` |
| `classificationIsFaceless` | nein | `{"type":"boolean"}` |
| `classificationIsOnCamera` | nein | `{"type":"boolean"}` |
| `joinedDateFrom` | nein | `{"type":"string"}` |
| `viewCountAllTimeFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewCountAllTimeTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `viewsPerHourEstimateFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewsPerHourEstimateTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `audienceRegion` | nein | `{"type":"array","items":{"type":"string","enum":["015","011","017","014","018","021","029","013","005","143","030","035","034","145","151","154","039","155","053","054","057","061"]}}` |
| `audienceAgeFrom` | nein | `{"type":"integer","minimum":0}` |
| `audienceAgeTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `audienceDominantGender` | nein | `{"type":"string","enum":["male","female","balanced"]}` |
| `audienceDominantIncome` | nein | `{"type":"array","items":{"type":"string","enum":["low","middle","upper_middle","high"]}}` |
| `detectionsMonetization` | nein | `{"type":"array","items":{"type":"string","enum":["adsense","sponsored","affiliate","product","donations","course","newsletter","community","services"]}}` |
| `detectionsMadeWithAI` | nein | `{"type":"boolean"}` |
| `detectionsForKids` | nein | `{"type":"boolean"}` |
| `terminated` | nein | `{"type":"boolean"}` |

### GET `/v1/search/channels/related`

| Parameter | Pflicht | Vollständiges Werteschema |
| --- | --- | --- |
| `from` | nein | `{"type":"integer","minimum":0}` |
| `size` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `filterBy` | nein | `{"type":"string","enum":["video","short"]}` |
| `contentKind` | nein | `{"type":"string","enum":["video","short","long-form","short-form"]}` |
| `publishedAtFrom` | nein | `{"type":"string"}` |
| `publishedAtTo` | nein | `{"type":"string"}` |
| `averageViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `averageViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `medianViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `medianViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `language` | nein | `{"type":"array","items":{"type":"string"}}` |
| `avgViewsToSubscribersRatioFrom` | nein | `{"type":"number","minimum":0}` |
| `avgViewsToSubscribersRatioTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `subscribersFrom` | nein | `{"type":"integer","minimum":0}` |
| `subscribersTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `videosCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `videosCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `viewVariationCoefficientFrom` | nein | `{"type":"number","minimum":0}` |
| `viewVariationCoefficientTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `revenueMonthlyEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `revenueMonthlyEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `rpmEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `rpmEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `avgDurationFrom` | nein | `{"type":"integer","minimum":0}` |
| `avgDurationTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `monetizationAdsense` | nein | `{"type":"boolean"}` |
| `monetizationSponsored` | nein | `{"type":"boolean"}` |
| `monetizationChanged` | nein | `{"type":"boolean"}` |
| `excludeNiche` | nein | `{"type":"array","items":{"type":"string"}}` |
| `referenceId` | nein | `{"type":"string"}` |
| `classificationQuality` | nein | `{"type":"string","enum":["negative","neutral","positive"]}` |
| `classificationIsFaceless` | nein | `{"type":"boolean"}` |
| `classificationIsOnCamera` | nein | `{"type":"boolean"}` |
| `joinedDateFrom` | nein | `{"type":"string"}` |
| `viewCountAllTimeFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewCountAllTimeTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `viewsPerHourEstimateFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewsPerHourEstimateTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `audienceRegion` | nein | `{"type":"array","items":{"type":"string","enum":["015","011","017","014","018","021","029","013","005","143","030","035","034","145","151","154","039","155","053","054","057","061"]}}` |
| `audienceAgeFrom` | nein | `{"type":"integer","minimum":0}` |
| `audienceAgeTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `audienceDominantGender` | nein | `{"type":"string","enum":["male","female","balanced"]}` |
| `audienceDominantIncome` | nein | `{"type":"array","items":{"type":"string","enum":["low","middle","upper_middle","high"]}}` |
| `detectionsMonetization` | nein | `{"type":"array","items":{"type":"string","enum":["adsense","sponsored","affiliate","product","donations","course","newsletter","community","services"]}}` |
| `detectionsMadeWithAI` | nein | `{"type":"boolean"}` |
| `detectionsForKids` | nein | `{"type":"boolean"}` |
| `terminated` | nein | `{"type":"boolean"}` |
| `relatedChannelId` | ja | `{"type":"array","items":{"type":"string"}}` |
| `relatedChannelTerminated` | nein | `{"type":"boolean"}` |

### GET `/v1/search/outliers`

| Parameter | Pflicht | Vollständiges Werteschema |
| --- | --- | --- |
| `from` | nein | `{"type":"integer","minimum":0}` |
| `size` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `by` | nein | `{"type":"string","enum":["semantic","lexical"]}` |
| `query` | nein | `{"type":"array","items":{"type":"string"}}` |
| `seed` | nein | `{"type":"string"}` |
| `sortBy` | nein | `{"type":"string","enum":["views","zScore","averageViewsRatio","publishedAt","revenue","rpm"]}` |
| `sortOrder` | nein | `{"type":"string","enum":["asc","desc"]}` |
| `type` | nein | `{"type":"string","enum":["video","short"]}` |
| `averageViewsRatioFrom` | nein | `{"type":"number"}` |
| `averageViewsRatioTo` | nein | `{"type":"number"}` |
| `zScoreFrom` | nein | `{"type":"number"}` |
| `zScoreTo` | nein | `{"type":"number"}` |
| `viewCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `language` | nein | `{"type":"array","items":{"type":"string"}}` |
| `durationFrom` | nein | `{"type":"integer","minimum":0}` |
| `durationTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `publishedAtFrom` | nein | `{"type":"string"}` |
| `publishedAtTo` | nein | `{"type":"string"}` |
| `subscribersCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `subscribersCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `channelAvgViewsFrom` | nein | `{"type":"number","minimum":0}` |
| `channelAvgViewsTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `channelVideoCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `channelVideoCountTo` | nein | `{"type":"integer","maximum":120,"exclusiveMinimum":0}` |
| `channelId` | nein | `{"type":"string"}` |
| `channelAvgViewsToSubscribersRatioFrom` | nein | `{"type":"number","minimum":0}` |
| `channelAvgViewsToSubscribersRatioTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `titlePattern` | nein | `{"type":"string"}` |
| `sentiment` | nein | `{"type":"string"}` |
| `subSentiment` | nein | `{"type":"string"}` |
| `referenceId` | nein | `{"type":"string"}` |
| `rpmEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `rpmEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `revenueEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `revenueEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `channelMonetizationAdsense` | nein | `{"type":"boolean"}` |
| `channelMonetizationSponsored` | nein | `{"type":"boolean"}` |
| `classificationQuality` | nein | `{"type":"string","enum":["negative","neutral","positive"]}` |
| `classificationIsFaceless` | nein | `{"type":"boolean"}` |
| `excludeKeyword` | nein | `{"type":"array","items":{"type":"string"}}` |

### GET `/v1/search/outliers/related`

| Parameter | Pflicht | Vollständiges Werteschema |
| --- | --- | --- |
| `from` | nein | `{"type":"integer","minimum":0}` |
| `size` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `by` | nein | `{"type":"string","enum":["semantic","lexical"]}` |
| `title` | nein | `{"type":"array","items":{"type":"string"}}` |
| `videoId` | nein | `{"type":"array","items":{"type":"string"}}` |
| `thumbnailVideoId` | nein | `{"type":"string"}` |
| `relatedChannelId` | nein | `{"type":"array","items":{"type":"string"}}` |
| `type` | nein | `{"type":"string","enum":["video","short"]}` |
| `averageViewsRatioFrom` | nein | `{"type":"number"}` |
| `averageViewsRatioTo` | nein | `{"type":"number"}` |
| `zScoreFrom` | nein | `{"type":"number"}` |
| `zScoreTo` | nein | `{"type":"number"}` |
| `viewCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `viewCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `language` | nein | `{"type":"array","items":{"type":"string"}}` |
| `durationFrom` | nein | `{"type":"integer","minimum":0}` |
| `durationTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `publishedAtFrom` | nein | `{"type":"string"}` |
| `publishedAtTo` | nein | `{"type":"string"}` |
| `subscribersCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `subscribersCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `channelAvgViewsFrom` | nein | `{"type":"number","minimum":0}` |
| `channelAvgViewsTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `channelVideoCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `channelVideoCountTo` | nein | `{"type":"integer","maximum":120,"exclusiveMinimum":0}` |
| `channelId` | nein | `{"type":"string"}` |
| `channelAvgViewsToSubscribersRatioFrom` | nein | `{"type":"number","minimum":0}` |
| `channelAvgViewsToSubscribersRatioTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `titlePattern` | nein | `{"type":"string"}` |
| `sentiment` | nein | `{"type":"string"}` |
| `subSentiment` | nein | `{"type":"string"}` |
| `referenceId` | nein | `{"type":"string"}` |
| `rpmEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `rpmEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `revenueEstimationFrom` | nein | `{"type":"number","minimum":0}` |
| `revenueEstimationTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `channelMonetizationAdsense` | nein | `{"type":"boolean"}` |
| `channelMonetizationSponsored` | nein | `{"type":"boolean"}` |
| `classificationQuality` | nein | `{"type":"string","enum":["negative","neutral","positive"]}` |
| `classificationIsFaceless` | nein | `{"type":"boolean"}` |
| `excludeKeyword` | nein | `{"type":"array","items":{"type":"string"}}` |

### GET `/v1/search/trending-formats`

| Parameter | Pflicht | Vollständiges Werteschema |
| --- | --- | --- |
| `from` | nein | `{"type":"integer","minimum":0}` |
| `size` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `sortBy` | nein | `{"type":"string","enum":["averageViews","averageViewsRatio","videosCount","avgDuration","foundAt","lastAverageViewsChangePercentage","lastMedianViewsChangePercentage","lastAvgViewsRatioChangePercentage","lastVideosCountChangePercentage"]}` |
| `sortOrder` | nein | `{"type":"string","enum":["asc","desc"]}` |
| `query` | nein | `{"type":"array","items":{"type":"string"}}` |
| `seed` | nein | `{"type":"string"}` |
| `averageViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `averageViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `medianViewsFrom` | nein | `{"type":"integer","minimum":0}` |
| `medianViewsTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `language` | nein | `{"type":"string"}` |
| `averageViewsRatioFrom` | nein | `{"type":"number","minimum":0}` |
| `averageViewsRatioTo` | nein | `{"type":"number","exclusiveMinimum":0}` |
| `videosCountFrom` | nein | `{"type":"integer","minimum":0}` |
| `videosCountTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `avgDurationFrom` | nein | `{"type":"integer","minimum":0}` |
| `avgDurationTo` | nein | `{"type":"integer","exclusiveMinimum":0}` |
| `referenceId` | nein | `{"type":"string"}` |
| `quality` | nein | `{"type":"string","enum":["positive","negative","neutral"]}` |
| `clickTrigger` | nein | `{"type":"array","items":{"type":"string"}}` |
| `createdAtFrom` | nein | `{"type":"string"}` |
| `lastVideosCountChangePercentageFrom` | nein | `{"type":"number"}` |
| `lastVideosCountChangePercentageTo` | nein | `{"type":"number"}` |
| `lastAvgViewsRatioChangePercentageFrom` | nein | `{"type":"number"}` |
| `lastAvgViewsRatioChangePercentageTo` | nein | `{"type":"number"}` |


## 14. Vollständige lokale Parameter und POST-Bodys

| Route | Parameter / Body |
| --- | --- |
| GET `/v1/jobs` | `limit`:1..100, Standard25; `offset`: nichtnegative sichere Ganzzahl, Standard0; `state`: `queued`, `running`, `succeeded`, `failed`. Andere Querynamen422. |
| GET `/v1/scans` | `limit`:1..200, Standard50; `offset`: nichtnegative Ganzzahl, Standard0; `state`: `pending`, `submitted`, `uncertain`, `completed`, `failed`. Lokaler Bestand, keine Provider-Suche. |
| POST `/v1/scan` | JSON `query`:1..20 nichtleere Texte mit jeweils höchstens200 Zeichen; `mode`: `fast` oder `standard`, Standard `fast`; `findBy`: nur `query`, Standard `query`; optional `webhookUrl`: HTTPS-URL mit serverseitig erlaubtem Host. Derzeit stets501 nach gültiger Eingabe; keine neuen Scans. |
| POST `/v1/session/import` | JSON `curl` oder `cookies`; optional `userAgent`, `csrf`. Andere Eigenschaften422. Browser-Basic: erlaubter Origin und gültiger CSRF-Token nötig. JSON-Limit100KB. |
| POST `/v1/login-ticket` | Kein Body erforderlich. API-Key-Header nötig. |
| POST `/connect/redeem` | JSON ausschließlich `ticket`, `csrf`; Origin/CSRF aus Portal. |
| POST `/connect/verify` | JSON ausschließlich `link`, `csrf`; aktiver mobiler Cookie, exakter Origin, gültiger CSRF-Token. |
| POST `/connect/capture` | JSON ausschließlich `csrf`; aktiver mobiler Cookie, exakter Origin, gültiger CSRF-Token. |

Für normale REST-Aufrufe ist Basic nicht zugelassen; die ausdrücklich genannten Browser-/Import-Routen sind die Ausnahme. Der eigene API-Key braucht keine zusätzlichen Rollen. Provider-Sitzung und Ressourcenverfügbarkeit werden getrennt geprüft.
