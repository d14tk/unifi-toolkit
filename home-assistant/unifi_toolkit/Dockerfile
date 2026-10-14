# Upstream-Image (multi-arch amd64/arm64), Version synchron zu config.yaml halten
FROM ghcr.io/crosstalk-solutions/unifi-toolkit:1.13.2

# Supervisor mountet /data als root
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx jq \
    && rm -rf /var/lib/apt/lists/* /etc/nginx/sites-enabled/default

# Backend nur auf Loopback: ohne Login (local mode) darf ausser nginx niemand ran.
# grep laesst den Build scheitern, falls Upstream die Zeile aendert.
RUN sed -i 's/host="0.0.0.0"/host="127.0.0.1"/' /app/run.py \
    && grep -q 'host="127.0.0.1"' /app/run.py

COPY rootfs /
RUN chmod +x /run.sh \
    && python -c "import json; d = json.load(open('/etc/nginx/ha-i18n/de.json', encoding='utf-8')); open('/etc/nginx/ha-i18n/de.js', 'w', encoding='utf-8').write('window.HA_I18N_DE = ' + json.dumps(d, ensure_ascii=False) + ';')"

WORKDIR /app
CMD ["/run.sh"]
