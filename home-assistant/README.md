# UniFi Toolkit für Home Assistant

Dieser Fork ergänzt das [UniFi Toolkit](https://github.com/Crosstalk-Solutions/unifi-toolkit) um eine Home-Assistant-App (Add-on), eine HACS-Integration als Installer und eine deutsche Oberfläche. Der Code der Anwendung selbst bleibt unverändert, die App nutzt das offizielle Image `ghcr.io/crosstalk-solutions/unifi-toolkit`.

Nicht verbunden mit Ubiquiti oder Crosstalk Solutions.

## Installation

### Über HACS

HACS kann keine Apps installieren. Die Integration in `custom_components/unifi_toolkit` übernimmt das:

1. HACS → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/d14tk/unifi-toolkit`, Typ *Integration*
2. *UniFi Toolkit* herunterladen, Home Assistant neu starten
3. *Einstellungen → Geräte & Dienste → Integration hinzufügen → UniFi Toolkit*

Die Integration registriert dieses Repository im App-Store, installiert die App, schaltet Seitenleiste und Watchdog ein und startet sie.

### Ohne HACS

[![Repository hinzufügen](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fd14tk%2Funifi-toolkit)

Danach *UniFi Toolkit* im App-Store installieren und starten.

## Was die App macht

- Läuft über Ingress in der HA-Seitenleiste, die Anmeldung übernimmt Home Assistant. Die Anwendung lauscht nur auf `127.0.0.1`, einziger Zugang ist nginx auf dem Ingress-Port.
- nginx schreibt die absoluten Pfade der Anwendung auf den Ingress-Pfad um, weil Upstream keinen Basis-Pfad unterstützt.
- Deutsche Oberfläche mit Umschalter Deutsch/English im Einstellungsdialog (Zahnrad). Standardsprache über die App-Option `language`.
- Datenbank und Schlüssel für die Controller-Zugangsdaten liegen in `/data` und sind im HA-Backup enthalten.

Details: [`home-assistant/unifi_toolkit/DOCS.md`](unifi_toolkit/DOCS.md). Übersetzung pflegen: [`home-assistant/i18n/README.md`](i18n/README.md).

## Aufbau

| Pfad | Inhalt |
|---|---|
| `repository.yaml` | App-Store-Repository für den Supervisor |
| `home-assistant/unifi_toolkit/` | Die App (Dockerfile, nginx, Übersetzung) |
| `home-assistant/i18n/` | Werkzeuge zum Extrahieren und Einspielen von Übersetzungen |
| `custom_components/unifi_toolkit/`, `hacs.json` | HACS-Integration (Installer) |
