# TubeLab Web API

Eigene REST-API für eine angemeldete TubeLab-Websitzung, mit persistenter Queue, geschütztem Aktivitäts-Dashboard und optionalem Login-Browser.

Die veröffentlichten Images enthalten keine Anmeldung. Jede Installation bekommt eigene Schlüssel und benötigt ein eigenes TubeLab-Konto. Der Recherche-Agent verwendet den eigenen API-Key dieser Installation. Admin-Passwort und Provider-Anmeldung sind getrennt.

## Fertige Images verwenden

Plattform des geprüften Release-Archivs: **linux/amd64**. Docker unter Linux oder Docker Desktop mit Linux-Containern nötig.

1. Release-Datei `TubeLab-Images-2026.10.09-linux-amd64.tar.gz`, `SHA256SUMS` und die Konfigurationsdateien herunterladen.
2. In einem neuen Verzeichnis ablegen und prüfen/laden:

```bash
sha256sum -c SHA256SUMS
docker load --input TubeLab-Images-2026.10.09-linux-amd64.tar.gz
cp .env.example .env
sudo python3 prepare.py
docker compose up -d
```

Auf Windows `python prepare.py` statt `sudo python3 prepare.py`. Private Verzeichnisse vor Zugriff durch andere Benutzer schützen. Keine bereits angemeldeten Datenverzeichnisse anderer Installationen übernehmen.

3. API-Dokumentation: http://127.0.0.1:8086/docs; Dashboard: http://127.0.0.1:8086/dashboard. Benutzer `admin`; Passwort das in `prepare.py` selbst gesetzte Passwort oder der selbst erzeugte API-Key.
4. Den eigenen Schlüssel lokal aus `data/api-key` lesen. Anfragen senden `Authorization: Api-Key <eigener Schlüssel>`, alternativ Bearer oder X-API-Key. Kein Key in URLs.
5. Für die einfache lokale Installation über `/session/import` einen erfolgreichen TubeLab-Copy-as-cURL-Request der **eigenen** Anmeldung importieren. Das ist eine private Adminaktion; nicht in das Repository hochladen.

## GitHub Container Registry verwenden

Sobald die Packages dieses Repositorys veröffentlicht sind, deren Namespace in `.env-ghcr.example` einsetzen und als `.env` speichern. Danach `docker compose pull` und `docker compose up -d` ausführen. Für öffentliche Packages ist kein GitHub-Login zum Pull nötig; private Packages brauchen freigegebenen Zugriff. Der GitHub-Registry-Zugang ist unabhängig vom eigenen TubeLab-API-Key.

## Eigener Browser-Login auf einem Server

Für den mobilen Login eine eigene HTTPS-Domain mit Reverseproxy zu `127.0.0.1:8086` einrichten. `PUBLIC_ORIGIN` in `.env` auf diese HTTPS-URL setzen; Schluessel und Admin-Passwort ausschliesslich im privaten Datenverzeichnis speichern.

```bash
sudo python3 prepare.py
docker compose -f compose.yml -f compose.browser.yml up -d
```

Dann authentifiziert `POST /v1/login-ticket` ausführen und den zurückgegebenen privaten Einmallink selbst öffnen. Im Serverbrowser am eigenen TubeLab-Konto anmelden, gegebenenfalls den E-Mail-Bestätigungslink im Portal einfügen, danach **Sitzung übernehmen**. `GET /v1/session` muss `authenticated:true` melden. Die Browserports sind nur im privaten Docker-Netz erreichbar.

## Recherche und Queue

- Standard: ein Worker,1000 offene Jobs,1s Startabstand. Bei HTTP202 die zurückgegebene `resultUrl` pollen; keine erneute Suchanfrage erzeugen.
- Alle Befehle,207 Suchparameter, Fehlercodes und Login-Routen: [API.md](API.md).
- `video.transcript` und allgemeines `scan.create` sind aktuell501. Vorhandene Scan-Prozess-ID erforderlich für `scan.get`; dieser Aufruf ist noch nicht live bestätigt.
- Eigene Cookie-Sitzung kann ablaufen. Gemessener0-Credit-Verbrauch bei früheren Suchprüfungen ist keine dauerhafte Kostenfrei-Garantie.


## GitHub-Veröffentlichung

Der Workflow importiert exakt das geprüfte Docker-Image-Archiv aus dem GitHub-Release und veröffentlicht beide Images bei GitHub Container Registry. SHA256SUMS wird vor dem Import geprüft. Keine Produktionsvolumes, angemeldeten Browserprofile oder TubeLab-Zugangsdaten werden übernommen.

Release-Tag: v2026.10.09. GitHub-Packages sind beim ersten Push standardmäßig privat; Package-Sichtbarkeit und Pull-Zugriff separat kontrollieren.

Offizielle Hinweise: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

Private Dateien data/, browser-data/ und .env niemals committen oder als Release anhängen.
