# InvestByYourself API Gateway (Nginx)

Production reverse proxy and TLS terminator that fronts the microservices defined
in `services/docker-compose.yml`.

## Layout

```
services/nginx/
  nginx.prod.conf        # Main nginx config (mounted at /etc/nginx/nginx.conf)
  conf.d/
    upstreams.inc        # Backend service upstream definitions (explicitly included)
    default.conf         # HTTP/HTTPS server blocks (auto-loaded by *.conf glob)
    _locations.inc       # Shared location blocks (included from server blocks)
  ssl/                   # TLS certificates (gitignored, see SSL setup below)
```

## Routing

| Path prefix       | Upstream                          | Rate limit |
| ----------------- | --------------------------------- | ---------- |
| `/api/etl/`       | `etl-service:8000`                | 30 req/s   |
| `/api/analysis/`  | `financial-analysis-service:8001` | 10 req/s   |
| `/api/data/`      | `data-service:8002`               | 30 req/s   |
| `/health`         | nginx itself                      | -          |
| `/gateway/health` | nginx itself                      | -          |

## Bring-up (no TLS yet)

For initial deployment without certificates:

1. In `conf.d/default.conf`, comment out the `return 301 https://...` line in
   the port 80 server block.
2. Uncomment the `include /etc/nginx/conf.d/_locations.inc;` line in the same
   server block.
3. Start the stack:

   ```bash
   cd services
   docker-compose --compatibility \
     -f docker-compose.yml -f docker-compose.prod.yml \
     up -d api-gateway
   ```

4. Verify routing:

   ```bash
   curl http://localhost/health
   curl http://localhost/api/data/health
   ```

## SSL setup

### Option A: Let's Encrypt with certbot (recommended)

Run certbot in standalone mode on the host (gateway must be stopped) or use
the `certbot/certbot` image:

```bash
# Stop the gateway temporarily
docker-compose -f services/docker-compose.yml -f services/docker-compose.prod.yml stop api-gateway

# Issue certificate (replace example values)
docker run --rm -it \
  -p 80:80 \
  -v "$(pwd)/services/nginx/ssl:/etc/letsencrypt/live/api.example.com" \
  certbot/certbot certonly --standalone \
  --preferred-challenges http \
  -d api.example.com \
  --email ops@example.com --agree-tos --no-eff-email

# Copy fullchain.pem and privkey.pem into services/nginx/ssl/
# (certbot writes symlinks; copy the actual files for the bind mount)
```

### Option B: Bring your own certificate

Place these files in `services/nginx/ssl/`:

- `fullchain.pem` - certificate chain (cert + intermediates)
- `privkey.pem` - private key, `chmod 600`

### Enable HTTPS

1. In `conf.d/default.conf`:
   - Restore the `return 301 https://...` redirect in the port 80 block
     (default state).
   - Uncomment the entire `server { listen 443 ssl ... }` block.
   - Set `server_name` to your real hostname.
2. Restart the gateway:

   ```bash
   docker-compose -f services/docker-compose.yml -f services/docker-compose.prod.yml \
     up -d --force-recreate api-gateway
   ```
3. Test:

   ```bash
   curl -I https://api.example.com/health
   # Optional: full SSL Labs grade
   # https://www.ssllabs.com/ssltest/analyze.html?d=api.example.com
   ```

### Auto-renewal (Let's Encrypt)

Add a cron job on the host to renew and reload nginx (zero-downtime via
`nginx -s reload`):

```cron
0 3 * * 1 docker run --rm \
  -v /path/to/services/nginx/ssl:/etc/letsencrypt/live/api.example.com \
  certbot/certbot renew --quiet && \
  docker exec investbyyourself-api-gateway nginx -s reload
```

## Validating config changes

Always test config syntax inside the running container before reloading:

```bash
docker exec investbyyourself-api-gateway nginx -t
docker exec investbyyourself-api-gateway nginx -s reload
```

## Logs

JSON-formatted access logs are written to `/var/log/nginx/access.log` inside the
container and stream to Docker's logging driver:

```bash
docker logs -f investbyyourself-api-gateway
```

## Security notes

- The `ssl/` directory is gitignored. Never commit real certificates or private
  keys.
- Rate limit zones (`api_general`, `api_strict`) are defined in
  `nginx.prod.conf`. Adjust based on observed traffic.
- HSTS is enabled in the HTTPS block with a 2-year max-age. Roll back the
  max-age first if you need to disable HTTPS in the future.
- The default redirect from HTTP to HTTPS is intentional. Disabling it
  permanently is not recommended.
