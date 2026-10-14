# Übersetzung pflegen

Nach einem Upstream-Update:

1. Upstream im passenden Tag auschecken (`git clone --branch vX.Y.Z https://github.com/Crosstalk-Solutions/unifi-toolkit`).
2. Texte extrahieren: `python -I i18n/extract.py <upstream> strings.json` (Templates, JS-Literale, Python-Strings).
3. Neue Schlüssel gegen `home-assistant/unifi_toolkit/rootfs/etc/nginx/ha-i18n/de.json` abgleichen und als `{en: de}` übersetzen. Nicht sichtbare Texte auf `""` setzen.
4. Einspielen: `python -I i18n/merge.py <uebersetzung.json>`. Das Skript verwirft Einträge, deren `${...}`-Platzhalter nicht passen.

`${...}` steht für dynamische Teile. Hat ein Muster kaum festen Text (z. B. `${secs}s`), akzeptiert die Laufzeit an dieser Stelle nur Zahlen.
