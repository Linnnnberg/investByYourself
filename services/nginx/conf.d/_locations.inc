# Reusable location blocks shared between HTTP (bring-up) and HTTPS server blocks.
# Included from default.conf via `include /etc/nginx/conf.d/_locations.inc;`.
#
# This file uses the .inc extension so it is NOT auto-loaded by the
# `include /etc/nginx/conf.d/*.conf;` glob in nginx.prod.conf.

# Common proxy headers
proxy_http_version 1.1;
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Request-ID      $request_id;
proxy_set_header Connection        "";

proxy_connect_timeout 10s;
proxy_send_timeout    60s;
proxy_read_timeout    60s;

# Gateway health (works without backend services).
location = /health {
    access_log off;
    add_header Content-Type text/plain;
    return 200 "ok\n";
}

# ETL service - data ingestion endpoints.
location /api/etl/ {
    limit_req zone=api_general burst=60 nodelay;
    proxy_pass http://etl_backend/;
}

# Financial analysis service - computation endpoints.
location /api/analysis/ {
    limit_req zone=api_strict burst=20 nodelay;
    proxy_pass http://analysis_backend/;
}

# Data service - read endpoints (companies, prices, ratios).
location /api/data/ {
    limit_req zone=api_general burst=60 nodelay;
    proxy_pass http://data_backend/;
}

# Per-service health checks (no rate limiting, used by orchestrator).
location = /api/etl/health      { access_log off; proxy_pass http://etl_backend/health; }
location = /api/analysis/health { access_log off; proxy_pass http://analysis_backend/health; }
location = /api/data/health     { access_log off; proxy_pass http://data_backend/health; }

# Deny dotfiles and common scanner targets.
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
}
