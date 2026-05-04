# Upstream service definitions for the API gateway.
# Container DNS names resolve via the investbyyourself-network bridge.
#
# This file uses the .inc extension so it is NOT auto-loaded by the
# `include /etc/nginx/conf.d/*.conf;` glob in nginx.prod.conf - it is
# loaded explicitly (once) from there.

upstream etl_backend {
    server etl-service:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream analysis_backend {
    server financial-analysis-service:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream data_backend {
    server data-service:8002 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
