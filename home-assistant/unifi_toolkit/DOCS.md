# UniFi Toolkit

## Einrichtung

1. App starten, dann **UniFi Toolkit** in der Seitenleiste öffnen.
2. Über das Zahnrad im Dashboard den Controller eintragen:
   - Controller URL: lokale Adresse der UniFi-OS-Konsole, z. B. `https://192.168.1.1`
   - API-Key (empfohlen, in UniFi OS unter *Settings → Admins* erzeugen) oder Benutzer und Passwort
   - Site ID: `default`, sofern nicht anders
   - Verify SSL aus lassen bei selbstsigniertem Zertifikat
3. *Test Connection*, dann *Save*.

Unterstützt werden nur UniFi-OS-Konsolen (UDM, UCG, Cloud Key Gen2+), kein eigenständiger Network-Controller.

## Optionen

| Option | Bedeutung |
|---|---|
| `language` | Standardsprache der Oberfläche (`de` oder `en`) |
| `log_level` | Log-Level der App |
| `stalker_refresh_interval` | Abfrageintervall des Wi-Fi Stalker in Sekunden |

## Sprache

Die Oberfläche ist auf Deutsch übersetzt. Umschalten geht im Dashboard über das Zahnrad (Einstellungen) → *Sprache / Language*. Die Wahl gilt pro Browser; ohne Wahl gilt die Option `language`.

Die Upstream-App hat keine Übersetzungen. Ein Skript (`rootfs/etc/nginx/ha-i18n/i18n.js`), das nginx in jede Seite einhängt, ersetzt bekannte englische Texte anhand von `de.json`, auch in nachgeladenen Inhalten. Diagrammbeschriftungen (Canvas) und Texte, die erst nach einem Upstream-Update neu dazukommen, bleiben englisch, bis `de.json` ergänzt ist (siehe `i18n/` im Repo).

## Daten und Sicherheit

- Datenbank (`unifi_toolkit.db`) und Schlüssel (`encryption_key`) liegen in `/data` und sind im HA-Backup enthalten.
- Der Schlüssel verschlüsselt die Controller-Zugangsdaten. Fehlt er, muss der Controller neu eingetragen werden.
- Zugriff nur über Ingress, also nur für angemeldete HA-Benutzer. House Arrest kann Firewall-Regeln auf der UniFi-Konsole anlegen, deshalb den Seitenleisten-Eintrag bei Bedarf auf Admins beschränken.
- Die App selbst lauscht nur auf `127.0.0.1`. Einziger Zugang ist nginx auf dem Ingress-Port, der nur Anfragen vom Supervisor-Ingress (`172.30.32.2`) annimmt.

## Technik

Die Upstream-App kennt keinen Basis-Pfad. Ein nginx vor der App schreibt absolute Pfade in HTML, JS und CSS auf den Ingress-Pfad um (`rootfs/etc/nginx/nginx.conf`). Nach einem Upstream-Update prüfen, ob neue Pfad-Präfixe dazugekommen sind.
