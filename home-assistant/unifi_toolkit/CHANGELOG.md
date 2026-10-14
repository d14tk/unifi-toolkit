# Changelog

## 1.13.2-2

- Deutsche Oberfläche: rund 1300 Texte aus Templates, JS und den API-Antworten übersetzt
- Umschalter Deutsch/English im Einstellungsdialog (Zahnrad), pro Browser gespeichert
- Neue Option `language` für die Standardsprache (Standard: `de`)

## 1.13.2-1

- Backend lauscht nur noch auf 127.0.0.1, Direktzugriff über Port 8000 entfällt
- nginx: `absolute_redirect off`, damit Slash-Redirects unter Ingress funktionieren
- run.sh reicht SIGTERM an nginx und App weiter und beendet beide sauber

## 1.13.2

- Erste Version der App, basiert auf dem Upstream-Image `ghcr.io/crosstalk-solutions/unifi-toolkit:1.13.2`
- Ingress mit nginx-Pfad-Umschreibung, Seitenleisten-Panel
- ENCRYPTION_KEY wird beim ersten Start erzeugt und in `/data` abgelegt
