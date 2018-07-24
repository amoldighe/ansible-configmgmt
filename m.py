alert-manager/                                                                                      0000755 0000000 0000000 00000000000 13324130704 012270  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   alert-manager/alertmanager.yml                                                                      0000644 0000000 0000000 00000002634 13324130017 015457  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   global:
  resolve_timeout: 5m

route:
  receiver: default
  group_by:
  - region
  - service
  group_interval: 5m
  group_wait: 60s
  repeat_interval: 3h
  routes:
  # alerta
  - receiver: Alerta
    continue: True
  # slack
  - receiver: HTTP-slack
    continue: True
    match_re:
      severity: critical|down
  # email
  - receiver: SMTP
    continue: True
    match_re:
      severity: critical|down|warning

inhibit_rules:
  # InhibitWarningWhenDown
  - source_match:
      severity: down
    target_match:
      severity: warning
    equal:
    - region
    - service
  # InhibitWarningWhenCritical
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal:
    - region
    - service
  # InhibitCriticalWhenDown
  - source_match:
      severity: down
    target_match:
      severity: critical
    equal:
    - region
    - service

receivers:
  - name: 'default'
  - name: 'HTTP-slack'
    slack_configs:
    # slack-endpoint
    - api_url: https://hooks.slack.com/services/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
      send_resolved: true
  - name: 'SMTP'
    email_configs:
    # smtp_server
    - to: JioJAWS.Tools@ril.com
      from: alerts.jpe4@ril.com
      smarthost: 10.142.240.27:25
      require_tls: false
      send_resolved: true
  - name: 'Alerta'
    webhook_configs:
    # alerta-vip
    - url: http://10.157.0.42:9080/api/webhooks/prometheus
      send_resolved: true
                                                                                                    compose/                                                                                            0000755 0000000 0000000 00000000000 13275561540 011231  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   compose/monitoring/                                                                                 0000755 0000000 0000000 00000000000 13324131776 013415  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   compose/monitoring/docker-compose.yml                                                               0000644 0000000 0000000 00000013301 13301523754 017044  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   version: '3'

services:
  alertmanager:
    deploy:
      labels:
        com.mirantis.monitoring: alertmanager
      replicas: 2
      restart_policy:
        condition: any
    environment:
      ALERTMANAGER_BIND_ADDRESS: 0.0.0.0
      ALERTMANAGER_BIND_PORT: 9093
      ALERTMANAGER_CONFIG_DIR: /srv/alertmanager
      ALERTMANAGER_DATA_DIR: /data
      ALERTMANAGER_DISCOVERY_DOMAIN: monitoring_alertmanager
      ALERTMANAGER_EXTERNAL_URL: http://10.157.0.42:15011
      HTTPS_PROXY: http://10.144.106.132:8678
      NO_PROXY: 127.0.0.1,localhost,10.157.0.42,10.157.0.43,10.157.0.44,10.157.0.45
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/alertmanager:2018.3.1
    labels:
      com.mirantis.monitoring: alertmanager
    networks:
    - monitoring
    ports:
    - 15011:9093
    volumes:
    - /srv/volumes/local/alertmanager/config:/srv/alertmanager
    - /srv/volumes/local/alertmanager/data:/data
  relay:
    deploy:
      labels:
        com.mirantis.monitoring: relay
      replicas: 2
      restart_policy:
        condition: any
    environment:
      PROMETHEUS_RELAY_DNS: tasks.monitoring_server
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/prometheus_relay:2018.3.1
    labels:
      com.mirantis.monitoring: relay
    networks:
    - monitoring
    ports:
    - 15016:8080
  mongodb:
    deploy:
      labels:
        com.mirantis.monitoring: mongo
      restart_policy:
        condition: any
    image: mongo
    networks:
    - monitoring
    ports:
    - 27017:27017
    volumes:
    - /srv/volumes/mongo:/data/db
  remote_collector:
    deploy:
      labels:
        com.mirantis.monitoring: remote_collector
      replicas: 1
      restart_policy:
        condition: any
    environment:
      HEKA_CACHE_DIR: /var/cache/remote_collector
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/heka:2018.3.1
    labels:
      com.mirantis.monitoring: remote_collector
    networks:
    - monitoring
    volumes:
    - /srv/volumes/local/remote_collector/etc/remote_collector:/etc/heka
    - /srv/volumes/local/remote_collector/usr/share/lma_collector:/usr/share/lma_collector
  server:
    deploy:
      labels:
        com.mirantis.monitoring: prometheus
      mode: global
      restart_policy:
        condition: any
    environment:
      PROMETHEUS_BIND_ADDRESS: 0.0.0.0
      PROMETHEUS_BIND_PORT: 9090
      PROMETHEUS_CONFIG_DIR: /srv/prometheus
      PROMETHEUS_DATA_DIR: /data
      PROMETHEUS_EXTERNAL_URL: http://10.157.0.42:15010
      PROMETHEUS_STORAGE_LOCAL_ENGINE: persisted
      PROMETHEUS_STORAGE_LOCAL_NUM_FINGERPRINT_MUTEXES: 4096
      PROMETHEUS_STORAGE_LOCAL_RETENTION: 360h
      PROMETHEUS_STORAGE_LOCAL_TARGET_HEAP_SIZE: 3221225472
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/prometheus@sha256:16b512f64a3633eecc15970a26482bc1ee861defec71119f8de73047735d87a0
    labels:
      com.mirantis.monitoring: prometheus
    networks:
    - monitoring
    ports:
    - 15010:9090
    volumes:
    - /srv/volumes/local/prometheus/config:/srv/prometheus
    - /srv/volumes/local/prometheus/data:/data
  remote_agent:
    deploy:
      labels:
        com.mirantis.monitoring: remote_agent
      replicas: 1
      restart_policy:
        condition: any
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/telegraf:2018.3.1
    labels:
      com.mirantis.monitoring: remote_agent
    networks:
    - monitoring
    ports:
    - 15014:9126
    volumes:
    - /srv/volumes/local/telegraf:/etc/telegraf
    - /srv/volumes/local/telegraf/telegraf.d:/etc/telegraf/telegraf.d
  pushgateway:
    deploy:
      labels:
        com.mirantis.monitoring: pushgateway
      replicas: 2
      restart_policy:
        condition: any
    environment:
      PUSHGATEWAY_BIND_ADDRESS: 0.0.0.0
      PUSHGATEWAY_BIND_PORT: 9091
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/pushgateway:2018.3.1
    labels:
      com.mirantis.monitoring: pushgateway
    networks:
    - monitoring
    ports:
    - 15012:9091
  alerta:
    depends_on:
    - mongodb
    deploy:
      labels:
        com.mirantis.monitoring: alerta
      restart_policy:
        condition: any
    environment:
      ADMIN_USERS: root@test.com
      ALERTMANAGER_API_URL: http://10.157.0.42:15011
      ALLOWED_EMAIL_DOMAIN: '*'
      ALLOWED_ENVIRONMENTS: Production,Development
      ALLOWED_GITHUB_ORGS: '*'
      ALLOWED_GITLAB_GROUPS: '*'
      AUTH_REQUIRED: 'False'
      CLIENT_ID: not-set
      CLIENT_SECRET: not-set
      CUSTOMER_VIEWS: 'False'
      GITLAB_URL: not-set
      HTTPS_PROXY: http://10.144.106.132:8678
      INSTALL_PLUGINS: reject,prometheus
      MONGO_URI: mongodb://10.157.0.42:27017/monitoring
      NO_PROXY: 127.0.0.1,localhost,10.157.0.42,10.157.0.43,10.157.0.44,10.157.0.45
      ORIGIN_BLACKLIST: not-set
      PLUGINS: reject,prometheus
      PROVIDER: basic
    image: alerta/alerta-web:5.1.1
    labels:
      com.mirantis.monitoring: alerta
    networks:
    - monitoring
    ports:
    - 9080:8080
  remote_storage_adapter:
    deploy:
      labels:
        com.mirantis.monitoring: remote_storage_adapter
      replicas: 1
      restart_policy:
        condition: any
    environment:
      RSA_BIND_ADDRESS: 0.0.0.0
      RSA_BIND_PORT: 9201
      RSA_INFLUXDB_DB: prometheus
      RSA_INFLUXDB_PASSWORD: MD5e1WuZUny6grQ9
      RSA_INFLUXDB_RETENTION_POLICY: lma
      RSA_INFLUXDB_URL: http://10.157.0.50:8086/
      RSA_INFLUXDB_USERNAME: lma
    image: docker-prod-local.artifactory.mirantis.com/openstack-docker/remote_storage_adapter:2018.3.1
    labels:
      com.mirantis.monitoring: remote_storage_adapter
    networks:
    - monitoring
    ports:
    - 15015:9201
networks:
  monitoring:
    driver: overlay
    driver_opts:
      encrypted: 1
                                                                                                                                                                                                                                                                                                                               compose/dashboard/                                                                                  0000755 0000000 0000000 00000000000 13324131741 013147  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   compose/dashboard/docker-compose.yml                                                                0000644 0000000 0000000 00000000643 13300765444 016616  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   version: '3'

services:
  grafana:
    deploy:
      replicas: 1
      restart_policy:
        condition: any
    environment:
      GF_DATABASE_HOST: 10.157.0.34:3306
      GF_DATABASE_NAME: grafana
      GF_DATABASE_PASSWORD: ajEGVDANkTdX5e2R
      GF_DATABASE_TYPE: mysql
      GF_DATABASE_USER: grafana
      GF_SECURITY_ADMIN_PASSWORD: bT7wFqaLTFizZOxq
    image: grafana/grafana:4.5.2
    ports:
    - 15013:3000
                                                                                             prometheus/                                                                                         0000755 0000000 0000000 00000000000 13324060561 011747  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   prometheus/prometheus.yml                                                                           0000644 0000000 0000000 00000164164 13324060561 014701  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   global:
  evaluation_interval: 15s
  external_labels:
    region: jpe4
  scrape_interval: 15s
  scrape_timeout: 15s
alerting:
  alertmanagers:
    # docker_swarm_alertmanager
    - dns_sd_configs:
      - names: [tasks.monitoring_alertmanager]
        type: A
        port: 9093
remote_write:
  # docker_remote_write
  - url: http://monitoring_remote_storage_adapter:9201/write

rule_files:
- alerts.yml

