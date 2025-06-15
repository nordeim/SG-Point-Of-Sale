Below is an updated version of your **`docker-compose.dev.yml`** adjusted to use the **Postgres v16 Alpine** image. I also double‑checked that `postgres:16-alpine` is available and supported in Docker Hub ([hub.docker.com][1]).

---

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: sgpos_dev_db
    env_file:
      - .env.dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

volumes:
  postgres_dev_data:
    driver: local
```

---

### 🛠️ What changed and why

* **Image tag updated**: Changed from `postgres:15-alpine` to `postgres:16-alpine`, which is indeed the current major version available and maintained for Alpine as of mid‑2025 .
* **Volume path remains unchanged**: The default data directory (`/var/lib/postgresql/data`) continues to match the new image, so no volume path adjustments are necessary.
* **Healthcheck and ports stay the same**: These configurations remain valid for Postgres 16.

---

### ✅ Next steps

1. **Spin it up**:

   ```bash
   docker-compose -f docker-compose.dev.yml up -d db
   ```

2. **Verify logs**:

   ```bash
   docker logs sgpos_dev_db
   ```

3. **Check the running version**:

   ```bash
   docker exec sgpos_dev_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();"
   ```

This should confirm that you're using **PostgreSQL 16.x running on Alpine**.

---

### Considerations

* **Pinning a minor version?**
  If you want to lock to the latest minor release (e.g., 16.8), update the image to `postgres:16.8-alpine` to avoid surprise behavior during patch updates ([hahouari.medium.com][2], [docker.com][3]).

* **Initialize scripts**
  If your setup uses `.sql` or `.sh` files in `./docker-entrypoint-initdb.d/`, they will continue to run on first init. No changes needed.

* **Upgrading production data**
  If you plan to migrate existing data from v15 to v16, be aware: major-version upgrades require either a dump/restore or container-based pg\_upgrade. This is usually not relevant in dev environments.

---

Let me know if you want help with version pinning (e.g. `16.8-alpine`), rollback strategies, or any further optimizations!

[1]: https://hub.docker.com/layers/library/postgres/16-alpine/images/sha256-c8598bfad5366cfae78bf7fb337cdd94ddd3f326f7c67239ee036da801e73f08?utm_source=chatgpt.com "Image Layer Details - postgres:16-alpine | Docker Hub"
[2]: https://hahouari.medium.com/upgrade-from-postgresql-16-x-to-17-0-in-docker-compose-00d7417fd555?utm_source=chatgpt.com "Upgrade from PostgreSQL 16.x to 17.0 in Docker Compose"
[3]: https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/?utm_source=chatgpt.com "How to Use the Postgres Docker Official Image"

---
https://chatgpt.com/share/684ece50-ca04-8000-a15c-1cdd49ae8b63

