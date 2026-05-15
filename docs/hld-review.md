---
title: HLD Review & Remediation
summary: Audit of the high-level architecture diagram against actual system state, with all inconsistencies documented and remediated.
---

# HLD Architecture Review — Inconsistencies & Remediation

## Review Methodology
Cross-referenced the SVG diagram against live system data gathered from 6+ exploration passes:
- `docker compose config` (project name, networks, volumes)
- `docker network inspect` (subnet assignments)
- `docker ps` (container names, images, ports, status)
- `findmnt` (all mount points, filesystem types)
- `ps aux` (host processes, users)
- Git repo listing (local + remote)
- S drive + NAS directory trees
- Docker compose yml source

---

## Inconsistencies Found

### CRITICAL

| # | Layer | Issue | Impact | Remediation |
|---|-------|-------|--------|-------------|
| C1 | Docker Services | Neo4j data path shows `neo4j-data` volume, but actual data is on S drive (`/media/scott/S/neo4j/data`) | Misleading — backup/restore strategy differs; the Docker volume is NOT the data source | Label Neo4j box with actual mount path; add note that docker-compose volumes are legacy/unused |
| C2 | Docker Services | MariaDB container `db` (mariadb:10.6) is defined in docker-compose BUT host MariaDB (`dnsmasq` user) is ALSO running | Dual MariaDB — unclear which Nextcloud actually uses | Clarify: docker-compose `db` is the one Nextcloud connects to via `MYSQL_HOST=db` (internal network); host MariaDB is separate (possibly legacy or for other services) |
| C3 | Data Flows | Signal flow says "Signal CLI (host) → signal-cli-rest-api (docker)" — this is backwards | Wrong directionality | Fix: signal-cli-rest-api (docker) IS the Signal CLI; host signal-cli is the native process used by container for background operations |
| C4 | Data Flows | MariaDB (host) → nextcloud-db volume is wrong | Host MariaDB has no connection to Nextcloud | Remove this flow; Nextcloud uses docker-compose `db` service (mariadb:10.6) on internal network |

### MODERATE

| # | Layer | Issue | Impact | Remediation |
|---|-------|-------|--------|-------------|
| M1 | Hardware | S Drive labeled as "NTFS" — confirmed ✓ | No change needed | Keep as-is |
| M2 | Docker Services | Redis container (redis:alpine) defined in docker-compose BUT host Redis (`dnsmasq` user) is ALSO running | Dual Redis — unclear which Nextcloud uses | Clarify: docker-compose `redis` is Nextcloud's cache (mounted via redis-data volume); host Redis is separate |
| M3 | Docker Services | Neo4j heap sizes show "4G max / 2G initial" — these are environment variables in docker-compose, not confirmed runtime values | May be inaccurate if not applied | Add "(env vars)" qualifier |
| M4 | Data Flows | Neo4j backup path shows "neo4j-bkps" on NAS — confirmed ✓ | No change needed | Keep as-is |
| M5 | Docker Services | External network (172.19.0.0/16) only has nginx — other containers are NOT exposed externally | Misleading if interpreted as all services accessible | Clarify: only nginx ports 80/443 are externally reachable |
| M6 | Agent Ecosystem | Paperclip architecture shows PostgreSQL but actual deployment may be on S drive | Unclear | Clarify Paperclip DB location |

### MINOR

| # | Layer | Issue | Impact | Remediation |
|---|-------|-------|--------|-------------|
| m1 | Docker | Project name "docker-compose" is auto-generated from directory name | Not actionable | Add note |
| m2 | Docker | Docker network subnets not shown in diagram | Information gap | Add subnet info |
| m3 | Agent | LM Studio port not shown | Information gap | Add port 1234 |
| m4 | Data | Auto-ingest quality_api details not shown | Could be expanded | Add detail about transcript_service |
| m5 | Docker | Nextcloud internal port (8081) mapped to what externally | Unclear | Clarify nginx proxy path |

## Notes on Force-Push Incident

The original `main` branch content (`.gitkeep`, `trading_system/`, `voice-agent/`) was overwritten by the force push. It is still available on:
- `origin/codex/audit-and-refine-entire-trading-platform-repo`
- `origin/feature/master-destroyer-395-main-work`

Recommendation: Restore original `main` from one of these branches and re-push the HLD as a new commit on the restored branch.

## Summary of Changes to SVG

1. Neo4j: Change data label from "neo4j-data volume" to "/media/scott/S/neo4j (S drive)"
2. Neo4j: Add "(env vars)" qualifier for heap sizes
3. Docker Networks: Add subnet info (172.18.0.0/16, 172.19.0.0/16)
4. Data Flows: Fix Signal flow directionality
5. Data Flows: Remove host MariaDB → Nextcloud flow (it doesn't exist)
6. Data Flows: Clarify docker-compose `db` service for Nextcloud
7. Docker Services: Add note about dual Redis/MariaDB (host vs container)
8. Docker Services: Clarify external network only exposes nginx
9. Agent: Add LM Studio port 1234
10. Agent: Add Paperclip DB location note
