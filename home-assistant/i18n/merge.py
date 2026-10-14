"""Fuehrt Uebersetzungsdateien ({en: de}) in unifi_toolkit/rootfs/etc/nginx/ha-i18n/de.json zusammen.

Aufruf: python -I i18n/merge.py <uebersetzung.json> [...]
Leere Werte und unveraenderte Texte werden verworfen, ebenso Eintraege, deren
${...}-Platzhalter im Deutschen nicht exakt zum Englischen passen.
"""
import json
import os
import re
import sys

TARGET = os.path.join(os.path.dirname(__file__), '..', 'unifi_toolkit', 'rootfs', 'etc', 'nginx', 'ha-i18n', 'de.json')
BS = chr(92)
HOLDER = re.compile(r'\$\{[^}]*\}')


JS_ESCAPE = re.compile(r'\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)', re.S)
SIMPLE = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v', '0': '\0'}


def unescape(s):
    """JS-Escapes aus extrahierten Literalen aufloesen (\\' \\" \\n \\u2026 \\u{1F512} ...)."""
    def repl(m):
        e = m.group(1)
        if e.startswith('u{'):
            return chr(int(e[2:-1], 16))
        if e[0] in 'ux' and len(e) > 1:
            return chr(int(e[1:], 16))
        return SIMPLE.get(e, e)
    return JS_ESCAPE.sub(repl, s) if BS in s else s


def main(paths):
    out = json.load(open(TARGET, encoding='utf-8')) if os.path.exists(TARGET) else {}
    rejected = []
    for path in paths:
        for en, de in json.load(open(path, encoding='utf-8')).items():
            if not de:
                continue
            en, de = unescape(en), unescape(de)
            if sorted(HOLDER.findall(en)) != sorted(HOLDER.findall(de)):
                rejected.append(en)
                continue
            if en.strip() != de.strip():
                out[en] = de
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(sorted(out.items())), f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{len(out)} Eintraege, {len(rejected)} verworfen (Platzhalter)')
    for en in rejected:
        print('  verworfen:', en.encode('ascii', 'replace').decode())


if __name__ == '__main__':
    main(sys.argv[1:])