scrape_configs:
  - job_name: telegraf
    scheme: http
    metrics_path: /metrics
    honor_labels: False
    scrape_interval: 15s
    scrape_timeout: 15s
    static_configs:
    - targets: ['192.168.15.66:9126','10.157.1.92:9126','192.168.14.127:9126','192.168.14.144:9126','10.157.1.98:9126','10.157.0.226:9126','10.157.1.42:9126','10.157.0.161:9126','10.157.1.30:9126','192.168.15.73:9126','10.157.0.69:9126','10.157.0.20:9126','10.157.1.90:9126','192.168.14.128:9126','10.157.0.25:9126','192.168.15.72:9126','10.157.0.79:9126','10.157.0.100:9126','192.168.14.206:9126','192.168.14.134:9126','10.157.0.115:9126','10.157.1.81:9126','192.168.14.145:9126','192.168.14.76:9126','10.157.0.159:9126','10.157.1.103:9126','192.168.15.15:9126','10.157.0.224:9126','192.168.9.112:9126','192.168.15.64:9126','192.168.15.6:9126','192.168.14.146:9126','10.157.1.34:9126','10.157.1.94:9126','10.157.1.12:9126','10.157.1.39:9126','192.168.9.72:9126','10.157.0.215:9126','192.168.15.3:9126','192.168.9.52:9126','192.168.14.225:9126','10.157.0.203:9126','10.157.0.52:9126','10.157.1.87:9126','10.157.0.243:9126','10.157.0.128:9126','10.157.0.170:9126','10.157.0.234:9126','192.168.14.147:9126','10.157.1.80:9126','192.168.9.110:9126','10.157.1.91:9126','10.157.0.27:9126','10.157.1.10:9126','192.168.14.229:9126','192.168.9.109:9126','10.157.0.245:9126','192.168.14.75:9126','192.168.15.14:9126','192.168.15.90:9126','192.168.8.206:9126','10.157.1.165:9126','192.168.8.239:9126','192.168.9.115:9126','10.157.0.166:9126','10.157.0.15:9126','10.157.1.86:9126','192.168.14.129:9126','192.168.9.113:9126','10.157.0.158:9126','192.168.14.130:9126','10.157.1.152:9126','10.157.0.221:9126','10.157.0.116:9126','192.168.14.121:9126','192.168.8.161:9126','10.157.1.125:9126','10.157.0.77:9126','192.168.14.59:9126','192.168.15.9:9126','10.157.0.150:9126','192.168.14.53:9126','10.157.0.219:9126','10.157.0.196:9126','10.157.0.85:9126','10.157.1.35:9126','192.168.15.7:9126','192.168.8.207:9126','192.168.9.111:9126','10.157.1.109:9126','10.157.1.130:9126','192.168.8.237:9126','10.157.1.3:9126','192.168.9.117:9126','10.157.1.77:9126','192.168.15.21:9126','192.168.15.175:9126','192.168.15.8:9126','192.168.15.65:9126','10.157.0.187:9126','10.157.0.89:9126','192.168.9.70:9126','10.157.0.207:9126','10.157.0.233:9126','10.157.0.28:9126','10.157.0.82:9126','192.168.14.57:9126','10.157.1.164:9126','10.157.1.105:9126','10.157.1.124:9126','192.168.8.238:9126','10.157.0.87:9126','10.157.1.111:9126','192.168.15.4:9126','192.168.14.135:9126','10.157.0.185:9126','192.168.15.2:9126','10.157.1.79:9126','10.157.1.56:9126','10.157.0.173:9126','10.157.0.55:9126','10.157.1.61:9126','10.157.0.101:9126','10.157.0.64:9126','192.168.8.234:9126','192.168.13.26:9126','10.157.0.51:9126','10.157.0.74:9126','10.157.0.86:9126','10.157.1.57:9126','10.157.1.63:9126','192.168.14.111:9126','10.157.1.82:9126','192.168.14.179:9126','10.157.0.194:9126','10.157.0.152:9126','10.157.1.14:9126','192.168.15.76:9126','10.157.0.106:9126','192.168.15.16:9126','192.168.14.117:9126','192.168.15.138:9126','10.157.0.157:9126','10.157.0.91:9126','10.157.1.66:9126','10.157.1.112:9126','10.157.0.108:9126','192.168.14.126:9126','10.157.0.124:9126','10.157.0.41:9126','10.157.0.23:9126','10.157.1.122:9126','10.157.0.111:9126','10.157.1.104:9126','10.157.1.115:9126','10.157.0.246:9126','10.157.0.59:9126','10.157.1.32:9126','10.157.0.102:9126','10.157.0.109:9126','192.168.15.11:9126','10.157.1.15:9126','10.157.1.74:9126','10.157.0.241:9126','192.168.9.74:9126','10.157.0.118:9126','10.157.1.148:9126','10.157.0.48:9126','10.157.0.119:9126','10.157.0.174:9126','192.168.14.54:9126','192.168.15.150:9126','10.157.0.17:9126','10.157.0.126:9126','10.157.1.69:9126','10.157.0.227:9126','10.157.1.132:9126','192.168.8.235:9126','10.157.1.123:9126','10.157.1.159:9126','10.157.0.230:9126','10.157.1.158:9126','10.157.0.220:9126','10.157.0.171:9126','10.157.0.123:9126','10.157.0.238:9126','10.157.0.182:9126','10.157.1.93:9126','10.157.0.36:9126','10.157.0.45:9126','10.157.0.31:9126','10.157.1.84:9126','10.157.0.232:9126','10.157.0.19:9126','10.157.0.172:9126','192.168.9.76:9126','10.157.1.106:9126','192.168.15.77:9126','10.157.0.223:9126','10.157.0.132:9126','10.157.0.120:9126','10.157.1.25:9126','10.157.0.189:9126','10.157.0.112:9126','192.168.15.74:9126','10.157.1.149:9126','10.157.1.47:9126','192.168.8.160:9126','10.157.1.131:9126','10.157.0.72:9126','10.157.0.113:9126','10.157.0.228:9126','192.168.14.119:9126','10.157.0.135:9126','10.157.0.29:9126','10.157.1.75:9126','192.168.15.151:9126','10.157.1.83:9126','10.157.0.57:9126','10.157.1.58:9126','10.157.1.163:9126','192.168.14.60:9126','10.157.0.114:9126','10.157.1.72:9126','192.168.14.125:9126','10.157.1.89:9126','10.157.1.110:9126','192.168.9.77:9126','10.157.0.213:9126','10.157.0.156:9126','192.168.14.72:9126','192.168.9.61:9126','10.157.0.70:9126','10.157.1.113:9126','10.157.0.61:9126','10.157.0.177:9126','10.157.0.139:9126','10.157.0.146:9126','10.157.0.236:9126','10.157.0.180:9126','10.157.1.99:9126','192.168.14.136:9126','192.168.8.236:9126','10.157.1.129:9126','192.168.14.140:9126','10.157.1.96:9126','10.157.0.56:9126','10.157.1.107:9126','10.157.0.148:9126','10.157.0.53:9126','192.168.15.22:9126','10.157.1.120:9126','10.157.0.39:9126','10.157.0.235:9126','192.168.14.77:9126','10.157.0.84:9126','192.168.14.118:9126','10.157.1.46:9126','10.157.1.127:9126','10.157.1.108:9126','10.157.0.191:9126','192.168.15.19:9126','192.168.9.53:9126','192.168.15.17:9126','10.157.0.12:9126','10.157.1.44:9126','192.168.15.18:9126','10.157.1.17:9126','10.157.0.178:9126','10.157.0.60:9126','192.168.14.123:9126','10.157.0.165:9126','10.157.0.107:9126','10.157.0.160:9126','10.157.0.218:9126','10.157.0.73:9126','10.157.1.29:9126','10.157.1.119:9126','10.157.0.190:9126','10.157.0.96:9126','10.157.1.161:9126','10.157.0.217:9126','10.157.0.47:9126','192.168.15.67:9126','192.168.8.162:9126','192.168.14.116:9126','10.157.0.154:9126','10.157.0.75:9126','10.157.1.133:9126','10.157.1.151:9126','10.157.0.251:9126','10.157.1.18:9126','10.157.0.253:9126','10.157.1.33:9126','10.157.0.62:9126','192.168.15.63:9126','10.157.1.59:9126','10.157.0.168:9126','10.157.1.8:9126','10.157.0.35:9126','10.157.0.125:9126','192.168.14.138:9126','10.157.1.100:9126','192.168.14.228:9126','10.157.0.95:9126','10.157.1.70:9126','10.157.0.195:9126','10.157.1.78:9126','10.157.1.146:9126','192.168.15.62:9126','10.157.1.128:9126','10.157.1.26:9126','10.157.0.248:9126','192.168.8.204:9126','192.168.9.119:9126','10.157.0.155:9126','10.157.1.145:9126','10.157.1.28:9126','10.157.0.183:9126','10.157.1.23:9126','10.157.1.38:9126','192.168.15.71:9126','10.157.0.188:9126','10.157.0.134:9126','192.168.14.137:9126','10.157.1.102:9126','10.157.0.37:9126','10.157.1.117:9126','192.168.15.5:9126','10.157.0.63:9126','10.157.1.48:9126','10.157.1.60:9126','10.157.1.71:9126','10.157.1.64:9126','10.157.0.76:9126','10.157.0.130:9126','10.157.0.141:9126','10.157.0.13:9126','10.157.0.92:9126','192.168.9.118:9126','10.157.1.20:9126','10.157.1.153:9126','10.157.0.176:9126','10.157.0.151:9126','10.157.0.18:9126','10.157.1.88:9126','192.168.14.131:9126','10.157.0.133:9126','10.157.1.62:9126','10.157.1.24:9126','10.157.0.65:9126','10.157.1.41:9126','192.168.9.78:9126','10.157.0.32:9126','10.157.0.104:9126','10.157.1.114:9126','10.157.1.118:9126','10.157.1.45:9126','192.168.14.110:9126','10.157.0.149:9126','10.157.0.94:9126','10.157.0.81:9126','10.157.0.142:9126','10.157.1.2:9126','10.157.1.36:9126','10.157.0.163:9126','10.157.0.117:9126','192.168.8.240:9126','192.168.8.178:9126','10.157.1.95:9126','10.157.0.237:9126','10.157.0.153:9126','10.157.0.110:9126','10.157.1.16:9126','10.157.1.116:9126','192.168.15.12:9126','10.157.0.44:9126','192.168.14.139:9126','10.157.0.33:9126','10.157.0.21:9126','10.157.0.40:9126','10.157.1.67:9126','192.168.8.205:9126','10.157.0.239:9126','192.168.9.80:9126','10.157.0.11:9126','10.157.1.31:9126','10.157.1.97:9126','10.157.0.164:9126','192.168.15.0:9126','10.157.1.6:9126','10.157.1.54:9126','10.157.0.83:9126','10.157.0.131:9126','10.157.1.40:9126','10.157.1.76:9126','10.157.0.49:9126','10.157.0.231:9126','192.168.14.78:9126','10.157.0.14:9126','10.157.0.88:9126','10.157.1.162:9126','10.157.0.184:9126','10.157.1.157:9126','10.157.0.192:9126','10.157.0.24:9126','10.157.0.90:9126','10.157.0.144:9126','10.157.1.49:9126','10.157.0.103:9126','192.168.15.75:9126','10.157.0.225:9126','10.157.0.167:9126','192.168.9.65:9126','10.157.0.222:9126','10.157.0.249:9126','10.157.1.5:9126','10.157.0.129:9126','10.157.0.181:9126','10.157.0.121:9126','10.157.0.214:9126','10.157.1.73:9126','10.157.0.250:9126','192.168.15.10:9126','10.157.0.78:9126','10.157.0.80:9126','10.157.0.43:9126','192.168.14.226:9126','192.168.14.79:9126','10.157.0.105:9126','10.157.0.162:9126','192.168.9.116:9126','10.157.1.160:9126','10.157.0.240:9126','10.157.1.43:9126','192.168.15.20:9126','10.157.0.143:9126','192.168.15.206:9126','10.157.0.147:9126','192.168.14.227:9126','192.168.9.71:9126','10.157.0.216:9126','10.157.0.93:9126','10.157.0.122:9126','10.157.0.242:9126','10.157.1.4:9126','192.168.15.13:9126','192.168.8.179:9126','10.157.0.169:9126','10.157.1.21:9126','192.168.15.152:9126','10.157.0.145:9126','192.168.15.1:9126','192.168.9.75:9126','10.157.1.143:9126','192.168.14.183:9126','10.157.0.186:9126','10.157.0.127:9126','192.168.14.122:9126','192.168.14.120:9126','192.168.14.71:9126','10.157.1.11:9126']
  - job_name: libvirt_qemu_exporter
    scheme: http
    metrics_path: /metrics
    honor_labels: False
    scrape_interval: 15s
    scrape_timeout: 15s
    static_configs:
    - targets: ['10.157.1.92:9177','10.157.1.98:9177','10.157.0.226:9177','10.157.1.42:9177','10.157.0.161:9177','10.157.1.30:9177','10.157.1.90:9177','10.157.0.100:9177','192.168.14.206:9177','10.157.0.115:9177','10.157.1.81:9177','10.157.0.159:9177','10.157.1.103:9177','10.157.0.224:9177','10.157.1.34:9177','10.157.1.94:9177','10.157.1.12:9177','10.157.1.39:9177','10.157.0.215:9177','10.157.0.203:9177','10.157.1.87:9177','10.157.0.243:9177','10.157.0.128:9177','10.157.0.170:9177','10.157.0.234:9177','10.157.1.80:9177','10.157.1.91:9177','10.157.1.10:9177','10.157.0.245:9177','10.157.1.165:9177','10.157.0.166:9177','10.157.1.86:9177','10.157.0.158:9177','10.157.1.152:9177','10.157.0.221:9177','10.157.0.116:9177','10.157.1.125:9177','10.157.0.150:9177','10.157.0.219:9177','10.157.0.196:9177','10.157.1.35:9177','10.157.1.109:9177','10.157.1.130:9177','10.157.1.3:9177','10.157.1.77:9177','10.157.0.187:9177','10.157.0.207:9177','10.157.0.233:9177','10.157.1.164:9177','10.157.1.105:9177','10.157.1.124:9177','10.157.1.111:9177','10.157.0.185:9177','10.157.1.79:9177','10.157.1.56:9177','10.157.0.173:9177','10.157.1.61:9177','10.157.0.101:9177','10.157.1.57:9177','10.157.1.63:9177','192.168.14.111:9177','10.157.1.82:9177','192.168.14.179:9177','10.157.0.194:9177','10.157.0.152:9177','10.157.1.14:9177','10.157.0.106:9177','192.168.15.138:9177','10.157.0.157:9177','10.157.1.66:9177','10.157.1.112:9177','10.157.0.108:9177','10.157.0.124:9177','10.157.1.122:9177','10.157.0.111:9177','10.157.1.104:9177','10.157.1.115:9177','10.157.0.246:9177','10.157.1.32:9177','10.157.0.102:9177','10.157.0.109:9177','10.157.1.15:9177','10.157.1.74:9177','10.157.0.241:9177','10.157.0.118:9177','10.157.1.148:9177','10.157.0.119:9177','10.157.0.174:9177','192.168.15.150:9177','10.157.0.126:9177','10.157.1.69:9177','10.157.0.227:9177','10.157.1.132:9177','10.157.1.123:9177','10.157.1.159:9177','10.157.0.230:9177','10.157.1.158:9177','10.157.0.220:9177','10.157.0.171:9177','10.157.0.123:9177','10.157.0.238:9177','10.157.0.182:9177','10.157.1.93:9177','10.157.1.84:9177','10.157.0.232:9177','10.157.0.172:9177','10.157.1.106:9177','10.157.0.223:9177','10.157.0.132:9177','10.157.0.120:9177','10.157.1.25:9177','10.157.0.189:9177','10.157.0.112:9177','10.157.1.149:9177','10.157.1.47:9177','10.157.1.131:9177','10.157.0.113:9177','10.157.0.228:9177','10.157.0.135:9177','10.157.1.75:9177','192.168.15.151:9177','10.157.1.83:9177','10.157.1.58:9177','10.157.1.163:9177','10.157.0.114:9177','10.157.1.72:9177','10.157.1.89:9177','10.157.1.110:9177','10.157.0.213:9177','10.157.0.156:9177','192.168.9.61:9177','10.157.1.113:9177','10.157.0.177:9177','10.157.0.139:9177','10.157.0.146:9177','10.157.0.236:9177','10.157.0.180:9177','10.157.1.99:9177','10.157.1.129:9177','10.157.1.96:9177','10.157.1.107:9177','10.157.0.148:9177','10.157.1.120:9177','10.157.0.235:9177','10.157.1.46:9177','10.157.1.127:9177','10.157.1.108:9177','10.157.0.191:9177','10.157.1.44:9177','10.157.1.17:9177','10.157.0.178:9177','10.157.0.165:9177','10.157.0.107:9177','10.157.0.160:9177','10.157.0.218:9177','10.157.1.29:9177','10.157.1.119:9177','10.157.0.190:9177','10.157.1.161:9177','10.157.0.217:9177','10.157.0.154:9177','10.157.1.133:9177','10.157.1.151:9177','10.157.0.251:9177','10.157.1.18:9177','10.157.0.253:9177','10.157.1.33:9177','10.157.1.59:9177','10.157.0.168:9177','10.157.1.8:9177','10.157.0.125:9177','10.157.1.100:9177','10.157.1.70:9177','10.157.0.195:9177','10.157.1.78:9177','10.157.1.146:9177','10.157.1.128:9177','10.157.1.26:9177','10.157.0.248:9177','10.157.0.155:9177','10.157.1.145:9177','10.157.1.28:9177','10.157.0.183:9177','10.157.1.23:9177','10.157.1.38:9177','10.157.0.188:9177','10.157.0.134:9177','10.157.1.102:9177','10.157.1.117:9177','10.157.1.48:9177','10.157.1.60:9177','10.157.1.71:9177','10.157.1.64:9177','10.157.0.130:9177','10.157.0.141:9177','10.157.1.20:9177','10.157.1.153:9177','10.157.0.176:9177','10.157.0.151:9177','10.157.1.88:9177','10.157.0.133:9177','10.157.1.62:9177','10.157.1.24:9177','10.157.1.41:9177','10.157.0.104:9177','10.157.1.114:9177','10.157.1.118:9177','10.157.1.45:9177','192.168.14.110:9177','10.157.0.149:9177','10.157.0.142:9177','10.157.1.2:9177','10.157.1.36:9177','10.157.0.163:9177','10.157.0.117:9177','10.157.1.95:9177','10.157.0.237:9177','10.157.0.153:9177','10.157.0.110:9177','10.157.1.16:9177','10.157.1.116:9177','10.157.1.67:9177','10.157.0.239:9177','10.157.1.31:9177','10.157.1.97:9177','10.157.0.164:9177','10.157.1.6:9177','10.157.1.54:9177','10.157.0.131:9177','10.157.1.40:9177','10.157.1.76:9177','10.157.0.231:9177','10.157.1.162:9177','10.157.0.184:9177','10.157.1.157:9177','10.157.0.192:9177','10.157.0.144:9177','10.157.1.49:9177','10.157.0.103:9177','10.157.0.225:9177','10.157.0.167:9177','10.157.0.222:9177','10.157.0.249:9177','10.157.1.5:9177','10.157.0.129:9177','10.157.0.181:9177','10.157.0.121:9177','10.157.0.214:9177','10.157.1.73:9177','10.157.0.250:9177','10.157.0.105:9177','10.157.0.162:9177','10.157.1.160:9177','10.157.0.240:9177','10.157.1.43:9177','10.157.0.143:9177','192.168.15.206:9177','10.157.0.147:9177','10.157.0.216:9177','10.157.0.122:9177','10.157.0.242:9177','10.157.1.4:9177','10.157.0.169:9177','10.157.1.21:9177','192.168.15.152:9177','10.157.0.145:9177','10.157.1.143:9177','192.168.14.183:9177','10.157.0.186:9177','10.157.0.127:9177','10.157.1.11:9177']
    metric_relabel_configs:
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.92:9177"
        target_label: "host"
        replacement: "cmp247"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.98:9177"
        target_label: "host"
        replacement: "cmp253"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.226:9177"
        target_label: "host"
        replacement: "cmp127"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.42:9177"
        target_label: "host"
        replacement: "cmp197"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.161:9177"
        target_label: "host"
        replacement: "cmp062"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.30:9177"
        target_label: "host"
        replacement: "cmp185"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.90:9177"
        target_label: "host"
        replacement: "cmp245"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.100:9177"
        target_label: "host"
        replacement: "cmp001"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.14.206:9177"
        target_label: "host"
        replacement: "cmp256"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.115:9177"
        target_label: "host"
        replacement: "cmp016"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.81:9177"
        target_label: "host"
        replacement: "cmp236"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.159:9177"
        target_label: "host"
        replacement: "cmp060"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.103:9177"
        target_label: "host"
        replacement: "cmp258"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.224:9177"
        target_label: "host"
        replacement: "cmp125"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.34:9177"
        target_label: "host"
        replacement: "cmp189"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.94:9177"
        target_label: "host"
        replacement: "cmp249"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.12:9177"
        target_label: "host"
        replacement: "cmp167"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.39:9177"
        target_label: "host"
        replacement: "cmp194"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.215:9177"
        target_label: "host"
        replacement: "cmp116"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.203:9177"
        target_label: "host"
        replacement: "cmp104"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.87:9177"
        target_label: "host"
        replacement: "cmp242"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.243:9177"
        target_label: "host"
        replacement: "cmp144"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.128:9177"
        target_label: "host"
        replacement: "cmp029"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.170:9177"
        target_label: "host"
        replacement: "cmp071"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.234:9177"
        target_label: "host"
        replacement: "cmp135"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.80:9177"
        target_label: "host"
        replacement: "cmp235"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.91:9177"
        target_label: "host"
        replacement: "cmp246"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.10:9177"
        target_label: "host"
        replacement: "cmp165"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.245:9177"
        target_label: "host"
        replacement: "cmp146"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.165:9177"
        target_label: "host"
        replacement: "cmp320"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.166:9177"
        target_label: "host"
        replacement: "cmp067"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.86:9177"
        target_label: "host"
        replacement: "cmp241"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.158:9177"
        target_label: "host"
        replacement: "cmp059"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.152:9177"
        target_label: "host"
        replacement: "cmp307"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.221:9177"
        target_label: "host"
        replacement: "cmp122"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.116:9177"
        target_label: "host"
        replacement: "cmp017"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.125:9177"
        target_label: "host"
        replacement: "cmp280"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.150:9177"
        target_label: "host"
        replacement: "cmp051"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.219:9177"
        target_label: "host"
        replacement: "cmp120"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.196:9177"
        target_label: "host"
        replacement: "cmp097"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.35:9177"
        target_label: "host"
        replacement: "cmp190"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.109:9177"
        target_label: "host"
        replacement: "cmp264"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.130:9177"
        target_label: "host"
        replacement: "cmp285"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.3:9177"
        target_label: "host"
        replacement: "cmp158"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.77:9177"
        target_label: "host"
        replacement: "cmp232"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.187:9177"
        target_label: "host"
        replacement: "cmp088"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.207:9177"
        target_label: "host"
        replacement: "cmp108"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.233:9177"
        target_label: "host"
        replacement: "cmp134"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.164:9177"
        target_label: "host"
        replacement: "cmp319"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.105:9177"
        target_label: "host"
        replacement: "cmp260"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.124:9177"
        target_label: "host"
        replacement: "cmp279"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.111:9177"
        target_label: "host"
        replacement: "cmp266"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.185:9177"
        target_label: "host"
        replacement: "cmp086"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.79:9177"
        target_label: "host"
        replacement: "cmp234"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.56:9177"
        target_label: "host"
        replacement: "cmp211"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.173:9177"
        target_label: "host"
        replacement: "cmp074"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.61:9177"
        target_label: "host"
        replacement: "cmp216"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.101:9177"
        target_label: "host"
        replacement: "cmp002"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.57:9177"
        target_label: "host"
        replacement: "cmp212"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.63:9177"
        target_label: "host"
        replacement: "cmp218"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.14.111:9177"
        target_label: "host"
        replacement: "cmp038"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.82:9177"
        target_label: "host"
        replacement: "cmp237"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.14.179:9177"
        target_label: "host"
        replacement: "cmp076"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.194:9177"
        target_label: "host"
        replacement: "cmp095"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.152:9177"
        target_label: "host"
        replacement: "cmp053"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.14:9177"
        target_label: "host"
        replacement: "cmp169"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.106:9177"
        target_label: "host"
        replacement: "cmp007"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.15.138:9177"
        target_label: "host"
        replacement: "cmp206"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.157:9177"
        target_label: "host"
        replacement: "cmp058"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.66:9177"
        target_label: "host"
        replacement: "cmp221"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.112:9177"
        target_label: "host"
        replacement: "cmp267"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.108:9177"
        target_label: "host"
        replacement: "cmp009"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.124:9177"
        target_label: "host"
        replacement: "cmp025"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.122:9177"
        target_label: "host"
        replacement: "cmp277"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.111:9177"
        target_label: "host"
        replacement: "cmp012"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.104:9177"
        target_label: "host"
        replacement: "cmp259"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.115:9177"
        target_label: "host"
        replacement: "cmp270"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.246:9177"
        target_label: "host"
        replacement: "cmp147"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.32:9177"
        target_label: "host"
        replacement: "cmp187"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.102:9177"
        target_label: "host"
        replacement: "cmp003"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.109:9177"
        target_label: "host"
        replacement: "cmp010"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.15:9177"
        target_label: "host"
        replacement: "cmp170"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.74:9177"
        target_label: "host"
        replacement: "cmp229"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.241:9177"
        target_label: "host"
        replacement: "cmp142"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.118:9177"
        target_label: "host"
        replacement: "cmp019"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.148:9177"
        target_label: "host"
        replacement: "cmp303"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.119:9177"
        target_label: "host"
        replacement: "cmp020"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.174:9177"
        target_label: "host"
        replacement: "cmp075"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.15.150:9177"
        target_label: "host"
        replacement: "cmp207"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.126:9177"
        target_label: "host"
        replacement: "cmp027"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.69:9177"
        target_label: "host"
        replacement: "cmp224"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.227:9177"
        target_label: "host"
        replacement: "cmp128"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.132:9177"
        target_label: "host"
        replacement: "cmp287"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.123:9177"
        target_label: "host"
        replacement: "cmp278"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.159:9177"
        target_label: "host"
        replacement: "cmp314"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.230:9177"
        target_label: "host"
        replacement: "cmp131"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.158:9177"
        target_label: "host"
        replacement: "cmp313"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.220:9177"
        target_label: "host"
        replacement: "cmp121"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.171:9177"
        target_label: "host"
        replacement: "cmp072"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.123:9177"
        target_label: "host"
        replacement: "cmp024"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.238:9177"
        target_label: "host"
        replacement: "cmp139"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.182:9177"
        target_label: "host"
        replacement: "cmp083"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.93:9177"
        target_label: "host"
        replacement: "cmp248"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.84:9177"
        target_label: "host"
        replacement: "cmp239"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.232:9177"
        target_label: "host"
        replacement: "cmp133"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.172:9177"
        target_label: "host"
        replacement: "cmp073"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.106:9177"
        target_label: "host"
        replacement: "cmp261"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.223:9177"
        target_label: "host"
        replacement: "cmp124"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.132:9177"
        target_label: "host"
        replacement: "cmp033"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.120:9177"
        target_label: "host"
        replacement: "cmp021"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.25:9177"
        target_label: "host"
        replacement: "cmp180"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.189:9177"
        target_label: "host"
        replacement: "cmp090"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.112:9177"
        target_label: "host"
        replacement: "cmp013"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.149:9177"
        target_label: "host"
        replacement: "cmp304"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.47:9177"
        target_label: "host"
        replacement: "cmp202"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.131:9177"
        target_label: "host"
        replacement: "cmp286"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.113:9177"
        target_label: "host"
        replacement: "cmp014"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.228:9177"
        target_label: "host"
        replacement: "cmp129"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.135:9177"
        target_label: "host"
        replacement: "cmp036"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.75:9177"
        target_label: "host"
        replacement: "cmp230"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.15.151:9177"
        target_label: "host"
        replacement: "cmp208"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.83:9177"
        target_label: "host"
        replacement: "cmp238"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.58:9177"
        target_label: "host"
        replacement: "cmp213"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.163:9177"
        target_label: "host"
        replacement: "cmp318"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.114:9177"
        target_label: "host"
        replacement: "cmp015"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.72:9177"
        target_label: "host"
        replacement: "cmp227"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.89:9177"
        target_label: "host"
        replacement: "cmp244"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.110:9177"
        target_label: "host"
        replacement: "cmp265"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.213:9177"
        target_label: "host"
        replacement: "cmp114"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.156:9177"
        target_label: "host"
        replacement: "cmp057"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.9.61:9177"
        target_label: "host"
        replacement: "cmp039"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.113:9177"
        target_label: "host"
        replacement: "cmp268"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.177:9177"
        target_label: "host"
        replacement: "cmp078"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.139:9177"
        target_label: "host"
        replacement: "cmp040"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.146:9177"
        target_label: "host"
        replacement: "cmp047"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.236:9177"
        target_label: "host"
        replacement: "cmp137"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.180:9177"
        target_label: "host"
        replacement: "cmp081"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.99:9177"
        target_label: "host"
        replacement: "cmp254"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.129:9177"
        target_label: "host"
        replacement: "cmp284"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.96:9177"
        target_label: "host"
        replacement: "cmp251"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.107:9177"
        target_label: "host"
        replacement: "cmp262"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.148:9177"
        target_label: "host"
        replacement: "cmp049"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.120:9177"
        target_label: "host"
        replacement: "cmp275"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.235:9177"
        target_label: "host"
        replacement: "cmp136"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.46:9177"
        target_label: "host"
        replacement: "cmp201"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.127:9177"
        target_label: "host"
        replacement: "cmp282"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.108:9177"
        target_label: "host"
        replacement: "cmp263"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.191:9177"
        target_label: "host"
        replacement: "cmp092"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.44:9177"
        target_label: "host"
        replacement: "cmp199"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.17:9177"
        target_label: "host"
        replacement: "cmp172"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.178:9177"
        target_label: "host"
        replacement: "cmp079"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.165:9177"
        target_label: "host"
        replacement: "cmp066"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.107:9177"
        target_label: "host"
        replacement: "cmp008"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.160:9177"
        target_label: "host"
        replacement: "cmp061"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.218:9177"
        target_label: "host"
        replacement: "cmp119"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.29:9177"
        target_label: "host"
        replacement: "cmp184"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.119:9177"
        target_label: "host"
        replacement: "cmp274"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.190:9177"
        target_label: "host"
        replacement: "cmp091"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.161:9177"
        target_label: "host"
        replacement: "cmp316"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.217:9177"
        target_label: "host"
        replacement: "cmp118"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.154:9177"
        target_label: "host"
        replacement: "cmp055"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.133:9177"
        target_label: "host"
        replacement: "cmp288"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.151:9177"
        target_label: "host"
        replacement: "cmp306"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.251:9177"
        target_label: "host"
        replacement: "cmp152"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.18:9177"
        target_label: "host"
        replacement: "cmp173"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.253:9177"
        target_label: "host"
        replacement: "cmp154"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.33:9177"
        target_label: "host"
        replacement: "cmp188"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.59:9177"
        target_label: "host"
        replacement: "cmp214"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.168:9177"
        target_label: "host"
        replacement: "cmp069"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.8:9177"
        target_label: "host"
        replacement: "cmp163"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.125:9177"
        target_label: "host"
        replacement: "cmp026"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.100:9177"
        target_label: "host"
        replacement: "cmp255"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.70:9177"
        target_label: "host"
        replacement: "cmp225"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.195:9177"
        target_label: "host"
        replacement: "cmp096"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.78:9177"
        target_label: "host"
        replacement: "cmp233"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.146:9177"
        target_label: "host"
        replacement: "cmp301"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.128:9177"
        target_label: "host"
        replacement: "cmp283"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.26:9177"
        target_label: "host"
        replacement: "cmp181"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.248:9177"
        target_label: "host"
        replacement: "cmp149"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.155:9177"
        target_label: "host"
        replacement: "cmp056"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.145:9177"
        target_label: "host"
        replacement: "cmp300"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.28:9177"
        target_label: "host"
        replacement: "cmp183"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.183:9177"
        target_label: "host"
        replacement: "cmp084"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.23:9177"
        target_label: "host"
        replacement: "cmp178"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.38:9177"
        target_label: "host"
        replacement: "cmp193"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.188:9177"
        target_label: "host"
        replacement: "cmp089"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.134:9177"
        target_label: "host"
        replacement: "cmp035"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.102:9177"
        target_label: "host"
        replacement: "cmp257"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.117:9177"
        target_label: "host"
        replacement: "cmp272"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.48:9177"
        target_label: "host"
        replacement: "cmp203"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.60:9177"
        target_label: "host"
        replacement: "cmp215"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.71:9177"
        target_label: "host"
        replacement: "cmp226"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.64:9177"
        target_label: "host"
        replacement: "cmp219"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.130:9177"
        target_label: "host"
        replacement: "cmp031"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.141:9177"
        target_label: "host"
        replacement: "cmp042"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.20:9177"
        target_label: "host"
        replacement: "cmp175"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.153:9177"
        target_label: "host"
        replacement: "cmp308"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.176:9177"
        target_label: "host"
        replacement: "cmp077"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.151:9177"
        target_label: "host"
        replacement: "cmp052"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.88:9177"
        target_label: "host"
        replacement: "cmp243"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.133:9177"
        target_label: "host"
        replacement: "cmp034"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.62:9177"
        target_label: "host"
        replacement: "cmp217"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.24:9177"
        target_label: "host"
        replacement: "cmp179"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.41:9177"
        target_label: "host"
        replacement: "cmp196"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.104:9177"
        target_label: "host"
        replacement: "cmp005"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.114:9177"
        target_label: "host"
        replacement: "cmp269"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.118:9177"
        target_label: "host"
        replacement: "cmp273"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.45:9177"
        target_label: "host"
        replacement: "cmp200"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.14.110:9177"
        target_label: "host"
        replacement: "cmp037"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.149:9177"
        target_label: "host"
        replacement: "cmp050"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.142:9177"
        target_label: "host"
        replacement: "cmp043"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.2:9177"
        target_label: "host"
        replacement: "cmp157"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.36:9177"
        target_label: "host"
        replacement: "cmp191"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.163:9177"
        target_label: "host"
        replacement: "cmp064"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.117:9177"
        target_label: "host"
        replacement: "cmp018"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.95:9177"
        target_label: "host"
        replacement: "cmp250"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.237:9177"
        target_label: "host"
        replacement: "cmp138"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.153:9177"
        target_label: "host"
        replacement: "cmp054"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.110:9177"
        target_label: "host"
        replacement: "cmp011"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.16:9177"
        target_label: "host"
        replacement: "cmp171"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.116:9177"
        target_label: "host"
        replacement: "cmp271"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.67:9177"
        target_label: "host"
        replacement: "cmp222"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.239:9177"
        target_label: "host"
        replacement: "cmp140"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.31:9177"
        target_label: "host"
        replacement: "cmp186"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.97:9177"
        target_label: "host"
        replacement: "cmp252"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.164:9177"
        target_label: "host"
        replacement: "cmp065"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.6:9177"
        target_label: "host"
        replacement: "cmp161"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.54:9177"
        target_label: "host"
        replacement: "cmp209"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.131:9177"
        target_label: "host"
        replacement: "cmp032"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.40:9177"
        target_label: "host"
        replacement: "cmp195"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.76:9177"
        target_label: "host"
        replacement: "cmp231"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.231:9177"
        target_label: "host"
        replacement: "cmp132"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.162:9177"
        target_label: "host"
        replacement: "cmp317"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.184:9177"
        target_label: "host"
        replacement: "cmp085"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.157:9177"
        target_label: "host"
        replacement: "cmp312"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.192:9177"
        target_label: "host"
        replacement: "cmp093"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.144:9177"
        target_label: "host"
        replacement: "cmp045"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.49:9177"
        target_label: "host"
        replacement: "cmp204"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.103:9177"
        target_label: "host"
        replacement: "cmp004"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.225:9177"
        target_label: "host"
        replacement: "cmp126"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.167:9177"
        target_label: "host"
        replacement: "cmp068"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.222:9177"
        target_label: "host"
        replacement: "cmp123"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.249:9177"
        target_label: "host"
        replacement: "cmp150"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.5:9177"
        target_label: "host"
        replacement: "cmp160"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.129:9177"
        target_label: "host"
        replacement: "cmp030"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.181:9177"
        target_label: "host"
        replacement: "cmp082"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.121:9177"
        target_label: "host"
        replacement: "cmp022"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.214:9177"
        target_label: "host"
        replacement: "cmp115"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.73:9177"
        target_label: "host"
        replacement: "cmp228"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.250:9177"
        target_label: "host"
        replacement: "cmp151"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.105:9177"
        target_label: "host"
        replacement: "cmp006"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.162:9177"
        target_label: "host"
        replacement: "cmp063"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.160:9177"
        target_label: "host"
        replacement: "cmp315"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.240:9177"
        target_label: "host"
        replacement: "cmp141"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.43:9177"
        target_label: "host"
        replacement: "cmp198"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.143:9177"
        target_label: "host"
        replacement: "cmp044"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.15.206:9177"
        target_label: "host"
        replacement: "cmp309"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.147:9177"
        target_label: "host"
        replacement: "cmp048"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.216:9177"
        target_label: "host"
        replacement: "cmp117"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.122:9177"
        target_label: "host"
        replacement: "cmp023"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.242:9177"
        target_label: "host"
        replacement: "cmp143"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.4:9177"
        target_label: "host"
        replacement: "cmp159"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.169:9177"
        target_label: "host"
        replacement: "cmp070"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.21:9177"
        target_label: "host"
        replacement: "cmp176"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.15.152:9177"
        target_label: "host"
        replacement: "cmp205"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.145:9177"
        target_label: "host"
        replacement: "cmp046"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.143:9177"
        target_label: "host"
        replacement: "cmp298"
      - action: replace
        source_labels: ['instance']
        regex: "192.168.14.183:9177"
        target_label: "host"
        replacement: "cmp080"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.186:9177"
        target_label: "host"
        replacement: "cmp087"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.127:9177"
        target_label: "host"
        replacement: "cmp028"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.1.11:9177"
        target_label: "host"
        replacement: "cmp166"
  - job_name: jmx_cassandra_exporter
    scheme: http
    metrics_path: /metrics
    honor_labels: False
    scrape_interval: 15s
    scrape_timeout: 15s
    static_configs:
    - targets: ['10.157.0.25:9111','10.157.0.27:9111','10.157.0.28:9111','10.157.0.23:9111','10.157.0.29:9111','10.157.0.24:9111']
    metric_relabel_configs:
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.25:9111"
        target_label: "host"
        replacement: "ntw03"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.27:9111"
        target_label: "host"
        replacement: "nal01"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.28:9111"
        target_label: "host"
        replacement: "nal02"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.23:9111"
        target_label: "host"
        replacement: "ntw01"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.29:9111"
        target_label: "host"
        replacement: "nal03"
      - action: replace
        source_labels: ['instance']
        regex: "10.157.0.24:9111"
        target_label: "host"
        replacement: "ntw02"
  - job_name: influxdb_relay
    scheme: http
    metrics_path: /metrics
    honor_labels: False
    scrape_interval: 15s
    scrape_timeout: 15s
    static_configs:
    - targets: ['10.157.0.52:9196','10.157.0.51:9196','10.157.0.53:9196']
  - job_name: grafana
    scheme: http
    metrics_path: /metrics
    honor_labels: False
    scrape_interval: 15s
    scrape_timeout: 15s
    static_configs:
    - targets: ['10.157.0.42:15013']
    metric_relabel_configs:
      - action: drop
        source_labels: ['__name__']
        regex: "http_.*"
  - job_name: alertmanager
    dns_sd_configs:
    - names:
      - tasks.monitoring_alertmanager
      type: A
      port: 9093
  - job_name: prometheus
    dns_sd_configs:
    - names:
      - tasks.monitoring_server
      type: A
      port: 9090
  - job_name: pushgateway
    dns_sd_configs:
    - names:
      - tasks.monitoring_pushgateway
      type: A
      port: 9091
  - job_name: remote_agent
    dns_sd_configs:
    - names:
      - tasks.monitoring_remote_agent
      type: A
      port: 9126
  - job_name: remote_storage_adapter
    dns_sd_configs:
    - names:
      - tasks.monitoring_remote_storage_adapter
      type: A
      port: 9201
                                                                                                                                                                                                                                                                                                                                                                                                            prometheus/alerts.yml                                                                               0000644 0000000 0000000 00000650652 13324060546 014005  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   

