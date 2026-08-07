# Agent Runbook

This repo is Jess's fork of Mealie. The local Docker image is named `jess-mealie:pantry`, and the production-like local container is named `mealie`.

## Working Directory

Run commands from:

```bash
cd /Users/jessmann/Documents/jess-mealie
```

This workspace used to contain the real fork nested under `mealie-src/`. That layout was removed; the fork's `.git` directory now lives at the workspace root. If `git status --short --branch` does not show the expected branch from this directory, stop and inspect before building or starting containers.

## Data Safety

Persistent Mealie data lives outside the repo at:

```text
/Users/jessmann/Documents/jess-mealie/data
```

The Docker container mounts that directory at `/app/data`.

Do not delete, recreate, or overwrite `/Users/jessmann/Documents/jess-mealie/data`. It contains the SQLite database, uploaded images, PaddleOCR cache, and other persistent application data.

It is safe to stop/remove/recreate the `mealie` container as long as the same bind mount is used.

Feature branches can apply Alembic migrations to this SQLite database. Before switching between feature branches with different migrations, back up `data/mealie.db` and verify the current revision:

```bash
sqlite3 data/mealie.db "select * from alembic_version;"
```

For example, the receipts/OCR branch adds receipt tables and migration revisions that are not present on pantry-only `main`. Running a stale receipts image against `data/mealie.db` can leave the DB ahead of `main`; restore an appropriate manual backup before testing a branch that lacks those migrations.

## Colima And Docker

Check whether Colima/Docker is running:

```bash
colima status
docker ps
```

Start Colima if needed:

```bash
colima start
```

Jess's Mac has 24GB RAM. Colima was previously running with 3GiB, which is tight for PaddleOCR. Recommended setting:

```bash
colima stop
colima start --cpu 4 --memory 6
```

Use 8GiB if PaddleOCR remains memory-sensitive and the Mac is not under other heavy load. Avoid going above 12GiB unless intentionally dedicating the machine to Docker work.

Changing Colima memory restarts Docker and temporarily stops the app, but it should not affect the bind-mounted Mealie data directory.

## Build The Image

Build the current fork:

```bash
docker build -f docker/Dockerfile \
  --build-arg COMMIT=$(git rev-parse HEAD) \
  -t jess-mealie:pantry .
```

This can be slow because the image includes large Python/PaddleOCR/OpenCV dependencies.

Always rebuild after changing branches when testing branch isolation. The tag `jess-mealie:pantry` is mutable and may still point to an image built from another branch.

Useful preflight before starting:

```bash
git status --short --branch
git log --oneline -1
docker image inspect jess-mealie:pantry --format 'image={{.Id}} created={{.Created}}'
```

## Start Mealie

Do not use `docker start mealie` when branch correctness matters. That only restarts the existing named container and can resurrect a stale image from another branch, even if the source checkout is now correct.

Start the production-like local container:

```bash
docker rm -f mealie 2>/dev/null || true
docker run -d \
  --name mealie \
  --restart unless-stopped \
  -p 9925:9000 \
  -v /Users/jessmann/Documents/jess-mealie/data:/app/data \
  -e ALLOW_SIGNUP=false \
  -e PUID=501 \
  -e PGID=20 \
  -e TZ=America/New_York \
  -e BASE_URL=http://localhost:9925 \
  -e DEFAULT_GROUP=Home \
  -e DEFAULT_HOUSEHOLD=Family \
  -e DB_ENGINE=sqlite \
  jess-mealie:pantry
```

Check health:

```bash
docker ps
docker inspect -f '{{.State.Health.Status}}' mealie
```

Local URL:

```text
http://localhost:9925
```

Tailscale URL for phone access:

```text
https://jesss-macbook-air.tailb9fb10.ts.net
```

Tailscale Serve has been configured to proxy the no-port HTTPS URL to `http://localhost:9925`.

## Stop Mealie

Stop the running container:

```bash
docker stop mealie
```

Remove the stopped container before recreating it:

```bash
docker rm mealie
```

## Restart After Rebuild

After rebuilding `jess-mealie:pantry`, recreate the container with the same data mount:

```bash
docker rm -f mealie 2>/dev/null || true
docker run -d --name mealie --restart unless-stopped -p 9925:9000 \
  -v /Users/jessmann/Documents/jess-mealie/data:/app/data \
  -e ALLOW_SIGNUP=false \
  -e PUID=501 \
  -e PGID=20 \
  -e TZ=America/New_York \
  -e BASE_URL=http://localhost:9925 \
  -e DEFAULT_GROUP=Home \
  -e DEFAULT_HOUSEHOLD=Family \
  -e DB_ENGINE=sqlite \
  jess-mealie:pantry
```

After restart, verify the container is healthy and check which image it is using:

```bash
docker ps --filter name=^/mealie$
docker inspect -f 'image={{.Config.Image}} id={{.Image}} health={{.State.Health.Status}}' mealie
curl -I http://localhost:9925/
```

## Development Notes

There is also a hot-reload flow in `dev/hot-reload.sh`. Prefer hot reload for frontend/backend iteration when possible; rebuilding the full Docker image is slow.

Keep branch-specific notes on the branch that needs them. For example, receipt/OCR implementation notes belong on the receipts branch, not on pantry-only `main`.