groups:
- name: recording.rules
  rules:
- name: alert.rules
  rules:
  - alert: ContrailNamedProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-named"} == 0) >= count(procstat_running{process_name="contrail-named"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-named"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyMysqlClusterHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="mysql_cluster"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyNovaApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="nova_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolWriteBytesTooHighssdrbdbench
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="ssd-rbdbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench write bytes too high."
      summary: "Ceph POOL ssd-rbdbench write bytes too high"
  - alert: RabbitMQDown
    expr: >-
      rabbitmq_up != 1
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "RabbitMQ service is down on node {{ $labels.host }}"
      summary: "RabbitMQ service down"
  - alert: ContrailWebServerProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-web-server"} == 0) >= count(procstat_running{process_name="contrail-web-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-web-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyContrailApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="contrail_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: GaleraNodeNotReady
    expr: >-
      mysql_wsrep_ready != 1
    for: 1m
    labels:
      environment: "Production"
      severity: "critical"
      service: "mysql"
    annotations:
      description: "The Galera service on {{ $labels.host }} is not ready to serve queries."
      summary: "Galera on {{ $labels.host }} not ready"
  - alert: ContrailIrondProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-irond"} == 0) >= count(procstat_running{process_name="contrail-irond"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-irond"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailJobServerProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-job-server"} == 0) == count(procstat_running{process_name="contrail-job-server"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-job-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CassandraServerProcessInfo
    expr: >-
      procstat_running{process_name="cassandra-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "cassandra-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailSupervisordAnalyticsProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-analytics"} == 0) >= count(procstat_running{process_name="contrail-supervisord-analytics"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-supervisord-analytics"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolReadBytesTooHighcindervolumes
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="cinder-volumes"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes read bytes too high."
      summary: "Ceph POOL cinder-volumes read bytes too high"
  - alert: ContrailSchemaProcessInfo
    expr: >-
      procstat_running{process_name="contrail-schema"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-schema"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolWriteBytesTooHighdefaultrgwbucketsindex
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="default.rgw.buckets.index"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index write bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index write bytes too high"
  - alert: ContrailSupervisordConfigProcessInfo
    expr: >-
      procstat_running{process_name="contrail-supervisord-config"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-supervisord-config"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailVrouterAgentProcessInfo
    expr: >-
      procstat_running{process_name="contrail-vrouter-agent"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-vrouter-agent"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: NovaTotalFreeMemoryLow
    expr: >-
      (100.0 * openstack_nova_total_free_ram) / (openstack_nova_total_free_ram + openstack_nova_total_used_ram) < 10.0
    for: 1m
    labels:
      environment: "Production"
      severity: "warning"
      service: "nova"
    annotations:
      description: "Memory low limit for 1 minutes"
      summary: "Memory low limit for new instances"
  - alert: ContrailDiscoveryProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-discovery"} == 0) >= count(procstat_running{process_name="contrail-discovery"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-discovery"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyKeystoneAdminApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="keystone_admin_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: NovaServiceDown
    expr: >-
      openstack_nova_service_state == 0
    for: 2m
    labels:
      severity: "warning"
      service: "{{ $labels.service }}"
      environment: "Production"
    annotations:
      description: "'{{ $labels.service }}' is down on {{ $labels.hostname }} for the last 2 minutes."
      summary: "'{{ $labels.service }}' is down on {{ $labels.hostname }}"
  - alert: CephPoolReadBytesTooHighglanceimages
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="glance-images"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images read bytes too high."
      summary: "Ceph POOL glance-images read bytes too high"
  - alert: CephPoolWriteOpsTooHighssdvolumes
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="ssd-volumes"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes write ops too high."
      summary: "Ceph POOL ssd-volumes write ops too high"
  - alert: CephPoolUsedSpaceCriticalcindervolumes
    expr: >-
      ceph_pool_usage_bytes_used{name="cinder-volumes"} / ceph_pool_usage_max_avail{name="cinder-volumes"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL cinder-volumes space utilization critical"
  - alert: CinderServicesInfo
    expr: >-
      openstack_cinder_service == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "'{{ $labels.service }}' is down on {{ $labels.hostname }} for the last 2 minutes."
      summary: "'{{ $labels.service }}' is down"
  - alert: DockerServiceMonitoringPushgatewayReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_pushgateway"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_pushgateway"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_pushgateway"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_pushgateway'. for 2 minutes"
      summary: "Docker Swarm service monitoring_pushgateway down for 2 minutes"
  - alert: SystemMemoryAvailableTooLow
    expr: >-
      avg_over_time(mem_available_percent[5m]) < 5.0
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The percentage of free memory is too low on node {{ $labels.host }} (current value={{ $value }}%, threshold=5.0%)."
      summary: "Free memory too low on {{ $labels.host }}"
  - alert: CephPoolWriteOpsTooHighssdrbdbench
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="ssd-rbdbench"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench write ops too high."
      summary: "Ceph POOL ssd-rbdbench write ops too high"
  - alert: HAproxyGlanceRegistryApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailSvcMonitorProcessInfo
    expr: >-
      procstat_running{process_name="contrail-svc-monitor"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-svc-monitor"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolWriteOpsTooHightestrbdbench
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="testrbdbench"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench write ops too high."
      summary: "Ceph POOL testrbdbench write ops too high"
  - alert: DockerServiceMonitoringAlertmanagerReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_alertmanager"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_alertmanager"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_alertmanager"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_alertmanager'. for 2 minutes"
      summary: "Docker Swarm service monitoring_alertmanager down for 2 minutes"
  - alert: NovaSomeComputesDown
    expr: >-
      openstack_nova_service_state{service="nova-compute"} == 0
    labels:
      environment: "Production"
  - alert: NovaAPIDown
    expr: >-
      openstack_api_check_status{service=~"nova.*|placement"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for the last 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: DockerServiceMonitoringAlertmanagerCriticalReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_alertmanager"} <= 2 * 0.4
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "monitoring_alertmanager"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_alertmanager' for 2 minutes."
      summary: "Docker Swarm service monitoring_alertmanager invalid number of replicas for 2 minutes"
  - alert: CephPoolUsedSpaceWarningdefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index.new"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index.new"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index.new space utilization warning"
  - alert: RedisServerProcessDown
    expr: >-
      count(procstat_running{process_name="redis-server"} == 0) == count(procstat_running{process_name="redis-server"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "redis-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephCommitLatencyTooHigh
    expr: >-
      avg(ceph_commit_latency_sum) / avg(ceph_commitcycle_latency_avgcount) > 0.7
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph commit latency too high."
      summary: "Ceph commit latency too high"
  - alert: HAproxyInfluxdbRelayBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyHeatCfnApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolReadBytesTooHightestbench
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="testbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench read bytes too high."
      summary: "Ceph POOL testbench read bytes too high"
  - alert: ContrailVrouterAgentProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-vrouter-agent"} == 0) >= count(procstat_running{process_name="contrail-vrouter-agent"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-vrouter-agent"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrControlProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-control"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-control"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-nodemgr-control"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolUsedSpaceWarningtestrbdbench
    expr: >-
      ceph_pool_usage_bytes_used{name="testrbdbench"} / ceph_pool_usage_max_avail{name="testrbdbench"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL testrbdbench space utilization warning"
  - alert: HAproxyInfluxdbRelayBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="influxdb_relay"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: HAproxyNovaApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="nova_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="nova_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: HAproxyNovaNovncBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolUsedSpaceCriticaldefaultrgwbucketsdata
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.data"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.data"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.data space utilization critical"
  - alert: HAproxyKibanaBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="kibana"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="kibana"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ContrailXMPPSessionsTooManyVariations
    expr: >-
      abs(delta(contrail_xmpp_session_count[2m])) >= 100
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "There are too many XMPP sessions changes on node {{ $labels.host }} (current value={{ $value }}, threshold=100)"
      summary: "Number of XMPP sessions changed between checks is too high"
  - alert: ContrailWebServerProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-web-server"} == 0) >= count(procstat_running{process_name="contrail-web-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-web-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: InfluxdbHTTPPointsWrittenFail
    expr: >-
      rate(influxdb_httpd_pointsWrittenFail[2m]) / rate(influxdb_httpd_pointsWrittenOK[2m]) * 100 > 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb"
    annotations:
      description: "{{ printf `%.1f` $value }}% of written points have failed on {{ $labels.host }} (threshold=5)."
      summary: "Influxdb too many failed writes"
  - alert: ContrailCollectorAPICritical
    expr: >-
      count(http_response_status{service=~"contrail.collector"} == 0) by (service) >= count(http_response_status{service=~"contrail.collector"}) by (service) *0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolUsedSpaceCriticalssdrbdbench
    expr: >-
      ceph_pool_usage_bytes_used{name="ssd-rbdbench"} / ceph_pool_usage_max_avail{name="ssd-rbdbench"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL ssd-rbdbench space utilization critical"
  - alert: NovaServicesCritical
    expr: >-
      openstack_nova_services{state="down",service=~"nova-cert|nova-conductor|nova-consoleauth|nova-scheduler"} >= on (service) sum(openstack_nova_services{service=~"nova-cert|nova-conductor|nova-consoleauth|nova-scheduler"}) by (service) * 0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of {{ $labels.service }} services are down for the last 2 minutes"
      summary: "More than 60.0% of {{ $labels.service }} services are down"
  - alert: CephPoolReadOpsTooHightestrbdbench
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="testrbdbench"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench read ops too high."
      summary: "Ceph POOL testrbdbench read ops too high"
  - alert: CephPoolUsedSpaceWarningssdvolumes
    expr: >-
      ceph_pool_usage_bytes_used{name="ssd-volumes"} / ceph_pool_usage_max_avail{name="ssd-volumes"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL ssd-volumes space utilization warning"
  - alert: ContrailFlowsQueueLimitExceededTooMany
    expr: >-
      rate(contrail_vrouter_flows_flow_queue_limit_exceeded[5m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with queue limit exceeded on node {{ $labels.host }} (current value={{ $value }}, threshold=0.1)"
      summary: "Too many vRouter flows with queue limit exceeded"
  - alert: ContrailVrouterDNSXMPPSessionsNone
    expr: >-
      max(contrail_vrouter_dns_xmpp) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-compute"
    annotations:
      description: "There are no vRouter DNS-XMPP sessions on node {{ $labels.host }}"
      summary: "No vRouter DNS-XMPP sessions"
  - alert: ContrailNamedProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-named"} == 0) >= count(procstat_running{process_name="contrail-named"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-named"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: RabbitMQTooManyMessages
    expr: >-
      rabbitmq_overview_messages  > 1048576
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "The number of outstanding messages in RabbitMQ is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=1048576)."
      summary: "Too many messages in RabbitMQ"
  - alert: CephPoolWriteBytesTooHighdefaultrgwbucketsdata
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="default.rgw.buckets.data"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data write bytes too high."
      summary: "Ceph POOL default.rgw.buckets.data write bytes too high"
  - alert: SystemMemoryAvailableLow
    expr: >-
      avg_over_time(mem_available_percent[5m]) < 10.0
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The percentage of free memory is low on node {{ $labels.host }} (current value={{ $value }}%, threshold=10.0%)."
      summary: "Free memory low on {{ $labels.host }}"
  - alert: HAproxyHorizonWebBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolUsedSpaceCriticaldefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index.new"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index.new"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index.new space utilization critical"
  - alert: CephPoolUsedSpaceCriticaltestrbdbench
    expr: >-
      ceph_pool_usage_bytes_used{name="testrbdbench"} / ceph_pool_usage_max_avail{name="testrbdbench"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL testrbdbench space utilization critical"
  - alert: GlusterFSDown
    expr: >-
      glusterfs_up != 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "glusterfs"
    annotations:
      description: "GlusterFS service is down on node {{ $labels.host }}"
      summary: "GlusterFS service down"
  - alert: ContrailJobServerProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-job-server"} == 0) >= count(procstat_running{process_name="contrail-job-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-job-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailXMPPSessionsNoneUp
    expr: >-
      max(contrail_xmpp_session_up_count) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "There are no active XMPP sessions on node {{ $labels.host }}"
      summary: "no active XMPP sessions"
  - alert: HAproxyContrailApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="contrail_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ZookeeperCritical
    expr: >-
      count(zookeeper_up == 0) >= count(zookeeper_up) * 0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "zookeeper"
    annotations:
      description: "More than 60.0% of Zookeeper services are down"
      summary: "More than 60.0% of Zookeeper services are down"
  - alert: SystemRxPacketsDroppedTooHigh
    expr: >-
      rate(net_drop_in[1m]) > 100
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The rate of received packets which are dropped is too high on node {{ $labels.host }} for interface {{ $labels.interface }} (current value={{ $value }}/sec, threshold=100/sec)"
      summary: "Too many received packets dropped on {{ $labels.host }} for interface {{ $labels.interface }}"
  - alert: ContrailSchemaProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-schema"} == 0) == count(procstat_running{process_name="contrail-schema"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-schema"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolWriteOpsTooHighcindervolumes
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="cinder-volumes"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes write ops too high."
      summary: "Ceph POOL cinder-volumes write ops too high"
  - alert: ElasticsearchClusterDiskHighWaterMark
    expr: >-
      (max(elasticsearch_fs_total_total_in_bytes) by (host, instance) - max(elasticsearch_fs_total_available_in_bytes) by (host, instance)) / max(elasticsearch_fs_total_total_in_bytes) by (host, instance) * 100.0 >= 90
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "elasticsearch"
    annotations:
      description: "Elasticsearch will not allocate new shards to node {{ $labels.host }} and will attempt to relocate shards to another node"
      summary: "Elasticsearch high disk watermark [90%] exceeded on node {{ $labels.host}} instance {{ $labels.instance }}"
  - alert: KeystoneErrorLogsTooHigh
    expr: >-
      sum(rate(log_messages{service="keystone",level=~"(?i:(error|emergency|fatal))"}[5m])) without (level) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "The rate of errors in {{ $labels.service }} logs over the last 5 minutes is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many errors in {{ $labels.service }} logs"
  - alert: HAproxyContrailAnalyticsBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: NovaAggregatesFreeMemoryShortage
    expr: >-
      (100.0 * openstack_nova_aggregate_free_ram) / (openstack_nova_aggregate_free_ram + openstack_nova_aggregate_used_ram) < 2.0
    for: 1m
    labels:
      aggregate: "{{ $labels.aggregate }}"
      environment: "Production"
      severity: "critical"
      service: "nova"
    annotations:
      description: "Memory shortage for 1 minutes on aggregate {{ $labels.aggregate }}"
      summary: "Memory shortage for new instances on aggregate {{ $labels.aggregate }}"
  - alert: ContrailWebServerProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-web-server"} == 0) == count(procstat_running{process_name="contrail-web-server"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-web-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: NovaTotalFreeVCPUsShortage
    expr: >-
      (100.0 * openstack_nova_total_free_vcpus) / (openstack_nova_total_free_vcpus + openstack_nova_total_used_vcpus) < 2.0
    for: 1m
    labels:
      environment: "Production"
      severity: "critical"
      service: "nova"
    annotations:
      description: "VPCU shortage for 1 minutes"
      summary: "VCPU shortage for new instances"
  - alert: ContrailFlowsInvalidLabelTooMany
    expr: >-
      min(contrail_vrouter_flows_invalid_label) by (host) >= 100
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with invalid label on node {{ $labels.host }} (current value={{ $value }}, threshold=100)"
      summary: "Too many vRouter flows with invalid label"
  - alert: SystemFreeOpenFilesTooLow
    expr: >-
      predict_linear(linux_sysctl_fs_file_nr[1h], 8*3600) > linux_sysctl_fs_file_max
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "Host {{ $labels.host }}) will run out of free open files in less than 8 hours."
      summary: "Free open files for {{ $labels.path }} too low on {{ $labels.host }}"
  - alert: SaltMasterProcessDown
    expr: >-
      procstat_running{process_name="salt-master"} == 0
    labels:
      environment: "Production"
      severity: "warning"
      service: "salt-master"
    annotations:
      description: "Salt-master service is down on node {{ $labels.host }}"
      summary: "Salt-master service is down"
  - alert: DockerServiceMonitoringAlertmanagerWarningReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_alertmanager"} <= 2 * 0.7
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "monitoring_alertmanager"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_alertmanager' for 2 minutes."
      summary: "Docker Swarm service monitoring_alertmanager invalid number of replicas for 2 minutes"
  - alert: ContrailNodemgrProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr"} == 0) == count(procstat_running{process_name="contrail-nodemgr"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailCollectorAPIWarning
    expr: >-
      count(http_response_status{service=~"contrail.collector"} == 0) by (service) >= count(http_response_status{service=~"contrail.collector"}) by (service) *0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyNovaMetadataApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: SshFailedLoginsTooHigh
    expr: >-
      rate(failed_logins_total[5m]) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "ssh"
    annotations:
      description: "The rate of failed logins is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many failed SSH logins"
  - alert: HAproxyInfluxdbRelayHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="influxdb_relay"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyHeatCfnApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="heat_cfn_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: CephPoolWriteOpsTooHightestbench
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="testbench"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench write ops too high."
      summary: "Ceph POOL testbench write ops too high"
  - alert: ContrailDeviceManagerProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-device-manager"} == 0) >= count(procstat_running{process_name="contrail-device-manager"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-device-manager"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailBGPSessionsSomeDown
    expr: >-
      min(contrail_bgp_session_down_count) by (host) > 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-control"
    annotations:
      description: "There are inactive BGP sessions on node {{ $labels.host }}"
      summary: "inactive BGP sessions"
  - alert: NovaServicesDown
    expr: >-
      openstack_nova_services{state="up",service=~"nova-cert|nova-conductor|nova-consoleauth|nova-scheduler"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' services are down for the last 2 minutes"
      summary: "All {{ $labels.service }} services down"
  - alert: HAproxyRabbitmqClusterBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: RedisServerProcessCritical
    expr: >-
      count(procstat_running{process_name="redis-server"} == 0) >= count(procstat_running{process_name="redis-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "redis-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrProcessInfo
    expr: >-
      procstat_running{process_name="contrail-nodemgr"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-nodemgr"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: HAproxyContrailAnalyticsBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="contrail_analytics"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ContrailSvcMonitorProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-svc-monitor"} == 0) >= count(procstat_running{process_name="contrail-svc-monitor"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-svc-monitor"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: InfluxdbHTTPClientErrors
    expr: >-
      rate(influxdb_httpd_clientError[2m]) / rate(influxdb_httpd_req[2m]) * 100 > 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb"
    annotations:
      description: "{{ printf `%.1f` $value }}% of client requests are in error on {{ $labels.host }} (threshold=5)."
      summary: "Influxdb number of client errors is high"
  - alert: HAproxyNovaMetadataApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="nova_metadata_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CinderServicesWarning
    expr: >-
      openstack_cinder_services{service=~"cinder-volume|cinder-scheduler", state="down"} >= on (service) sum(openstack_cinder_services{service=~"cinder-volume|cinder-scheduler"}) by (service) * 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "{{ $value }} {{ $labels.service }} services are down for the last 2 minutes (More than 30.0%)"
      summary: "More than 30.0% of {{ $labels.service }} services are down"
  - alert: HAproxyGlanceApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="glance_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailVrouterLLSSessionsTooMany
    expr: >-
      min(contrail_vrouter_lls) by (host) >= 10
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter LLS sessions on node {{ $labels.host }} (current value={{ $value }}, threshold=10)"
      summary: "Too many vRouter LLS sessions"
  - alert: HAproxyElasticsearchBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolUsedSpaceWarningtestbench
    expr: >-
      ceph_pool_usage_bytes_used{name="testbench"} / ceph_pool_usage_max_avail{name="testbench"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL testbench space utilization warning"
  - alert: CephPoolReadOpsTooHightestbench
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="testbench"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench read ops too high."
      summary: "Ceph POOL testbench read ops too high"
  - alert: ContrailAnalyticsApiProcessInfo
    expr: >-
      procstat_running{process_name="contrail-analytics-api"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-analytics-api"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolWriteOpsTooHighdefaultrgwbucketsindex
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="default.rgw.buckets.index"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index write ops too high."
      summary: "Ceph POOL default.rgw.buckets.index write ops too high"
  - alert: ContrailTopologyProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-topology"} == 0) == count(procstat_running{process_name="contrail-topology"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-topology"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolReadBytesTooHighdefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="default.rgw.buckets.index.new"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new read bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index.new read bytes too high"
  - alert: CephPoolReadOpsTooHighssdvolumes
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="ssd-volumes"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes read ops too high."
      summary: "Ceph POOL ssd-volumes read ops too high"
  - alert: ContrailSupervisordControlProcessInfo
    expr: >-
      procstat_running{process_name="contrail-supervisord-control"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-supervisord-control"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: NovaComputesCritical
    expr: >-
      openstack_nova_services_percent{state="down",service=~"nova-compute"} >= on (service) sum(openstack_nova_services{service=~"nova-compute"}) by (service) * 0.5
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 50.0% of {{ $labels.service }} services are down for the last 2 minutes"
      summary: "More than 50.0% of {{ $labels.service }} services are down"
  - alert: ContrailSchemaProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-schema"} == 0) >= count(procstat_running{process_name="contrail-schema"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-schema"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: GlanceErrorLogsTooHigh
    expr: >-
      sum(rate(log_messages{service="glance",level=~"(?i:(error|emergency|fatal))"}[5m])) without (level) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "The rate of errors in {{ $labels.service }} logs over the last 5 minutes is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many errors in {{ $labels.service }} logs"
  - alert: InfluxdbRelayFailedRequests
    expr: >-
      rate(influxdb_relay_failed_requests_total[5m]) / rate(influxdb_relay_requests_total[5m]) * 100 > 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb-relay"
    annotations:
      description: "{{ printf `%.1f` $value }}% of requests have been dropped on {{ $labels.instance }} (threshold=5)."
      summary: "InfluxDB Relay too many failed requests"
  - alert: HAproxyMysqlClusterBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailVrouterDNSXMPPSessionsTooMany
    expr: >-
      min(contrail_vrouter_dns_xmpp) by (host) >= 10
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter DNS-XMPP sessions on node {{ $labels.host }} (current value={{ $value }}, threshold=10)"
      summary: "Too many vRouter DNS-XMPP sessions"
  - alert: ContrailAPICritical
    expr: >-
      count(http_response_status{service=~"contrail.api"} == 0) by (service) >= count(http_response_status{service=~"contrail.api"}) by (service) *0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephOSDSpaceLow
    expr: >-
      ceph_stat_bytes_used / ceph_stat_bytes > 0.8
    labels:
      severity: "critical"
      service: "ceph"
      environment: "Production"
    annotations:
      description: "The node ({{ $labels.host }}) is reporting lowspace on OSD {{ $labels.id }}."
      summary: "Ceph OSD {{ $labels.id }} is nearly full"
  - alert: InfluxdbDown
    expr: >-
      count(influxdb_up == 0) == count(influxdb_up)
    labels:
      environment: "Production"
      severity: "critical"
      service: "influxdb"
    annotations:
      description: "All InfluxDB services are down"
      summary: "All InfluxDB services are down"
  - alert: HAproxyNovaPlacementApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="nova_placement_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyHeatCloudwatchApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailNodemgrDatabaseProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-database"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-database"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr-database"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HeatAPIServicesDown
    expr: >-
      count(http_response_status{service=~"heat.*-api"} == 0) by (service) == on (service) count(http_response_status{service=~"heat.*-api"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "{{ $labels.service }}"
    annotations:
      description: "All {{ $labels.service }} services are down for the last 2 minutes"
      summary: "All {{ $labels.service }} services are down"
  - alert: HAproxyKibanaBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="kibana"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="kibana"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="kibana"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: DockerServiceMonitoringRelayCriticalReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_relay"} <= 2 * 0.4
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "monitoring_relay"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_relay' for 2 minutes."
      summary: "Docker Swarm service monitoring_relay invalid number of replicas for 2 minutes"
  - alert: ContrailNodeManagerAPIWarning
    expr: >-
      count(http_response_status{service=~"contrail.node.manager"} == 0) by (service) >= count(http_response_status{service=~"contrail.node.manager"}) by (service) *0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyNovaMetadataApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="nova_metadata_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ZookeeperDown
    expr: >-
      count(zookeeper_up == 0) == count(zookeeper_up)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "zookeeper"
    annotations:
      description: "All Zookeeper services are down"
      summary: "All Zookeeper services are down"
  - alert: ElasticsearchInfo
    expr: >-
      elasticsearch_up{host=~'.*'} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "elasticsearch"
    annotations:
      description: "Elasticsearch service is down on node {{ $labels.host }}"
      summary: "Elasticsearch service is down"
  - alert: HAproxyHeatCfnApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: NovaSomeDisabledComputesUp
    expr: >-
      openstack_nova_service_state{service="nova-compute"} == 1 and openstack_nova_service_status{service="nova-compute"} == 0
    for: 2m
    labels:
      severity: "warning"
      service: "nova-compute"
      environment: "Production"
    annotations:
      description: "Some compute nodes are disabled but not in DOWN state. See nova service-list for details"
      summary: "Disabled computes in UP state"
  - alert: ContrailSupervisordControlProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-control"} == 0) >= count(procstat_running{process_name="contrail-supervisord-control"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-supervisord-control"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailVrouterAPIDown
    expr: >-
      count(http_response_status{service=~"contrail.vrouter"} == 0) by (service) == count(http_response_status{service=~"contrail.vrouter"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' APIs are down"
      summary: "All '{{ $labels.service }}' APIs are down"
  - alert: NovaComputesWarning
    expr: >-
      openstack_nova_services{state="down",service=~"nova-compute"} >= on (service) sum(openstack_nova_services{service=~"nova-compute"}) by (service) * 0.25
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 25.0% of {{ $labels.service }} services are down for the last 2 minutes"
      summary: "More than 25.0% of {{ $labels.service }} services are down"
  - alert: NovaErrorLogsTooHigh
    expr: >-
      sum(rate(log_messages{service="nova",level=~"(?i:(error|emergency|fatal))"}[5m])) without (level) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "The rate of errors in {{ $labels.service }} logs over the last 5 minutes is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many errors in {{ $labels.service }} logs"
  - alert: NtpOffset
    expr: >-
      ntpq_offset >= 250
    labels:
      environment: "Production"
      severity: "critical"
      service: "ntp"
    annotations:
      description: "NTP offset is higher than 250ms on node {{ $labels.host }}"
      summary: "NTP offset is too high"
  - alert: KafkaServerProcessCritical
    expr: >-
      count(procstat_running{process_name="kafka-server"} == 0) >= count(procstat_running{process_name="kafka-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "kafka-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSupervisordControlProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-control"} == 0) >= count(procstat_running{process_name="contrail-supervisord-control"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-control"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrVrouterProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-vrouter"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-vrouter"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr-vrouter"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNamedProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-named"} == 0) == count(procstat_running{process_name="contrail-named"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-named"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailSnmpCollectorProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-snmp-collector"} == 0) == count(procstat_running{process_name="contrail-snmp-collector"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-snmp-collector"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolUsedSpaceCriticalssdvolumes
    expr: >-
      ceph_pool_usage_bytes_used{name="ssd-volumes"} / ceph_pool_usage_max_avail{name="ssd-volumes"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL ssd-volumes space utilization critical"
  - alert: ContrailDeviceManagerProcessInfo
    expr: >-
      procstat_running{process_name="contrail-device-manager"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-device-manager"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CassandraServerProcessWarning
    expr: >-
      count(procstat_running{process_name="cassandra-server"} == 0) >= count(procstat_running{process_name="cassandra-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "cassandra-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailVrouterXMPPSessionsTooManyVariations
    expr: >-
      abs(delta(contrail_vrouter_xmpp[2m])) >= 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter XMPP sessions changes on node {{ $labels.host }} (current value={{ $value }}, threshold=5)"
      summary: "Number of vRouter XMPP sessions changed between checks is too high"
  - alert: KeystoneAPIDown
    expr: >-
      openstack_api_check_status{service=~"keystone.*"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: HAproxyNovaNovncHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="nova_novnc"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailFlowsDiscardTooMany
    expr: >-
      rate(contrail_vrouter_flows_discard[5m]) >= 0.1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many discarded vRouter flows on node {{ $labels.host }} (current value={{ $value }}, threshold=0.1)"
      summary: "Too many vRouter discarded flows"
  - alert: HAproxyElasticsearchBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyCinderApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="cinder_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyContrailAnalyticsBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_analytics"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyGlareBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glare"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="glare"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glare"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: NovaTotalFreeMemoryShortage
    expr: >-
      (100.0 * openstack_nova_total_free_ram) / (openstack_nova_total_free_ram + openstack_nova_total_used_ram) < 2.0
    for: 1m
    labels:
      environment: "Production"
      severity: "critical"
      service: "nova"
    annotations:
      description: "Memory shortage for 1 minutes"
      summary: "Memory shortage for new instances"
  - alert: KafkaServerProcessDown
    expr: >-
      count(procstat_running{process_name="kafka-server"} == 0) == count(procstat_running{process_name="kafka-server"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "kafka-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: RabbitMQDiskLow
    expr: >-
      predict_linear(rabbitmq_node_disk_free[8h], 8*3600) <=  rabbitmq_node_disk_free_limit
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "The RabbitMQ disk partition will be full in less than 8 hours on node {{ $labels.host }}."
      summary: "RabbitMQ disk free space too low"
  - alert: ContrailSnmpCollectorProcessInfo
    expr: >-
      procstat_running{process_name="contrail-snmp-collector"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-snmp-collector"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ElasticsearchClusterHealthStatusRed
    expr: >-
      elasticsearch_cluster_health_status == 3
    labels:
      environment: "Production"
      severity: "critical"
      service: "elasticsearch"
    annotations:
      description: "The Elasticsearch cluster status is RED for the last 5 minutes."
      summary: "Elasticsearch cluster status is RED"
  - alert: CephPoolUsedSpaceWarningssdrbdbench
    expr: >-
      ceph_pool_usage_bytes_used{name="ssd-rbdbench"} / ceph_pool_usage_max_avail{name="ssd-rbdbench"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL ssd-rbdbench space utilization warning"
  - alert: HAproxyNovaPlacementApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailVrouterLLSSessionsTooManyVariations
    expr: >-
      abs(delta(contrail_vrouter_lls[2m])) >= 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter LLS sessions changes on node {{ $labels.host }} (current value={{ $value }}, threshold=5)"
      summary: "Number of vRouter LLS sessions changed between checks is too high"
  - alert: HAproxyElasticsearchHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="elasticsearch"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ElasticsearchClusterHealthStatusYellow
    expr: >-
      elasticsearch_cluster_health_status == 2
    labels:
      environment: "Production"
      severity: "warning"
      service: "elasticsearch"
    annotations:
      description: "The Elasticsearch cluster status is YELLOW for the last 5 minutes."
      summary: "Elasticsearch cluster status is YELLOW"
  - alert: ContrailFlowsFragErrTooMany
    expr: >-
      min(contrail_vrouter_flows_frag_err) by (host) >= 100
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with fragment errors on node {{ $labels.host }} (current value={{ $value }}, threshold=100)"
      summary: "Too many vRouter flows with fragment errors"
  - alert: CephPoolWriteBytesTooHighssdvolumes
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="ssd-volumes"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes write bytes too high."
      summary: "Ceph POOL ssd-volumes write bytes too high"
  - alert: CephHealthCritical
    expr: >-
      ceph_overall_health == 3
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph health is 'critical'. Run 'ceph -s' to get details."
      summary: "Ceph health critical"
  - alert: ContrailApiProcessInfo
    expr: >-
      procstat_running{process_name="contrail-api"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-api"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailTopologyProcessInfo
    expr: >-
      procstat_running{process_name="contrail-topology"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-topology"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolUsedSpaceWarningdefaultrgwbucketsindex
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index space utilization warning"
  - alert: HAproxyCinderApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailFlowsActiveTooMany
    expr: >-
      deriv(contrail_vrouter_flows_active[5m]) >= 100
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many active vRouter flows on node {{ $labels.host }} (current value={{ $value }}, threshold=100)"
      summary: "Too many vRouter active flows"
  - alert: KibanaProcessDown
    expr: >-
      count(procstat_running{process_name="kibana"} == 0) == count(procstat_running{process_name="kibana"})
    labels:
      environment: "Production"
      severity: "down"
      service: "kibana"
    annotations:
      description: "All Kibana services are down"
      summary: "All Kibana services are down"
  - alert: KafkaServerProcessWarning
    expr: >-
      count(procstat_running{process_name="kafka-server"} == 0) >= count(procstat_running{process_name="kafka-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "kafka-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: InfluxdbHTTPPointsWrittenDropped
    expr: >-
      rate(influxdb_httpd_pointsWrittenDropped[2m]) / rate(influxdb_httpd_pointsWrittenOK[2m]) * 100 > 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb"
    annotations:
      description: "{{ printf `%.1f` $value }}% of written points have been dropped on {{ $labels.host }} (threshold=5)."
      summary: "Influxdb too many dropped writes"
  - alert: MemcachedProcessDown
    expr: >-
      procstat_running{process_name="memcached"} == 0
    labels:
      environment: "Production"
      severity: "critical"
      service: "memcached"
    annotations:
      description: "Memcached service is down on node {{ $labels.host }}"
      summary: "Memcached service is down"
  - alert: InfluxdbRelayBufferNearFull
    expr: >-
      influxdb_relay_backend_buffer_bytes > 536870912.0 * 70 / 100
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb-relay"
    annotations:
      description: "The buffer size for the {{ $labels.instance }}/{{ $labels.backend }} backend is getting full (current value={{ $value }} bytes, threshold=375809638.4)."
      summary: "InfluxDB Relay buffer almost full"
  - alert: CinderServicesCritical
    expr: >-
      openstack_cinder_services{service=~"cinder-volume|cinder-scheduler", state="down"} >= on (service) sum(openstack_cinder_services{service=~"cinder-volume|cinder-scheduler"}) by (service) * 0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "{{ $value }} {{ $labels.service }} services are down for the last 2 minutes (More than 60.0%)"
      summary: "More than 60.0% of {{ $labels.service }} services are down"
  - alert: HeatAPIServicesInfo
    expr: >-
      http_response_status{service=~"heat.*-api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for the last 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: ContrailSupervisordConfigProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-config"} == 0) >= count(procstat_running{process_name="contrail-supervisord-config"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-supervisord-config"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrControlProcessInfo
    expr: >-
      procstat_running{process_name="contrail-nodemgr-control"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-nodemgr-control"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: NovaTotalFreeVCPUsLow
    expr: >-
      (100.0 * openstack_nova_total_free_vcpus) / (openstack_nova_total_free_vcpus + openstack_nova_total_used_vcpus) < 10.0
    for: 1m
    labels:
      environment: "Production"
      severity: "warning"
      service: "nova"
    annotations:
      description: "VPCU low limit for 1 minutes"
      summary: "VCPU low limit for new instances"
  - alert: ContrailTopologyProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-topology"} == 0) >= count(procstat_running{process_name="contrail-topology"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-topology"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrVrouterProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-vrouter"} == 0) == count(procstat_running{process_name="contrail-nodemgr-vrouter"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-nodemgr-vrouter"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailVrouterXMPPSessionsTooMany
    expr: >-
      min(contrail_vrouter_xmpp) by (host) >= 10
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter XMPP sessions on node {{ $labels.host }} (current value={{ $value }}, threshold=10)"
      summary: "Too many vRouter XMPP sessions"
  - alert: ZookeeperWarning
    expr: >-
      count(zookeeper_up == 0) >= count(zookeeper_up) * 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "zookeeper"
    annotations:
      description: "More than 30.0% of Zookeeper services are down"
      summary: "More than 30.0% of Zookeeper services are down"
  - alert: InfluxdbCritical
    expr: >-
      count(influxdb_up == 0) >= count(influxdb_up) * 0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "influxdb"
    annotations:
      description: "More than 60.0% of InfluxDB services are down"
      summary: "More than 60.0% of InfluxDB services are down"
  - alert: ContrailAlarmGenProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-alarm-gen"} == 0) >= count(procstat_running{process_name="contrail-alarm-gen"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-alarm-gen"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: SystemDiskInodesFull
    expr: >-
      disk_inodes_used / disk_inodes_total >= 0.99
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The disk inodes ({{ $labels.path }}) are used at {{ $value }}% on {{ $labels.host }}."
      summary: "Inodes for {{ $labels.path }} full on {{ $labels.host }}"
  - alert: ElasticsearchClusterDiskLowWaterMark
    expr: >-
      (max(elasticsearch_fs_total_total_in_bytes) by (host, instance) - max(elasticsearch_fs_total_available_in_bytes) by (host, instance)) / max(elasticsearch_fs_total_total_in_bytes)  by (host, instance) * 100.0 >= 85
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "elasticsearch"
    annotations:
      description: "Elasticsearch will not allocate new shards to node {{ $labels.host }}"
      summary: "Elasticsearch low disk watermark [85%] exceeded on node {{ $labels.host}} instance {{ $labels.instance }}"
  - alert: ContrailQueryEngineProcessInfo
    expr: >-
      procstat_running{process_name="contrail-query-engine"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-query-engine"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailDiscoveryAPIWarning
    expr: >-
      count(http_response_status{service=~"contrail.discovery"} == 0) by (service) >= count(http_response_status{service=~"contrail.discovery"}) by (service) *0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolReadBytesTooHighcinderbackup
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="cinder-backup"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup read bytes too high."
      summary: "Ceph POOL cinder-backup read bytes too high"
  - alert: KeystoneAPIServiceDown
    expr: >-
      http_response_status{service=~"keystone.*"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: ContrailAnalyticsApiProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-analytics-api"} == 0) == count(procstat_running{process_name="contrail-analytics-api"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-analytics-api"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyNovaMetadataApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="nova_metadata_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailSupervisordAnalyticsProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-analytics"} == 0) == count(procstat_running{process_name="contrail-supervisord-analytics"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-supervisord-analytics"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolWriteOpsTooHighdefaultrgwbucketsdata
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="default.rgw.buckets.data"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data write ops too high."
      summary: "Ceph POOL default.rgw.buckets.data write ops too high"
  - alert: CephPoolWriteBytesTooHighdefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="default.rgw.buckets.index.new"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new write bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index.new write bytes too high"
  - alert: GlanceAPIDown
    expr: >-
      max(openstack_api_check_status{service=~"glance.*"}) by (service) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: ContrailVrouterAgentProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-vrouter-agent"} == 0) >= count(procstat_running{process_name="contrail-vrouter-agent"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-vrouter-agent"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailXMPPSessionsNone
    expr: >-
      max(contrail_xmpp_session_count) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "There are no XMPP sessions on node {{ $labels.host }}"
      summary: "No XMPP sessions"
  - alert: HAproxyInfluxdbRelayBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="influxdb_relay"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephApplyLatencyTooHigh
    expr: >-
      avg(ceph_apply_latency_sum) / avg(ceph_apply_latency_avgcount) > 0.007
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph apply latency too high."
      summary: "Ceph apply latency too high"
  - alert: ContrailIrondProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-irond"} == 0) >= count(procstat_running{process_name="contrail-irond"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-irond"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailDiscoveryProcessInfo
    expr: >-
      procstat_running{process_name="contrail-discovery"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-discovery"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailAPIWarning
    expr: >-
      count(http_response_status{service=~"contrail.api"} == 0) by (service) >= count(http_response_status{service=~"contrail.api"}) by (service) *0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailApiProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-api"} == 0) >= count(procstat_running{process_name="contrail-api"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-api"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CassandraServerProcessCritical
    expr: >-
      count(procstat_running{process_name="cassandra-server"} == 0) >= count(procstat_running{process_name="cassandra-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "cassandra-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HeatAPIServicesWarning
    expr: >-
      count(http_response_status{service=~"heat.*-api"} == 0) by (service) >= on (service) count(http_response_status{service=~"heat.*-api"}) by (service) * 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "{{ $value }} {{ $labels.service }} services are down for the last 2 minutes (More than 30.0%)"
      summary: "More than 30.0% of {{ $labels.service }} services are down"
  - alert: HAproxyHorizonWebBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="horizon_web"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CephPoolUsedSpaceWarningglanceimages
    expr: >-
      ceph_pool_usage_bytes_used{name="glance-images"} / ceph_pool_usage_max_avail{name="glance-images"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL glance-images space utilization warning"
  - alert: CephPoolUsedSpaceWarningcindervolumes
    expr: >-
      ceph_pool_usage_bytes_used{name="cinder-volumes"} / ceph_pool_usage_max_avail{name="cinder-volumes"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL cinder-volumes space utilization warning"
  - alert: InfluxdbInfo
    expr: >-
      influxdb_up == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "influxdb"
    annotations:
      description: "InfluxDB service is down on node {{ $labels.host }}"
      summary: "InfluxDB service down"
  - alert: ContrailAPIInfo
    expr: >-
      http_response_status{service=~"contrail.api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is failed for 2 minutes on node {{ $labels.host }}"
      summary: "Endpoint check for '{{ $labels.service }}' is failed"
  - alert: InfluxdbWarning
    expr: >-
      count(influxdb_up == 0) >= count(influxdb_up) * 0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb"
    annotations:
      description: "More than 30.0% of InfluxDB services are down"
      summary: "More than 30.0% of InfluxDB services are down"
  - alert: ContrailDnsProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-dns"} == 0) == count(procstat_running{process_name="contrail-dns"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-dns"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailDnsProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-dns"} == 0) >= count(procstat_running{process_name="contrail-dns"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-dns"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: SystemTxPacketsDroppedTooHigh
    expr: >-
      rate(net_drop_out[1m]) > 100
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The rate of transmitted packets which are dropped is too high on node {{ $labels.host }} for interface {{ $labels.interface }} (current value={{ $value }}/sec, threshold=100/sec)"
      summary: "Too many transmitted packets dropped on {{ $labels.host }} for interface {{ $labels.interface }}"
  - alert: CephPoolWriteBytesTooHighcindervolumes
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="cinder-volumes"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes write bytes too high."
      summary: "Ceph POOL cinder-volumes write bytes too high"
  - alert: CephPoolReadOpsTooHighdefaultrgwbucketsindex
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="default.rgw.buckets.index"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index read ops too high."
      summary: "Ceph POOL default.rgw.buckets.index read ops too high"
  - alert: ContrailNodeManagerAPIInfo
    expr: >-
      http_response_status{service=~"contrail.node.manager"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is failed for 2 minutes on node {{ $labels.host }}"
      summary: "Endpoint check for '{{ $labels.service }}' is failed"
  - alert: CephPoolUsedSpaceWarningdefaultrgwbucketsdata
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.data"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.data"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.data space utilization warning"
  - alert: ContrailCollectorProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-collector"} == 0) >= count(procstat_running{process_name="contrail-collector"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-collector"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyGlanceRegistryApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailDeviceManagerProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-device-manager"} == 0) >= count(procstat_running{process_name="contrail-device-manager"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-device-manager"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CinderServicesDown
    expr: >-
      openstack_cinder_services{state="up",service=~"cinder-volume|cinder-scheduler"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All {{ $labels.service }} services are down for the last 2 minutes"
      summary: "All {{ $labels.service }} services are down"
  - alert: ContrailNodemgrControlProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-control"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-control"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr-control"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailAnalyticsApiProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-analytics-api"} == 0) >= count(procstat_running{process_name="contrail-analytics-api"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-analytics-api"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSnmpCollectorProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-snmp-collector"} == 0) >= count(procstat_running{process_name="contrail-snmp-collector"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-snmp-collector"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSupervisordDatabaseProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-database"} == 0) >= count(procstat_running{process_name="contrail-supervisord-database"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-database"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSupervisordVrouterProcessInfo
    expr: >-
      procstat_running{process_name="contrail-supervisord-vrouter"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-supervisord-vrouter"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailAlarmGenProcessInfo
    expr: >-
      procstat_running{process_name="contrail-alarm-gen"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-alarm-gen"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailNodemgrProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr"} == 0) >= count(procstat_running{process_name="contrail-nodemgr"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-nodemgr"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailDnsProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-dns"} == 0) >= count(procstat_running{process_name="contrail-dns"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-dns"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: RabbitMQMemoryLow
    expr: >-
      (rabbitmq_node_mem_limit - rabbitmq_node_mem_used) <= 104857600
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "The amount of free memory is too low on node {{ $labels.host }} (current value={{ $value }}B, threshold=104857600B)."
      summary: "RabbitMQ free memory too low"
  - alert: HAproxyHeatApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="heat_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="heat_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ContrailSupervisordVrouterProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-vrouter"} == 0) >= count(procstat_running{process_name="contrail-supervisord-vrouter"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-supervisord-vrouter"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNamedProcessInfo
    expr: >-
      procstat_running{process_name="contrail-named"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-named"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailCollectorAPIDown
    expr: >-
      count(http_response_status{service=~"contrail.collector"} == 0) by (service) == count(http_response_status{service=~"contrail.collector"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' APIs are down"
      summary: "All '{{ $labels.service }}' APIs are down"
  - alert: CassandraServerProcessDown
    expr: >-
      count(procstat_running{process_name="cassandra-server"} == 0) == count(procstat_running{process_name="cassandra-server"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "cassandra-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyKeystoneAdminApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolWriteBytesTooHighdefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="default.rgw.buckets.index.new1"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 write bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index.new1 write bytes too high"
  - alert: HAproxyGlanceRegistryApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="glance_registry_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: RabbitMQMemoryFull
    expr: >-
      rabbitmq_node_mem_used >= rabbitmq_node_mem_limit
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "All producers are blocked because the memory is full on node {{ $labels.host }}."
      summary: "RabbitMQ producers blocked due to full memory"
  - alert: CephPoolReadBytesTooHighssdvolumes
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="ssd-volumes"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-volumes read bytes too high."
      summary: "Ceph POOL ssd-volumes read bytes too high"
  - alert: HAproxyContrailApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: SystemICMPHostIsNotReachable
    expr: >-
      ping_percent_packet_loss != 0
    labels:
      severity: "critical"
      service: "icmp"
      environment: "Production"
    annotations:
      description: "Node {{ $labels.url }} is not responding to ping command"
      summary: "Node {{ $labels.url }} is not reachable via ICMP"
  - alert: ContrailSupervisordConfigProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-config"} == 0) == count(procstat_running{process_name="contrail-supervisord-config"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-config"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailIfmapServerProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-ifmap-server"} == 0) == count(procstat_running{process_name="contrail-ifmap-server"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-ifmap-server"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyHeatCloudwatchApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: HAproxyNovaApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="nova_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolReadBytesTooHighssdrbdbench
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="ssd-rbdbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench read bytes too high."
      summary: "Ceph POOL ssd-rbdbench read bytes too high"
  - alert: CephPoolReadBytesTooHighephemeralvms
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="ephemeral-vms"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms read bytes too high."
      summary: "Ceph POOL ephemeral-vms read bytes too high"
  - alert: HAproxyHeatCfnApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="heat_cfn_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="heat_cfn_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ElasticsearchCritical
    expr: >-
      count(elasticsearch_up{host=~'.*'} == 0) >= count(elasticsearch_up{host=~'.*'}) *  0.6 
    labels:
      environment: "Production"
      severity: "critical"
      service: "elasticsearch"
    annotations:
      description: "More than 60.0% of Elasticsearch services are down"
      summary: "More than 60.0% of Elasticsearch services are down"
  - alert: SystemDiskErrors
    expr: >-
      increase(hdd_errors[5m]) > 0
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The disk ({{ $labels.device }}) is reporting errors on {{ $labels.host }}."
      summary: "Disk {{ $labels.device }} is failing"
  - alert: CephPoolReadOpsTooHighephemeralvms
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="ephemeral-vms"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms read ops too high."
      summary: "Ceph POOL ephemeral-vms read ops too high"
  - alert: ContrailApiProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-api"} == 0) == count(procstat_running{process_name="contrail-api"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-api"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailIfmapServerProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-ifmap-server"} == 0) >= count(procstat_running{process_name="contrail-ifmap-server"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-ifmap-server"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyKeystonePublicApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="keystone_public_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CephPoolWriteBytesTooHightestrbdbench
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="testrbdbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench write bytes too high."
      summary: "Ceph POOL testrbdbench write bytes too high"
  - alert: ContrailCollectorProcessInfo
    expr: >-
      procstat_running{process_name="contrail-collector"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-collector"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ElasticsearchWarning
    expr: >-
      count(elasticsearch_up{host=~'.*'} == 0) >= count(elasticsearch_up{host=~'.*'}) *  0.3 
    labels:
      environment: "Production"
      severity: "warning"
      service: "elasticsearch"
    annotations:
      description: "More than 30.0% of Elasticsearch services are down"
      summary: "More than 30.0% of Elasticsearch services are down"
  - alert: ContrailVrouterAPIInfo
    expr: >-
      http_response_status{service=~"contrail.vrouter"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is failed for 2 minutes on node {{ $labels.host }}"
      summary: "Endpoint check for '{{ $labels.service }}' is failed"
  - alert: SystemDiskSpaceFull
    expr: >-
      disk_used_percent >= 85
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The disk partition ({{ $labels.path }}) is used at {{ $value }}% on {{ $labels.host }}."
      summary: "Disk partition {{ $labels.path }} full on {{ $labels.host }}"
  - alert: CephPoolWriteOpsTooHighdefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="default.rgw.buckets.index.new"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new write ops too high."
      summary: "Ceph POOL default.rgw.buckets.index.new write ops too high"
  - alert: HAproxyKeystonePublicApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyKeystoneAdminApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: MaasDhcpdProcessDown
    expr: >-
      procstat_running{process_name="mas_dhcpd"} == 0
    labels:
      severity: "critical"
      service: "maas"
      environment: "Production"
    annotations:
      description: "MaaS DHCP service stopped. Check on node {{ $labels.host }}"
      summary: "DHPD is down on node {{ $labels.host }}"
  - alert: HeatAPIDown
    expr: >-
      openstack_api_check_status{service=~"heat.*"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: HAproxyMysqlClusterBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailControlProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-control"} == 0) >= count(procstat_running{process_name="contrail-control"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-control"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailXMPPSessionsTooMany
    expr: >-
      min(contrail_xmpp_session_count) by (host) >= 500
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "There are too many XMPP sessions on node {{ $labels.host }} (current value={{ $value }}, threshold=500)"
      summary: "Too many XMPP sessions"
  - alert: HAproxyGlareBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glare"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="glare"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailFlowsInvalidNHTooMany
    expr: >-
      rate(contrail_vrouter_flows_invalid_nh[5m]) >= 2
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with invalid next hop on node {{ $labels.host }} (current value={{ $value }}, threshold=0.1)"
      summary: "Too many vRouter flows with invalid next hop"
  - alert: HAproxyHeatApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="heat_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: CephPoolWriteBytesTooHightestbench
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="testbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench write bytes too high."
      summary: "Ceph POOL testbench write bytes too high"
  - alert: HAproxyNovaNovncBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="nova_novnc"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CephPoolWriteOpsTooHighephemeralvms
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="ephemeral-vms"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms write ops too high."
      summary: "Ceph POOL ephemeral-vms write ops too high"
  - alert: ContrailNodemgrDatabaseProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-database"} == 0) == count(procstat_running{process_name="contrail-nodemgr-database"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-nodemgr-database"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyHorizonWebHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="horizon_web"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailVrouterAPICritical
    expr: >-
      count(http_response_status{service=~"contrail.vrouter"} == 0) by (service) >= count(http_response_status{service=~"contrail.vrouter"}) by (service) *0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyContrailDiscoveryBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailNodemgrDatabaseProcessInfo
    expr: >-
      procstat_running{process_name="contrail-nodemgr-database"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-nodemgr-database"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: OutOfMemoryTooHigh
    expr: >-
      rate(out_of_memory_total[5m]) > 0.0011
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The rate of out-of-memory errors is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.0011)."
      summary: "Too many out-of-memory errors"
  - alert: ContrailSnmpCollectorProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-snmp-collector"} == 0) >= count(procstat_running{process_name="contrail-snmp-collector"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-snmp-collector"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailCollectorProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-collector"} == 0) == count(procstat_running{process_name="contrail-collector"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-collector"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolWriteBytesTooHighcinderbackup
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="cinder-backup"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup write bytes too high."
      summary: "Ceph POOL cinder-backup write bytes too high"
  - alert: DockerServiceMonitoringPushgatewayWarningReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_pushgateway"} <= 2 * 0.7
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "monitoring_pushgateway"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_pushgateway' for 2 minutes."
      summary: "Docker Swarm service monitoring_pushgateway invalid number of replicas for 2 minutes"
  - alert: HAproxyNovaNovncBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_novnc"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailSupervisordConfigProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-config"} == 0) >= count(procstat_running{process_name="contrail-supervisord-config"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-config"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyGlareHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="glare"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: CephPoolReadBytesTooHightestrbdbench
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="testrbdbench"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL testrbdbench read bytes too high."
      summary: "Ceph POOL testrbdbench read bytes too high"
  - alert: CephOSDDown
    expr: >-
      ceph_osd_down == 1
    labels:
      severity: "critical"
      service: "ceph"
      environment: "Production"
    annotations:
      description: "Ceph OSD {{ $labels.host }} down"
      summary: "Ceph OSD {{ $labels.host }} down"
  - alert: ContrailJobServerProcessInfo
    expr: >-
      procstat_running{process_name="contrail-job-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-job-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolUsedSpaceWarningdefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index.new1"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index.new1"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index.new1 space utilization warning"
  - alert: KibanaProcessWarning
    expr: >-
      count(procstat_running{process_name="kibana"} == 0) >= count(procstat_running{process_name="kibana"}) * 0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "kibana"
    annotations:
      description: "More than 30.0% of Kibana services are down"
      summary: "More than 30.0% of Kibana services are down"
  - alert: HAproxyGlanceApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="glance_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="glance_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ContrailApiProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-api"} == 0) >= count(procstat_running{process_name="contrail-api"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-api"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HaproxyDown
    expr: >-
      haproxy_up != 1
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy"
    annotations:
      description: "Haproxy service is down on node {{ $labels.host }}"
      summary: "Haproxy service down"
  - alert: HAproxyKeystonePublicApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="keystone_public_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyNeutronApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="neutron_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyHeatApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="heat_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailFlowsTableFullTooMany
    expr: >-
      min(contrail_vrouter_flows_flow_table_full) by (host) >= 100
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with table full on node {{ $labels.host }} (current value={{ $value }}, threshold=100)"
      summary: "Too many vRouter flows with table full"
  - alert: HeatErrorLogsTooHigh
    expr: >-
      sum(rate(log_messages{service="heat",level=~"(?i:(error|emergency|fatal))"}[5m])) without (level) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "The rate of errors in {{ $labels.service }} logs over the last 5 minutes is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many errors in {{ $labels.service }} logs"
  - alert: ContrailCollectorProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-collector"} == 0) >= count(procstat_running{process_name="contrail-collector"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-collector"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyNeutronApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="neutron_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: ContrailFlowsInvalidITFTooMany
    expr: >-
      rate(contrail_vrouter_flows_composite_invalid_interface[5m]) >= 0.05
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter flows with composite invalid interface on node {{ $labels.host }} (current value={{ $value }}, threshold=0.05)"
      summary: "Too many vRouter flows with composite invalid interface"
  - alert: CephPoolUsedSpaceWarningcinderbackup
    expr: >-
      ceph_pool_usage_bytes_used{name="cinder-backup"} / ceph_pool_usage_max_avail{name="cinder-backup"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL cinder-backup space utilization warning"
  - alert: CephPoolReadOpsTooHighdefaultrgwbucketsdata
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="default.rgw.buckets.data"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data read ops too high."
      summary: "Ceph POOL default.rgw.buckets.data read ops too high"
  - alert: NovaAggregatesFreeMemoryLow
    expr: >-
      (100.0 * openstack_nova_aggregate_free_ram) / (openstack_nova_aggregate_free_ram + openstack_nova_aggregate_used_ram) < 10.0
    for: 1m
    labels:
      aggregate: "{{ $labels.aggregate }}"
      environment: "Production"
      severity: "warning"
      service: "nova"
    annotations:
      description: "Memory low limit for 1 minutes on aggregate {{ $labels.aggregate }}"
      summary: "Memory low limit for new instances on aggregate {{ $labels.aggregate }}"
  - alert: CephPoolReadOpsTooHighssdrbdbench
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="ssd-rbdbench"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ssd-rbdbench read ops too high."
      summary: "Ceph POOL ssd-rbdbench read ops too high"
  - alert: NovaAggregatesFreeVCPUsLow
    expr: >-
      (100.0 * openstack_nova_aggregate_free_vcpus) / (openstack_nova_aggregate_free_vcpus + openstack_nova_aggregate_used_vcpus) < 10.0
    for: 1m
    labels:
      aggregate: "{{ $labels.aggregate }}"
      environment: "Production"
      severity: "warning"
      service: "nova"
    annotations:
      description: "VPCU low limit for 1 minutes on aggregate {{ $labels.aggregate }}"
      summary: "VCPU low limit for new instances on aggregate {{ $labels.aggregate }}"
  - alert: CinderAPIServiceInfo
    expr: >-
      http_response_status{service=~"cinder-api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for the last 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: HAproxyNeutronApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailAlarmGenProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-alarm-gen"} == 0) >= count(procstat_running{process_name="contrail-alarm-gen"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-alarm-gen"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyGlanceApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="glance_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: PrometheusRemoteStorageQueue
    expr: >-
      prometheus_remote_storage_queue_length / prometheus_remote_storage_queue_capacity * 100 > 75.0
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "prometheus"
    annotations:
      description: "The Prometheus {{ $labels.instance }} remote storage queue almost full (current value={{ $value }}%, threshold=75.0%)"
      summary: "Prometheus {{ $labels.instance }} remote storage queue is filling"
  - alert: HAproxyContrailApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyKeystonePublicApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="keystone_public_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: CephPoolUsedSpaceWarningephemeralvms
    expr: >-
      ceph_pool_usage_bytes_used{name="ephemeral-vms"} / ceph_pool_usage_max_avail{name="ephemeral-vms"} >  0.75 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph POOL ephemeral-vms space utilization warning"
  - alert: DockerServiceMonitoringRemoteAgentReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_remote_agent"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_remote_agent"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_remote_agent"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_remote_agent'. for 2 minutes"
      summary: "Docker Swarm service monitoring_remote_agent down for 2 minutes"
  - alert: ContrailAPIDown
    expr: >-
      count(http_response_status{service=~"contrail.api"} == 0) by (service) == count(http_response_status{service=~"contrail.api"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' APIs are down"
      summary: "All '{{ $labels.service }}' APIs are down"
  - alert: DockerServiceMonitoringRemoteStorageAdapterReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_remote_storage_adapter"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_remote_storage_adapter"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_remote_storage_adapter"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_remote_storage_adapter'. for 2 minutes"
      summary: "Docker Swarm service monitoring_remote_storage_adapter down for 2 minutes"
  - alert: ContrailJobServerProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-job-server"} == 0) >= count(procstat_running{process_name="contrail-job-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-job-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: GlanceAPIServiceDown
    expr: >-
      http_response_status{service=~"glance-api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: ContrailQueryEngineProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-query-engine"} == 0) >= count(procstat_running{process_name="contrail-query-engine"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-query-engine"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: DockerdProcessDown
    expr: >-
      procstat_running{process_name="dockerd"} == 0
    labels:
      environment: "Production"
      severity: "critical"
      service: "docker"
    annotations:
      description: "Dockerd service is down on node {{ $labels.host }}"
      summary: "Dockerd service is down"
  - alert: SystemSSHHostIsNotReachable
    expr: >-
      ssh_reachable != 0
    labels:
      severity: "critical"
      service: "ssh"
      environment: "Production"
    annotations:
      description: "Can not connect to ssh on node {{ $labels.server }}"
      summary: "Node {{ $labels.server }} is not reachable via SSH"
  - alert: ContrailVrouterXMPPSessionsNone
    expr: >-
      max(contrail_vrouter_xmpp) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-compute"
    annotations:
      description: "There are no vRouter XMPP sessions on node {{ $labels.host }}"
      summary: "No vRouter XMPP sessions"
  - alert: ContrailQueryEngineProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-query-engine"} == 0) == count(procstat_running{process_name="contrail-query-engine"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-query-engine"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolReadBytesTooHighdefaultrgwbucketsindex
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="default.rgw.buckets.index"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index read bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index read bytes too high"
  - alert: NovaAPIServiceDown
    expr: >-
      http_response_status{service=~"nova-api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for the last 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: CephPoolReadBytesTooHighdefaultrgwbucketsdata
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="default.rgw.buckets.data"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.data read bytes too high."
      summary: "Ceph POOL default.rgw.buckets.data read bytes too high"
  - alert: ApacheIdleWorkersShortage
    expr: >-
      apache_IdleWorkers == 0
    labels:
      environment: "Production"
      severity: "warning"
      service: "apache"
    annotations:
      description: "Apache idle workers shortage on node {{ $labels.host }}"
      summary: "Apache idle workers shortage"
  - alert: NovaLibvirtDown
    expr: >-
      max(libvirt_up) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "libvirt"
    annotations:
      description: "libvirt check on '{{ $labels.host }}' is down for 2 minutes"
      summary: "libvirt check on '{{ $labels.host }}' is down"
  - alert: HAproxyContrailAnalyticsHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="contrail_analytics"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: NovaAggregatesFreeVCPUsShortage
    expr: >-
      (100.0 * openstack_nova_aggregate_free_vcpus) / (openstack_nova_aggregate_free_vcpus + openstack_nova_aggregate_used_vcpus) < 2.0
    for: 1m
    labels:
      aggregate: "{{ $labels.aggregate }}"
      environment: "Production"
      severity: "critical"
      service: "nova"
    annotations:
      description: "VPCU shortage for 1 minutes on aggregate {{ $labels.aggregate }}"
      summary: "VCPU shortage for new instances on aggregate {{ $labels.aggregate }}"
  - alert: ContrailDiscoveryProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-discovery"} == 0) >= count(procstat_running{process_name="contrail-discovery"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-discovery"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSupervisordControlProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-control"} == 0) == count(procstat_running{process_name="contrail-supervisord-control"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-control"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailSvcMonitorProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-svc-monitor"} == 0) >= count(procstat_running{process_name="contrail-svc-monitor"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-svc-monitor"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephNumOsdWarning
    expr: >-
      ceph_osdmap_num_osds > ceph_osdmap_num_up_osds
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph OSD is down. Run 'ceph osd tree' to get details."
      summary: "Ceph OSDs down warning"
  - alert: ContrailAlarmGenProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-alarm-gen"} == 0) == count(procstat_running{process_name="contrail-alarm-gen"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-alarm-gen"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyNovaPlacementApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="nova_placement_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CephPoolReadOpsTooHighcinderbackup
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="cinder-backup"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup read ops too high."
      summary: "Ceph POOL cinder-backup read ops too high"
  - alert: CinderAPIDown
    expr: >-
      max(openstack_api_check_status{service=~"cinder.*"}) by (service) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for the last 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: CephPoolUsedSpaceCriticalephemeralvms
    expr: >-
      ceph_pool_usage_bytes_used{name="ephemeral-vms"} / ceph_pool_usage_max_avail{name="ephemeral-vms"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL ephemeral-vms space utilization critical"
  - alert: ContrailDiscoveryAPIInfo
    expr: >-
      http_response_status{service=~"contrail.discovery"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is failed for 2 minutes on node {{ $labels.host }}"
      summary: "Endpoint check for '{{ $labels.service }}' is failed"
  - alert: HAproxyRabbitmqClusterBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="rabbitmq_cluster"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: HAproxyHorizonWebBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="horizon_web"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: MaasNamedProcessDown
    expr: >-
      procstat_running{process_name="mas_named"} == 0
    labels:
      severity: "critical"
      service: "maas"
      environment: "Production"
    annotations:
      description: "MaaS DNS service stopped. Check on node {{ $labels.host }}"
      summary: "Named is down on node {{ $labels.host }}"
  - alert: CephPoolUsedSpaceCriticaldefaultrgwbucketsindex
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index space utilization critical"
  - alert: ContrailControlProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-control"} == 0) == count(procstat_running{process_name="contrail-control"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-control"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: HAproxyKeystoneAdminApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="keystone_admin_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="keystone_admin_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: RedisServerProcessInfo
    expr: >-
      procstat_running{process_name="redis-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "redis-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CinderErrorLogsTooHigh
    expr: >-
      sum(rate(log_messages{service="cinder",level=~"(?i:(error|emergency|fatal))"}[5m])) without (level) > 0.2
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "The rate of errors in {{ $labels.service }} logs over the last 5 minutes is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=0.2)."
      summary: "Too many errors in {{ $labels.service }} logs"
  - alert: AlertmanagerNotificationFailed
    expr: >-
      rate(alertmanager_notifications_failed_total[5m]) > 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "alertmanager"
    annotations:
      description: "Alertmanager {{ $labels.instance }} failed notifications for {{ $labels.integration }} (current value={{ $value }}, threshold=0.3)"
      summary: "Alertmanager {{ $labels.instance }} failed notifications"
  - alert: RedisServerProcessWarning
    expr: >-
      count(procstat_running{process_name="redis-server"} == 0) >= count(procstat_running{process_name="redis-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "redis-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: NeutronAPIDown
    expr: >-
      openstack_api_check_status{service=~"neutron.*"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is down for 2 minutes"
      summary: "Endpoint check for '{{ $labels.service }}' is down"
  - alert: GlanceRegistryServiceDown
    expr: >-
      http_response_status{service=~"glance-registry"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: ContrailIfmapServerProcessInfo
    expr: >-
      procstat_running{process_name="contrail-ifmap-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-ifmap-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ElasticsearchDown
    expr: >-
      count(elasticsearch_up{host=~'.*'} == 0) == count(elasticsearch_up{host=~'.*'})
    labels:
      environment: "Production"
      severity: "down"
      service: "elasticsearch"
    annotations:
      description: "All Elasticsearch services are down"
      summary: "All Elasticsearch services are down"
  - alert: ContrailNodemgrVrouterProcessInfo
    expr: >-
      procstat_running{process_name="contrail-nodemgr-vrouter"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-nodemgr-vrouter"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailWebServerProcessInfo
    expr: >-
      procstat_running{process_name="contrail-web-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-web-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: SystemSwapIn
    expr: >-
      rate(swap_in[2m]) > 1048576
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The rate of swap input bytes is too high on node {{ $labels.host }} (current value={{ $value }}b/s, threshold=1048576b/s)."
      summary: "Swap input throughput too high on {{ $labels.host }}"
  - alert: CephPoolUsedSpaceCriticalglanceimages
    expr: >-
      ceph_pool_usage_bytes_used{name="glance-images"} / ceph_pool_usage_max_avail{name="glance-images"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL glance-images space utilization critical"
  - alert: SystemDiskSpaceTooLow
    expr: >-
      predict_linear(disk_free[1h], 8*3600) < 0
    for: 15m
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The disk partition ({{ $labels.path }}) will be full in less than 8 hours on {{ $labels.host }}."
      summary: "Free space for {{ $labels.path }} too low on {{ $labels.host }}"
  - alert: ContrailSupervisordAnalyticsProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-analytics"} == 0) >= count(procstat_running{process_name="contrail-supervisord-analytics"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-analytics"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolUsedSpaceCriticaltestbench
    expr: >-
      ceph_pool_usage_bytes_used{name="testbench"} / ceph_pool_usage_max_avail{name="testbench"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL testbench free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL testbench space utilization critical"
  - alert: ContrailIrondProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-irond"} == 0) == count(procstat_running{process_name="contrail-irond"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-irond"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: PrometheusTargetDown
    expr: >-
      up != 1
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "prometheus"
    annotations:
      description: "The Prometheus target {{ $labels.instance }} is down for the job {{ $labels.job }}."
      summary: "Prometheus endpoint {{ $labels.instance }} down"
  - alert: ContrailIfmapServerProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-ifmap-server"} == 0) >= count(procstat_running{process_name="contrail-ifmap-server"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-ifmap-server"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyKibanaBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="kibana"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="kibana"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: HAproxyContrailDiscoveryHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="contrail_discovery"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: KibanaProcessCritical
    expr: >-
      count(procstat_running{process_name="kibana"} == 0) >= count(procstat_running{process_name="kibana"}) * 0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "kibana"
    annotations:
      description: "More than 60.0% of Kibana services are down"
      summary: "More than 60.0% of Kibana services are down"
  - alert: ContrailSupervisordDatabaseProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-database"} == 0) == count(procstat_running{process_name="contrail-supervisord-database"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-database"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailNodemgrConfigProcessInfo
    expr: >-
      procstat_running{process_name="contrail-nodemgr-config"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-nodemgr-config"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephPoolWriteBytesTooHighglanceimages
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="glance-images"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images write bytes too high."
      summary: "Ceph POOL glance-images write bytes too high"
  - alert: HAproxyRabbitmqClusterHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="rabbitmq_cluster"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailNodeManagerAPIDown
    expr: >-
      count(http_response_status{service=~"contrail.node.manager"} == 0) by (service) == count(http_response_status{service=~"contrail.node.manager"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' APIs are down"
      summary: "All '{{ $labels.service }}' APIs are down"
  - alert: HeatAPIServicesCritical
    expr: >-
      count(http_response_status{service=~"heat.*-api"} == 0) by (service) >= on (service) count(http_response_status{service=~"heat.*-api"}) by (service) * 0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "{{ $value }} {{ $labels.service }} services are down for the last 2 minutes (More than 60.0%)"
      summary: "More than 60.0% of {{ $labels.service }} services are down"
  - alert: SaltMinionProcessDown
    expr: >-
      procstat_running{process_name="salt-minion"} == 0
    labels:
      environment: "Production"
      severity: "warning"
      service: "salt-minion"
    annotations:
      description: "Salt-minion service is down on node {{ $labels.host }}"
      summary: "Salt-minion service is down"
  - alert: ContrailXMPPSessionsSomeDown
    expr: >-
      min(contrail_xmpp_session_down_count) by (host) > 0
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "There are inactive XMPP sessions on node {{ $labels.host }}"
      summary: "inactive XMPP sessions"
  - alert: ContrailVrouterAPIWarning
    expr: >-
      count(http_response_status{service=~"contrail.vrouter"} == 0) by (service) >= count(http_response_status{service=~"contrail.vrouter"}) by (service) *0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyContrailDiscoveryBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="contrail_discovery"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: DockerServiceDashboardGrafanaReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="dashboard_grafana"} == 0 or absent(docker_swarm_tasks_running{service_name="dashboard_grafana"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "dashboard_grafana"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'dashboard_grafana'. for 2 minutes"
      summary: "Docker Swarm service dashboard_grafana down for 2 minutes"
  - alert: HAproxyNeutronApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="neutron_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: InfluxdbSeriesNumberTooHigh
    expr: >-
      influxdb_database_numSeries >= 10000000
    labels:
      environment: "Production"
      severity: "critical"
      service: "influxdb"
    annotations:
      description: "The InfluxDB {{ $labels.database }} database has exceeded the maximum number of series (value={{ $value }},threshold=10000000)."
      summary: "InfluxDB too many series for {{ $labels.database }}"
  - alert: KafkaServerProcessInfo
    expr: >-
      procstat_running{process_name="kafka-server"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "kafka-server"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: HAproxyGlanceApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="glance_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="glance_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: DockerServiceMonitoringRelayReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_relay"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_relay"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_relay"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_relay'. for 2 minutes"
      summary: "Docker Swarm service monitoring_relay down for 2 minutes"
  - alert: DockerServiceMonitoringRemoteCollectorReplicasDown
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_remote_collector"} == 0 or absent(docker_swarm_tasks_running{service_name="monitoring_remote_collector"}) == 1
    for: 2m
    labels:
      environment: "Production"
      severity: "down"
      service: "monitoring_remote_collector"
    annotations:
      description: "No replicas are running for the Docker Swarn service 'monitoring_remote_collector'. for 2 minutes"
      summary: "Docker Swarm service monitoring_remote_collector down for 2 minutes"
  - alert: SystemCpuIdleTooLow
    expr: >-
      avg_over_time(cpu_usage_idle{cpu="cpu-total"}[5m]) < 10.0
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The average idle CPU usage is too low on node {{ $labels.host }} (current value={{ $value }}%, threshold=10.0%)."
      summary: "Idle CPU usage too low on {{ $labels.host }}"
  - alert: HAproxyCinderApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="cinder_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: CephPoolUsedSpaceCriticaldefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_usage_bytes_used{name="default.rgw.buckets.index.new1"} / ceph_pool_usage_max_avail{name="default.rgw.buckets.index.new1"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL default.rgw.buckets.index.new1 space utilization critical"
  - alert: CephPoolReadOpsTooHighdefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="default.rgw.buckets.index.new1"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 read ops too high."
      summary: "Ceph POOL default.rgw.buckets.index.new1 read ops too high"
  - alert: CephHealthWarning
    expr: >-
      ceph_overall_health == 2
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph health is 'warning'. Run 'ceph -s' to get details."
      summary: "Ceph health warning"
  - alert: ContrailTopologyProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-topology"} == 0) >= count(procstat_running{process_name="contrail-topology"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-topology"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailDiscoveryAPICritical
    expr: >-
      count(http_response_status{service=~"contrail.discovery"} == 0) by (service) >= count(http_response_status{service=~"contrail.discovery"}) by (service) *0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: KibanaProcessInfo
    expr: >-
      procstat_running{process_name="kibana"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "kibana"
    annotations:
      description: "Kibana service is down on node {{ $labels.host }}"
      summary: "Kibana service is down"
  - alert: DockerServiceMonitoringPushgatewayCriticalReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_pushgateway"} <= 2 * 0.4
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "monitoring_pushgateway"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_pushgateway' for 2 minutes."
      summary: "Docker Swarm service monitoring_pushgateway invalid number of replicas for 2 minutes"
  - alert: HAproxyCinderApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="cinder_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: SystemDiskInodesTooLow
    expr: >-
      predict_linear(disk_inodes_free[1h], 8*3600) < 0
    for: 15m
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The disk inodes ({{ $labels.path }}) will be full in less than 8 hours on {{ $labels.host }}."
      summary: "Free inodes for {{ $labels.path }} too low on {{ $labels.host }}"
  - alert: KeystoneAPITooSlow
    expr: >-
      max by(host) (openstack_http_response_times{service='keystone',quantile="0.9",http_method=~"^(GET|POST)$",http_status=~"^2..$"}) >= 3.0
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "keystone"
    annotations:
      description: "The 90th percentile of the Keystone API response times for GET and POST requests is too high on node {{ $labels.host }} (current value={{ $value }}s, threshold=3.0s)."
      summary: "Keystone API too slow"
  - alert: ContrailNodemgrControlProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-control"} == 0) == count(procstat_running{process_name="contrail-nodemgr-control"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-nodemgr-control"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolWriteBytesTooHighephemeralvms
    expr: >-
      ceph_pool_stats_write_bytes_sec{name="ephemeral-vms"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL ephemeral-vms write bytes too high."
      summary: "Ceph POOL ephemeral-vms write bytes too high"
  - alert: RemoteStorageAdapterSendingTooSlow
    expr: >-
      100.0 - (100.0 * sent_samples_total{job="remote_storage_adapter"} / on (job, instance) received_samples_total) > 10.0
    labels:
      environment: "Production"
      severity: "warning"
      service: "remote_storage_adapter"
    annotations:
      description: "Remote storage adapter can not ingest samples fast enough on {{ $labels.instance }} (current value={{ $value }}%, threshold=10.0%)."
      summary: "Remote storage adapter too slow on {{ $labels.instance }}"
  - alert: HAproxyGlanceRegistryApiBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="glance_registry_api"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="glance_registry_api"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: HAproxyMysqlClusterBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="mysql_cluster"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="mysql_cluster"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: NeutronAPIServiceDown
    expr: >-
      http_response_status{service=~"neutron-api"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "The HTTP check for '{{ $labels.service }}' is down on {{ $labels.host }} for 2 minutes."
      summary: "HTTP check for '{{ $labels.service }}' down"
  - alert: ContrailNodeManagerAPICritical
    expr: >-
      count(http_response_status{service=~"contrail.node.manager"} == 0) by (service) >= count(http_response_status{service=~"contrail.node.manager"}) by (service) *0.6
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyKibanaHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="kibana"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: ContrailBGPSessionsNoneUp
    expr: >-
      max(contrail_bgp_session_up_count) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-control"
    annotations:
      description: "There are no active BGP sessions on node {{ $labels.host }}"
      summary: "no active BGP sessions"
  - alert: ContrailSchemaProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-schema"} == 0) >= count(procstat_running{process_name="contrail-schema"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-schema"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ZookeeperInfo
    expr: >-
      zookeeper_up != 1
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "zookeeper"
    annotations:
      description: "Zookeeper service is down on node {{ $labels.host }}."
      summary: "Zookeeper service down"
  - alert: GaleraServiceDown
    expr: >-
      mysql_up != 1
    labels:
      environment: "Production"
      severity: "critical"
      service: "mysql"
    annotations:
      description: "Galera service is down on node {{ $labels.host }}"
      summary: "Galera service down"
  - alert: CephPoolReadBytesTooHighdefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_stats_read_bytes_sec{name="default.rgw.buckets.index.new1"} >  70000000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 read bytes too high."
      summary: "Ceph POOL default.rgw.buckets.index.new1 read bytes too high"
  - alert: HAproxyGlareBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="glare"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="glare"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: RemoteStorageAdapterIgnoredTooHigh
    expr: >-
      100.0 * prometheus_influxdb_ignored_samples_total{job="remote_storage_adapter"} / on (job, instance) sent_samples_total > 5.0
    labels:
      environment: "Production"
      severity: "warning"
      service: "remote_storage_adapter"
    annotations:
      description: "Remote storage adapter is receiving too many invalid metrics on {{ $labels.instance }} (current value={{ $value }}%, threshold=5.0%)."
      summary: "Remote storage adapter receiving too many invalid metrics on {{ $labels.instance }}"
  - alert: ContrailNodemgrDatabaseProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-database"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-database"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-nodemgr-database"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailCollectorAPIInfo
    expr: >-
      http_response_status{service=~"contrail.collector"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "info"
      service: "{{ $labels.service }}"
    annotations:
      description: "Endpoint check for '{{ $labels.service }}' is failed for 2 minutes on node {{ $labels.host }}"
      summary: "Endpoint check for '{{ $labels.service }}' is failed"
  - alert: ContrailNodemgrConfigProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-config"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-config"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr-config"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolReadOpsTooHighcindervolumes
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="cinder-volumes"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-volumes read ops too high."
      summary: "Ceph POOL cinder-volumes read ops too high"
  - alert: ContrailAnalyticsApiProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-analytics-api"} == 0) >= count(procstat_running{process_name="contrail-analytics-api"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-analytics-api"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailIrondProcessInfo
    expr: >-
      procstat_running{process_name="contrail-irond"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-irond"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: RabbitMQDiskFull
    expr: >-
      rabbitmq_node_disk_free <=  rabbitmq_node_disk_free_limit
    labels:
      environment: "Production"
      severity: "critical"
      service: "rabbitmq"
    annotations:
      description: "All producers are blocked because the RabbitMQ disk partition is full on node {{ $labels.host }}."
      summary: "RabbitMQ producers blocked due to full disk"
  - alert: ContrailSupervisordVrouterProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-vrouter"} == 0) >= count(procstat_running{process_name="contrail-supervisord-vrouter"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-vrouter"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolReadOpsTooHighglanceimages
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="glance-images"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images read ops too high."
      summary: "Ceph POOL glance-images read ops too high"
  - alert: ContrailDiscoveryAPIDown
    expr: >-
      count(http_response_status{service=~"contrail.discovery"} == 0) by (service) == count(http_response_status{service=~"contrail.discovery"}) by (service)
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' APIs are down"
      summary: "All '{{ $labels.service }}' APIs are down"
  - alert: ContrailVrouterDNSXMPPSessionsTooManyVariations
    expr: >-
      abs(delta(contrail_vrouter_dns_xmpp[2m])) >= 5
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-compute"
    annotations:
      description: "There are too many vRouter DNS-XMPP sessions changes on node {{ $labels.host }} (current value={{ $value }}, threshold=5)"
      summary: "Number of vRouter DNS-XMPP sessions changed between checks is too high"
  - alert: ContrailNodemgrConfigProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-config"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-config"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-nodemgr-config"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolWriteOpsTooHighcinderbackup
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="cinder-backup"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup write ops too high."
      summary: "Ceph POOL cinder-backup write ops too high"
  - alert: ContrailNodemgrProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr"} == 0) >= count(procstat_running{process_name="contrail-nodemgr"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-nodemgr"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: ContrailSupervisordAnalyticsProcessInfo
    expr: >-
      procstat_running{process_name="contrail-supervisord-analytics"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-supervisord-analytics"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: GaleraNodeNotConnected
    expr: >-
      mysql_wsrep_connected != 1
    for: 1m
    labels:
      environment: "Production"
      severity: "critical"
      service: "mysql"
    annotations:
      description: "The Galera service on {{ $labels.host }} is not connected to the cluster."
      summary: "Galera on {{ $labels.host }} not connected"
  - alert: NovaComputesDown
    expr: >-
      openstack_nova_services{state="up",service=~"nova-compute"} == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "All '{{ $labels.service }}' services are down for the last 2 minutes"
      summary: "All {{ $labels.service }} services are down"
  - alert: ContrailDeviceManagerProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-device-manager"} == 0) == count(procstat_running{process_name="contrail-device-manager"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-device-manager"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailSvcMonitorProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-svc-monitor"} == 0) == count(procstat_running{process_name="contrail-svc-monitor"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-svc-monitor"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: DockerServiceMonitoringRelayWarningReplicasNumber
    expr: >-
      docker_swarm_tasks_running{service_name="monitoring_relay"} <= 2 * 0.7
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "monitoring_relay"
    annotations:
      description: "{{ $value }}/2 replicas are running for the Docker Swarn service 'monitoring_relay' for 2 minutes."
      summary: "Docker Swarm service monitoring_relay invalid number of replicas for 2 minutes"
  - alert: HAproxyContrailDiscoveryBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="contrail_discovery"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailControlProcessInfo
    expr: >-
      procstat_running{process_name="contrail-control"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-control"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailSupervisordDatabaseProcessInfo
    expr: >-
      procstat_running{process_name="contrail-supervisord-database"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-supervisord-database"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: ContrailControlProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-control"} == 0) >= count(procstat_running{process_name="contrail-control"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-control"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: HAproxyHeatCloudwatchApiBackendWarning
    expr: >-
      max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}[12h])) by (proxy) - min(haproxy_active_servers{sv="BACKEND",proxy="heat_cloudwatch_api"}) by (proxy) >= 1
    for: 5m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }} of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "At least one backend is down for '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailNodemgrConfigProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-config"} == 0) == count(procstat_running{process_name="contrail-nodemgr-config"})
    labels:
      environment: "Production"
      severity: "down"
      service: "contrail-nodemgr-config"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: CephPoolWriteOpsTooHighglanceimages
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="glance-images"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL glance-images write ops too high."
      summary: "Ceph POOL glance-images write ops too high"
  - alert: ContrailDiscoveryProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-discovery"} == 0) == count(procstat_running{process_name="contrail-discovery"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-discovery"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: ContrailDnsProcessInfo
    expr: >-
      procstat_running{process_name="contrail-dns"} == 0
    labels:
      environment: "Production"
      severity: "info"
      service: "contrail-dns"
    annotations:
      description: "{{ $labels.service }} service is down on node {{ $labels.host }}"
      summary: "{{ $labels.service }} service is down"
  - alert: CephUsedSpaceCritical
    expr: >-
      ceph_osd_bytes_used / ceph_osd_bytes > 0.85
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph OSD free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph used space critical"
  - alert: HAproxyNovaPlacementApiBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="nova_placement_api"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailVrouterAgentProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-vrouter-agent"} == 0) == count(procstat_running{process_name="contrail-vrouter-agent"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-vrouter-agent"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
  - alert: NovaServicesWarning
    expr: >-
      openstack_nova_services{state="down",service=~"nova-cert|nova-conductor|nova-consoleauth|nova-scheduler"} >= on (service) sum(openstack_nova_services{service=~"nova-cert|nova-conductor|nova-consoleauth|nova-scheduler"}) by (service) * 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "{{ $labels.service }}"
    annotations:
      description: "More than 30.0% of {{ $labels.service }} services are down for the last 2 minutes"
      summary: "More than 30.0% of {{ $labels.service }} services are down"
  - alert: ContrailQueryEngineProcessCritical
    expr: >-
      count(procstat_running{process_name="contrail-query-engine"} == 0) >= count(procstat_running{process_name="contrail-query-engine"}) *0.6
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-query-engine"
    annotations:
      description: "More than 60.0% of '{{ $labels.service }}' is down"
      summary: "More than 60.0% of '{{ $labels.service }}' is down"
  - alert: CephUsedSpaceWarning
    expr: >-
      ceph_osd_bytes_used / ceph_osd_bytes > 0.75
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph OSD free space utilization warning. Run 'ceph df' to get details."
      summary: "Ceph used space warning"
  - alert: HAproxyNovaApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="nova_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: NginxDown
    expr: >-
      nginx_up != 1
    labels:
      environment: "Production"
      severity: "critical"
      service: "nginx"
    annotations:
      description: "Nginx service is down on node {{ $labels.host }}"
      summary: "Nginx service down"
  - alert: ContrailBGPSessionsNone
    expr: >-
      max(contrail_bgp_session_count) by (host) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-control"
    annotations:
      description: "There are no BGP sessions on node {{ $labels.host }}"
      summary: "No BGP sessions"
  - alert: CephNumMonQuorumWarning
    expr: >-
      count(ceph_service_service_health{service='mons'}) < 3
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph Mon node is down. Run 'ceph -s' to get details."
      summary: "Ceph Mon node down warning"
  - alert: HAproxyHeatApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="heat_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: HAproxyElasticsearchBackendDown
    expr: >-
      max(haproxy_active_servers{sv="BACKEND",proxy="elasticsearch"}) by (proxy) + max(haproxy_backup_servers{sv="BACKEND",proxy="elasticsearch"}) by (proxy) == 0
    for: 2m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "The proxy '{{ $labels.proxy }}' has no active backend"
      summary: "All backends are down for the '{{ $labels.proxy }}' proxy"
  - alert: KeepalivedProcessDown
    expr: >-
      procstat_running{process_name="keepalived"} == 0
    labels:
      environment: "Production"
      severity: "warning"
      service: "keepalived"
    annotations:
      description: "Keepalived service is down on node {{ $labels.host }}"
      summary: "Keepalived service is down"
  - alert: CephPoolWriteOpsTooHighdefaultrgwbucketsindexnew1
    expr: >-
      ceph_pool_stats_write_op_per_sec{name="default.rgw.buckets.index.new1"} >  200.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new1 write ops too high."
      summary: "Ceph POOL default.rgw.buckets.index.new1 write ops too high"
  - alert: InfluxdbSeriesNumberHigh
    expr: >-
      influxdb_database_numSeries >= 9500000.0
    labels:
      environment: "Production"
      severity: "warning"
      service: "influxdb"
    annotations:
      description: "The InfluxDB {{ $labels.database }} database is getting close to the maximum number of series (value={{ $value }},threshold=9500000.0)."
      summary: "InfluxDB high number of series for {{ $labels.database }}"
  - alert: SystemSwapOut
    expr: >-
      rate(swap_out[2m]) > 1048576
    labels:
      environment: "Production"
      severity: "warning"
      service: "system"
    annotations:
      description: "The rate of swap output bytes is too high on node {{ $labels.host }} (current value={{ $value }}b/s, threshold=1048576b/s)."
      summary: "Swap output throughput too high on {{ $labels.host }}"
  - alert: HAproxyHeatCloudwatchApiHTTPResponse5xx
    expr: >-
      rate(haproxy_http_response_5xx{sv="FRONTEND",proxy="heat_cloudwatch_api"}[1m]) > 1
    for: 2m
    labels:
      environment: "Production"
      severity: "warning"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "Too many 5xx HTTP errors have been detected on the '{{ $labels.proxy }}' proxy for the last 2 minutes ({{ $value }} error(s) per second)"
      summary: "HTTP 5xx responses on '{{ $labels.proxy }}' proxy (host {{ $labels.host }})"
  - alert: CephPoolUsedSpaceCriticalcinderbackup
    expr: >-
      ceph_pool_usage_bytes_used{name="cinder-backup"} / ceph_pool_usage_max_avail{name="cinder-backup"} >  0.85 
    labels:
      environment: "Production"
      severity: "critical"
      service: "ceph"
    annotations:
      description: "Ceph POOL cinder-backup free space utilization critical. Run 'ceph df' to get details."
      summary: "Ceph POOL cinder-backup space utilization critical"
  - alert: SystemLoad5TooHigh
    expr: >-
      system_load5 / system_n_cpus > 3
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The 5-minutes system load is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=3)."
      summary: "High system load (5m) on {{ $labels.host }}"
  - alert: HAproxyRabbitmqClusterBackendCritical
    expr: >-
      (max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}[12h])) by (proxy)
       - min (haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}) by (proxy)
      ) / max(max_over_time(haproxy_active_servers{sv="BACKEND",proxy="rabbitmq_cluster"}[12h])) by (proxy) * 100 >= 50
    for: 5m
    labels:
      environment: "Production"
      severity: "critical"
      service: "haproxy/{{ $labels.proxy }}"
    annotations:
      description: "{{ $value }}% of backends are down for the '{{ $labels.proxy }}' proxy"
      summary: "Less than 50% of backends are up for the '{{ $labels.proxy }}' proxy for the last 5 minutes"
  - alert: ContrailSupervisordDatabaseProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-database"} == 0) >= count(procstat_running{process_name="contrail-supervisord-database"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-supervisord-database"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: ContrailNodemgrVrouterProcessWarning
    expr: >-
      count(procstat_running{process_name="contrail-nodemgr-vrouter"} == 0) >= count(procstat_running{process_name="contrail-nodemgr-vrouter"}) *0.3
    labels:
      environment: "Production"
      severity: "warning"
      service: "contrail-nodemgr-vrouter"
    annotations:
      description: "More than 30.0% of '{{ $labels.service }}' is down"
      summary: "More than 30.0% of '{{ $labels.service }}' is down"
  - alert: CephPoolReadOpsTooHighdefaultrgwbucketsindexnew
    expr: >-
      ceph_pool_stats_read_op_per_sec{name="default.rgw.buckets.index.new"} >  1000.0 
    labels:
      environment: "Production"
      severity: "warning"
      service: "ceph"
    annotations:
      description: "Ceph POOL default.rgw.buckets.index.new read ops too high."
      summary: "Ceph POOL default.rgw.buckets.index.new read ops too high"
  - alert: ApacheDown
    expr: >-
      apache_up != 1
    labels:
      environment: "Production"
      severity: "critical"
      service: "apache"
    annotations:
      description: "Apache service is down on node {{ $labels.host }}"
      summary: "Apache service down"
  - alert: ContrailSupervisordVrouterProcessDown
    expr: >-
      count(procstat_running{process_name="contrail-supervisord-vrouter"} == 0) == count(procstat_running{process_name="contrail-supervisord-vrouter"})
    labels:
      environment: "Production"
      severity: "critical"
      service: "contrail-supervisord-vrouter"
    annotations:
      description: "All '{{ $labels.service }}' services are down"
      summary: "All '{{ $labels.service }}' services are down"
                                                                                      telegraf/                                                                                           0000755 0000000 0000000 00000000000 13324134432 011344  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   telegraf/telegraf.d/                                                                                0000755 0000000 0000000 00000000000 13324134432 013357  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   telegraf/telegraf.d/input-processes.conf                                                            0000644 0000000 0000000 00000000025 13324134432 017366  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.processes]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           telegraf/telegraf.d/input-haproxy.conf                                                              0000644 0000000 0000000 00000000071 13324134432 017053  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.haproxy]]
servers = ["/run/haproxy/admin.sock"]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                       telegraf/telegraf.d/input-diskio.conf                                                               0000644 0000000 0000000 00000000022 13324134432 016637  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.diskio]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              telegraf/telegraf.d/input-system.conf                                                               0000644 0000000 0000000 00000000022 13324134432 016701  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.system]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              telegraf/telegraf.d/input-disk.conf                                                                 0000644 0000000 0000000 00000000201 13324134432 016306  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.disk]]
  ignore_fs = ["aufs", "rootfs", "sysfs", "proc", "devtmpfs", "devpts", "tmpfs", "fusectl", "cgroup", "overlay"]
                                                                                                                                                                                                                                                                                                                                                                                               telegraf/telegraf.d/input-http_listener.conf                                                        0000644 0000000 0000000 00000000200 13324134432 020237  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.http_listener]]
service_address = "127.0.0.1:8186"
read_timeout = "10s"
write_timeout = "10s"
tagexclude =["hostname"]
                                                                                                                                                                                                                                                                                                                                                                                                telegraf/telegraf.d/input-cpu.conf                                                                  0000644 0000000 0000000 00000000062 13324134432 016150  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.cpu]]
  totalcpu = true
  percpu = false
                                                                                                                                                                                                                                                                                                                                                                                                                                                                              telegraf/telegraf.d/input-kernel.conf                                                               0000644 0000000 0000000 00000000022 13324134432 016635  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.kernel]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              telegraf/telegraf.d/input-monitor_heka_cp.conf                                                      0000644 0000000 0000000 00000000343 13324134432 020524  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   
[[inputs.exec]]
commands =["bash -c 'for i in $(ls /var/cache/log_collector/output_queue/*/checkpoint.txt);do echo heka_output_checkpoint,checkpoint=$i value=$(cut -d\\  -f2 $i);done'"]
interval = "60s"
data_format = "influx"
                                                                                                                                                                                                                                                                                             telegraf/telegraf.d/input-monitor_heka.conf                                                         0000644 0000000 0000000 00000000155 13324134432 020043  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   
[[inputs.exec]]
commands =["/usr/local/bin/monitor_heka_queues.sh"]
interval = "60s"
data_format = "influx"
                                                                                                                                                                                                                                                                                                                                                                                                                   telegraf/telegraf.d/input-docker.conf                                                               0000644 0000000 0000000 00000000320 13324134432 016625  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.docker]]
  endpoint = "unix:///var/run/docker.sock"
  timeout = "5s"
  perdevice = true
  total = false
  gather_services = true
  container_name_exclude = ["*"]
namepass =["docker", "docker_swarm"]
                                                                                                                                                                                                                                                                                                                telegraf/telegraf.d/input-procstat.conf                                                             0000644 0000000 0000000 00000000437 13324134432 017226  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   
[[inputs.procstat]]
  pattern = "salt-minion"
  process_name = "salt-minion"
[[inputs.procstat]]
  exe = "keepalived"
  process_name = "keepalived"
[[inputs.procstat]]
  pattern = "node.*kibana"
  process_name = "kibana"
[[inputs.procstat]]
  exe = "dockerd"
  process_name = "dockerd"
                                                                                                                                                                                                                                 telegraf/telegraf.d/input-linux_sysctl_fs.conf                                                      0000644 0000000 0000000 00000000033 13324134432 020607  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.linux_sysctl_fs]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     telegraf/telegraf.d/input-swap.conf                                                                 0000644 0000000 0000000 00000000020 13324134432 016325  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.swap]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                telegraf/telegraf.d/output-prometheus_client.conf                                                   0000644 0000000 0000000 00000000066 13324134432 021317  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[outputs.prometheus_client]]
listen = "0.0.0.0:9126"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                          telegraf/telegraf.d/input-ping.conf                                                                 0000644 0000000 0000000 00000031322 13324134432 016321  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.ping]]
interval = "1m"
urls = ["ceph113.jpe4.jiocloud.com", "cmp247.jpe4.jiocloud.com", "ceph045.jpe4.jiocloud.com", "ceph055.jpe4.jiocloud.com", "cmp253.jpe4.jiocloud.com", "cmp127.jpe4.jiocloud.com", "cmp197.jpe4.jiocloud.com", "cmp062.jpe4.jiocloud.com", "cmp185.jpe4.jiocloud.com", "ceph108.jpe4.jiocloud.com", "rsl01.jpe4.jiocloud.com", "ctl04.jpe4.jiocloud.com", "cmp245.jpe4.jiocloud.com", "ceph047.jpe4.jiocloud.com", "ntw03.jpe4.jiocloud.com", "ceph104.jpe4.jiocloud.com", "kvm08.jpe4.jiocloud.com", "cmp001.jpe4.jiocloud.com", "cmp256.jpe4.jiocloud.com", "ceph050.jpe4.jiocloud.com", "cmp016.jpe4.jiocloud.com", "cmp236.jpe4.jiocloud.com", "ceph059.jpe4.jiocloud.com", "ceph038.jpe4.jiocloud.com", "cmp060.jpe4.jiocloud.com", "cmp258.jpe4.jiocloud.com", "ceph099.jpe4.jiocloud.com", "cmp125.jpe4.jiocloud.com", "ceph076.jpe4.jiocloud.com", "ceph112.jpe4.jiocloud.com", "ceph063.jpe4.jiocloud.com", "ceph056.jpe4.jiocloud.com", "cmp189.jpe4.jiocloud.com", "cmp249.jpe4.jiocloud.com", "cmp167.jpe4.jiocloud.com", "cmp194.jpe4.jiocloud.com", "ssd011.jpe4.jiocloud.com", "cmp116.jpe4.jiocloud.com", "ceph094.jpe4.jiocloud.com", "ceph061.jpe4.jiocloud.com", "ceph085.jpe4.jiocloud.com", "cmp104.jpe4.jiocloud.com", "mtr02.jpe4.jiocloud.com", "cmp242.jpe4.jiocloud.com", "cmp144.jpe4.jiocloud.com", "cmp029.jpe4.jiocloud.com", "cmp071.jpe4.jiocloud.com", "cmp135.jpe4.jiocloud.com", "ceph058.jpe4.jiocloud.com", "cmp235.jpe4.jiocloud.com", "ceph073.jpe4.jiocloud.com", "cmp246.jpe4.jiocloud.com", "nal01.jpe4.jiocloud.com", "cmp165.jpe4.jiocloud.com", "ceph090.jpe4.jiocloud.com", "ceph074.jpe4.jiocloud.com", "cmp146.jpe4.jiocloud.com", "ceph039.jpe4.jiocloud.com", "ceph100.jpe4.jiocloud.com", "ceph103.jpe4.jiocloud.com", "ceph010.jpe4.jiocloud.com", "cmp320.jpe4.jiocloud.com", "ceph009.jpe4.jiocloud.com", "ceph019.jpe4.jiocloud.com", "cmp067.jpe4.jiocloud.com", "cfg01.jpe4.jiocloud.com", "cmp241.jpe4.jiocloud.com", "ceph043.jpe4.jiocloud.com", "ceph077.jpe4.jiocloud.com", "cmp059.jpe4.jiocloud.com", "ceph042.jpe4.jiocloud.com", "cmp307.jpe4.jiocloud.com", "cmp122.jpe4.jiocloud.com", "cmp017.jpe4.jiocloud.com", "ceph026.jpe4.jiocloud.com", "ceph002.jpe4.jiocloud.com", "cmp280.jpe4.jiocloud.com", "kvm06.jpe4.jiocloud.com", "ceph015.jpe4.jiocloud.com", "ceph062.jpe4.jiocloud.com", "cmp051.jpe4.jiocloud.com", "ceph012.jpe4.jiocloud.com", "cmp120.jpe4.jiocloud.com", "cmp097.jpe4.jiocloud.com", "kvm14.jpe4.jiocloud.com", "cmp190.jpe4.jiocloud.com", "ceph065.jpe4.jiocloud.com", "ceph011.jpe4.jiocloud.com", "cmp264.jpe4.jiocloud.com", "cmp285.jpe4.jiocloud.com", "ceph007.jpe4.jiocloud.com", "cmp158.jpe4.jiocloud.com", "ceph025.jpe4.jiocloud.com", "cmp232.jpe4.jiocloud.com", "ceph082.jpe4.jiocloud.com", "ceph060.jpe4.jiocloud.com", "ceph064.jpe4.jiocloud.com", "ceph109.jpe4.jiocloud.com", "cmp088.jpe4.jiocloud.com", "kvm18.jpe4.jiocloud.com", "ssd013.jpe4.jiocloud.com", "cmp108.jpe4.jiocloud.com", "cmp134.jpe4.jiocloud.com", "nal02.jpe4.jiocloud.com", "kvm11.jpe4.jiocloud.com", "ceph014.jpe4.jiocloud.com", "cmp319.jpe4.jiocloud.com", "cmp260.jpe4.jiocloud.com", "cmp279.jpe4.jiocloud.com", "ceph008.jpe4.jiocloud.com", "kvm16.jpe4.jiocloud.com", "cmp266.jpe4.jiocloud.com", "ceph096.jpe4.jiocloud.com", "ceph049.jpe4.jiocloud.com", "cmp086.jpe4.jiocloud.com", "ceph093.jpe4.jiocloud.com", "cmp234.jpe4.jiocloud.com", "cmp211.jpe4.jiocloud.com", "cmp074.jpe4.jiocloud.com", "ceph-mon01.jpe4.jiocloud.com", "cmp216.jpe4.jiocloud.com", "cmp002.jpe4.jiocloud.com", "ceph-mon06.jpe4.jiocloud.com", "ceph001.jpe4.jiocloud.com", "ceph086.jpe4.jiocloud.com", "mtr01.jpe4.jiocloud.com", "kvm03.jpe4.jiocloud.com", "kvm15.jpe4.jiocloud.com", "cmp212.jpe4.jiocloud.com", "cmp218.jpe4.jiocloud.com", "ceph075.jpe4.jiocloud.com", "cmp237.jpe4.jiocloud.com", "cmp076.jpe4.jiocloud.com", "cmp095.jpe4.jiocloud.com", "cmp053.jpe4.jiocloud.com", "cmp169.jpe4.jiocloud.com", "kvm21.jpe4.jiocloud.com", "cmp007.jpe4.jiocloud.com", "ceph101.jpe4.jiocloud.com", "ceph020.jpe4.jiocloud.com", "cmp206.jpe4.jiocloud.com", "cmp058.jpe4.jiocloud.com", "kvm20.jpe4.jiocloud.com", "cmp221.jpe4.jiocloud.com", "cmp267.jpe4.jiocloud.com", "cmp009.jpe4.jiocloud.com", "ceph048.jpe4.jiocloud.com", "cmp025.jpe4.jiocloud.com", "log03.jpe4.jiocloud.com", "ntw01.jpe4.jiocloud.com", "cmp277.jpe4.jiocloud.com", "cmp012.jpe4.jiocloud.com", "cmp259.jpe4.jiocloud.com", "cmp270.jpe4.jiocloud.com", "cmp147.jpe4.jiocloud.com", "kvm25.jpe4.jiocloud.com", "cmp187.jpe4.jiocloud.com", "cmp003.jpe4.jiocloud.com", "cmp010.jpe4.jiocloud.com", "ceph080.jpe4.jiocloud.com", "cmp170.jpe4.jiocloud.com", "cmp229.jpe4.jiocloud.com", "cmp142.jpe4.jiocloud.com", "ssd009.jpe4.jiocloud.com", "cmp019.jpe4.jiocloud.com", "cmp303.jpe4.jiocloud.com", "prx02.jpe4.jiocloud.com", "cmp020.jpe4.jiocloud.com", "cmp075.jpe4.jiocloud.com", "ceph032.jpe4.jiocloud.com", "cmp207.jpe4.jiocloud.com", "ctl01.jpe4.jiocloud.com", "cmp027.jpe4.jiocloud.com", "cmp224.jpe4.jiocloud.com", "cmp128.jpe4.jiocloud.com", "cmp287.jpe4.jiocloud.com", "ceph005.jpe4.jiocloud.com", "cmp278.jpe4.jiocloud.com", "cmp314.jpe4.jiocloud.com", "cmp131.jpe4.jiocloud.com", "cmp313.jpe4.jiocloud.com", "cmp121.jpe4.jiocloud.com", "cmp072.jpe4.jiocloud.com", "cmp024.jpe4.jiocloud.com", "cmp139.jpe4.jiocloud.com", "cmp083.jpe4.jiocloud.com", "cmp248.jpe4.jiocloud.com", "dbs02.jpe4.jiocloud.com", "mon03.jpe4.jiocloud.com", "msg01.jpe4.jiocloud.com", "cmp239.jpe4.jiocloud.com", "cmp133.jpe4.jiocloud.com", "ctl03.jpe4.jiocloud.com", "cmp073.jpe4.jiocloud.com", "ssd004.jpe4.jiocloud.com", "cmp261.jpe4.jiocloud.com", "ceph118.jpe4.jiocloud.com", "cmp124.jpe4.jiocloud.com", "cmp033.jpe4.jiocloud.com", "cmp021.jpe4.jiocloud.com", "cmp180.jpe4.jiocloud.com", "cmp090.jpe4.jiocloud.com", "cmp013.jpe4.jiocloud.com", "ceph115.jpe4.jiocloud.com", "cmp304.jpe4.jiocloud.com", "cmp202.jpe4.jiocloud.com", "ceph004.jpe4.jiocloud.com", "cmp286.jpe4.jiocloud.com", "kvm01.jpe4.jiocloud.com", "cmp014.jpe4.jiocloud.com", "cmp129.jpe4.jiocloud.com", "ceph023.jpe4.jiocloud.com", "cmp036.jpe4.jiocloud.com", "nal03.jpe4.jiocloud.com", "cmp230.jpe4.jiocloud.com", "cmp208.jpe4.jiocloud.com", "cmp238.jpe4.jiocloud.com", "ceph-mon03.jpe4.jiocloud.com", "cmp213.jpe4.jiocloud.com", "cmp318.jpe4.jiocloud.com", "ceph017.jpe4.jiocloud.com", "cmp015.jpe4.jiocloud.com", "cmp227.jpe4.jiocloud.com", "ceph046.jpe4.jiocloud.com", "cmp244.jpe4.jiocloud.com", "cmp265.jpe4.jiocloud.com", "ssd010.jpe4.jiocloud.com", "cmp114.jpe4.jiocloud.com", "cmp057.jpe4.jiocloud.com", "ceph037.jpe4.jiocloud.com", "fnd01.jpe4.jiocloud.com", "cmp268.jpe4.jiocloud.com", "kvm27.jpe4.jiocloud.com", "cmp078.jpe4.jiocloud.com", "ceph126", "cmp040.jpe4.jiocloud.com", "cmp047.jpe4.jiocloud.com", "cmp137.jpe4.jiocloud.com", "cmp081.jpe4.jiocloud.com", "cmp254.jpe4.jiocloud.com", "ceph052.jpe4.jiocloud.com", "ceph006.jpe4.jiocloud.com", "cmp284.jpe4.jiocloud.com", "ceph057.jpe4.jiocloud.com", "cmp251.jpe4.jiocloud.com", "ceph-mon02.jpe4.jiocloud.com", "cmp262.jpe4.jiocloud.com", "cmp049.jpe4.jiocloud.com", "mtr03.jpe4.jiocloud.com", "ceph084.jpe4.jiocloud.com", "cmp275.jpe4.jiocloud.com", "log01.jpe4.jiocloud.com", "cmp136.jpe4.jiocloud.com", "ceph033.jpe4.jiocloud.com", "kvm13.jpe4.jiocloud.com", "ceph021.jpe4.jiocloud.com", "cmp201.jpe4.jiocloud.com", "cmp282.jpe4.jiocloud.com", "cmp263.jpe4.jiocloud.com", "cmp092.jpe4.jiocloud.com", "ceph095.jpe4.jiocloud.com", "ssd001.jpe4.jiocloud.com", "ceph098.jpe4.jiocloud.com", "mas01.jpe4.jiocloud.com", "cmp199.jpe4.jiocloud.com", "ceph097.jpe4.jiocloud.com", "cmp172.jpe4.jiocloud.com", "cmp079.jpe4.jiocloud.com", "kvm26.jpe4.jiocloud.com", "ceph036.jpe4.jiocloud.com", "cmp066.jpe4.jiocloud.com", "cmp008.jpe4.jiocloud.com", "cmp061.jpe4.jiocloud.com", "cmp119.jpe4.jiocloud.com", "kvm02.jpe4.jiocloud.com", "cmp184.jpe4.jiocloud.com", "cmp274.jpe4.jiocloud.com", "cmp091.jpe4.jiocloud.com", "cadf01.jpe4.jiocloud.com", "cmp316.jpe4.jiocloud.com", "cmp118.jpe4.jiocloud.com", "prx01.jpe4.jiocloud.com", "ceph114.jpe4.jiocloud.com", "ceph003.jpe4.jiocloud.com", "ceph022.jpe4.jiocloud.com", "cmp055.jpe4.jiocloud.com", "kvm04.jpe4.jiocloud.com", "cmp288.jpe4.jiocloud.com", "cmp306.jpe4.jiocloud.com", "cmp152.jpe4.jiocloud.com", "cmp173.jpe4.jiocloud.com", "cmp154.jpe4.jiocloud.com", "cmp188.jpe4.jiocloud.com", "ceph-mon04.jpe4.jiocloud.com", "ceph111.jpe4.jiocloud.com", "cmp214.jpe4.jiocloud.com", "cmp069.jpe4.jiocloud.com", "cmp163.jpe4.jiocloud.com", "dbs01.jpe4.jiocloud.com", "cmp026.jpe4.jiocloud.com", "ceph053.jpe4.jiocloud.com", "cmp255.jpe4.jiocloud.com", "ceph089.jpe4.jiocloud.com", "kvm24.jpe4.jiocloud.com", "cmp225.jpe4.jiocloud.com", "cmp096.jpe4.jiocloud.com", "cmp233.jpe4.jiocloud.com", "cmp301.jpe4.jiocloud.com", "ceph110.jpe4.jiocloud.com", "cmp283.jpe4.jiocloud.com", "cmp181.jpe4.jiocloud.com", "cmp149.jpe4.jiocloud.com", "ceph030.jpe4.jiocloud.com", "ceph106.jpe4.jiocloud.com", "cmp056.jpe4.jiocloud.com", "cmp300.jpe4.jiocloud.com", "cmp183.jpe4.jiocloud.com", "cmp084.jpe4.jiocloud.com", "cmp178.jpe4.jiocloud.com", "cmp193.jpe4.jiocloud.com", "ceph107.jpe4.jiocloud.com", "cmp089.jpe4.jiocloud.com", "cmp035.jpe4.jiocloud.com", "ceph051.jpe4.jiocloud.com", "cmp257.jpe4.jiocloud.com", "dbs03.jpe4.jiocloud.com", "cmp272.jpe4.jiocloud.com", "ceph079.jpe4.jiocloud.com", "ceph-mon05.jpe4.jiocloud.com", "cmp203.jpe4.jiocloud.com", "cmp215.jpe4.jiocloud.com", "cmp226.jpe4.jiocloud.com", "cmp219.jpe4.jiocloud.com", "kvm05.jpe4.jiocloud.com", "cmp031.jpe4.jiocloud.com", "cmp042.jpe4.jiocloud.com", "decapod.jpe4.jiocloud.com", "ceph117.jpe4.jiocloud.com", "ceph105.jpe4.jiocloud.com", "cmp175.jpe4.jiocloud.com", "cmp308.jpe4.jiocloud.com", "cmp077.jpe4.jiocloud.com", "cmp052.jpe4.jiocloud.com", "ctl02.jpe4.jiocloud.com", "cmp243.jpe4.jiocloud.com", "ceph041.jpe4.jiocloud.com", "cmp034.jpe4.jiocloud.com", "cmp217.jpe4.jiocloud.com", "cmp179.jpe4.jiocloud.com", "ceph-mon07.jpe4.jiocloud.com", "cmp196.jpe4.jiocloud.com", "ssd016.jpe4.jiocloud.com", "msg02.jpe4.jiocloud.com", "cmp005.jpe4.jiocloud.com", "cmp269.jpe4.jiocloud.com", "cmp273.jpe4.jiocloud.com", "cmp200.jpe4.jiocloud.com", "cmp050.jpe4.jiocloud.com", "kvm23.jpe4.jiocloud.com", "kvm10.jpe4.jiocloud.com", "cmp043.jpe4.jiocloud.com", "cmp157.jpe4.jiocloud.com", "cmp191.jpe4.jiocloud.com", "cmp064.jpe4.jiocloud.com", "cmp018.jpe4.jiocloud.com", "ceph016.jpe4.jiocloud.com", "ceph029.jpe4.jiocloud.com", "cmp250.jpe4.jiocloud.com", "cmp138.jpe4.jiocloud.com", "cmp054.jpe4.jiocloud.com", "cmp011.jpe4.jiocloud.com", "cmp171.jpe4.jiocloud.com", "cmp271.jpe4.jiocloud.com", "ceph081.jpe4.jiocloud.com", "mon02.jpe4.jiocloud.com", "ceph054.jpe4.jiocloud.com", "msg03.jpe4.jiocloud.com", "ctl05.jpe4.jiocloud.com", "log02.jpe4.jiocloud.com", "cmp222.jpe4.jiocloud.com", "ceph031.jpe4.jiocloud.com", "cmp140.jpe4.jiocloud.com", "ssd006.jpe4.jiocloud.com", "proxy.jpe4.jiocloud.com", "cmp186.jpe4.jiocloud.com", "cmp252.jpe4.jiocloud.com", "cmp065.jpe4.jiocloud.com", "ceph092.jpe4.jiocloud.com", "cmp161.jpe4.jiocloud.com", "cmp209.jpe4.jiocloud.com", "kvm12.jpe4.jiocloud.com", "cmp032.jpe4.jiocloud.com", "cmp195.jpe4.jiocloud.com", "cmp231.jpe4.jiocloud.com", "prx03.jpe4.jiocloud.com", "cmp132.jpe4.jiocloud.com", "ceph040.jpe4.jiocloud.com", "bmk01.jpe4.jiocloud.com", "kvm17.jpe4.jiocloud.com", "cmp317.jpe4.jiocloud.com", "cmp085.jpe4.jiocloud.com", "cmp312.jpe4.jiocloud.com", "cmp093.jpe4.jiocloud.com", "ntw02.jpe4.jiocloud.com", "kvm19.jpe4.jiocloud.com", "cmp045.jpe4.jiocloud.com", "cmp204.jpe4.jiocloud.com", "cmp004.jpe4.jiocloud.com", "ceph116.jpe4.jiocloud.com", "cmp126.jpe4.jiocloud.com", "cmp068.jpe4.jiocloud.com", "ssd015.jpe4.jiocloud.com", "cmp123.jpe4.jiocloud.com", "cmp150.jpe4.jiocloud.com", "cmp160.jpe4.jiocloud.com", "cmp030.jpe4.jiocloud.com", "cmp082.jpe4.jiocloud.com", "cmp022.jpe4.jiocloud.com", "cmp115.jpe4.jiocloud.com", "cmp228.jpe4.jiocloud.com", "cmp151.jpe4.jiocloud.com", "ceph066.jpe4.jiocloud.com", "kvm07.jpe4.jiocloud.com", "kvm09.jpe4.jiocloud.com", "mon01.jpe4.jiocloud.com", "ceph087.jpe4.jiocloud.com", "ceph018.jpe4.jiocloud.com", "cmp006.jpe4.jiocloud.com", "cmp063.jpe4.jiocloud.com", "ceph034.jpe4.jiocloud.com", "cmp315.jpe4.jiocloud.com", "cmp141.jpe4.jiocloud.com", "cmp198.jpe4.jiocloud.com", "ceph083.jpe4.jiocloud.com", "cmp044.jpe4.jiocloud.com", "cmp309.jpe4.jiocloud.com", "cmp048.jpe4.jiocloud.com", "ceph088.jpe4.jiocloud.com", "ssd012.jpe4.jiocloud.com", "cmp117.jpe4.jiocloud.com", "kvm22.jpe4.jiocloud.com", "cmp023.jpe4.jiocloud.com", "cmp143.jpe4.jiocloud.com", "cmp159.jpe4.jiocloud.com", "ceph102.jpe4.jiocloud.com", "ceph028.jpe4.jiocloud.com", "cmp070.jpe4.jiocloud.com", "cmp176.jpe4.jiocloud.com", "cmp205.jpe4.jiocloud.com", "cmp046.jpe4.jiocloud.com", "ceph091.jpe4.jiocloud.com", "ssd008.jpe4.jiocloud.com", "cmp298.jpe4.jiocloud.com", "cmp080.jpe4.jiocloud.com", "cmp087.jpe4.jiocloud.com", "cmp028.jpe4.jiocloud.com", "ceph027.jpe4.jiocloud.com", "ceph024.jpe4.jiocloud.com", "ceph035.jpe4.jiocloud.com"]
timeout = 1.0
count = 4
fieldpass =["percent_packet_loss"]
                                                                                                                                                                                                                                                                                                              telegraf/telegraf.d/input-ntp.conf                                                                  0000644 0000000 0000000 00000000044 13324134432 016162  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.ntpq]]
  dns_lookup = false                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            telegraf/telegraf.d/input-mem.conf                                                                  0000644 0000000 0000000 00000000017 13324134432 016137  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.mem]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 telegraf/telegraf.d/input-monitor_ssh_connection.conf                                               0000644 0000000 0000000 00000000201 13324134432 022137  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   
[[inputs.exec]]
commands =[ "/usr/local/bin/monitor_ssh_connection.sh" ]
timeout = "30s"
interval = "1m"
data_format = "influx"
                                                                                                                                                                                                                                                                                                                                                                                               telegraf/telegraf.d/input-net.conf                                                                  0000644 0000000 0000000 00000000017 13324134432 016147  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [[inputs.net]]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 