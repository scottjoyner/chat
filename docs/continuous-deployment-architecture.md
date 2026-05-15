---
title: Continuous Deployment Architecture
summary: Full CD pipeline design for x1-370 home infrastructure covering Docker services, Neo4j, auto-ingest, Paperclip, and Hermes Agent.
---

# Continuous Deployment Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTINUOUS DEPLOYMENT PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Code → Build → Test → Stage → Deploy → Verify → Monitor                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Stages

### 1. Code (Source)

```
Local Git Workflows:
┌─────────────────────────────────────────────────────────────────────────────┐
│ scottjoyner/chat       ← Architecture diagrams, docs                        │
│ scottjoyner/hermes-agent  ← Agent framework (fork)                          │
│ scottjoyner/auto-ingest ← Content OS pipeline                               │
│ scottjoyner/paperclip    ← Agent orchestration (local + remote)             │
│ scottjoyner/lms          ← LM Studio homelab                                │
│ scottjoyner/phonelog     ← Phone logging                                    │
│ scottjoyner/tts          ← Text-to-speech                                   │
│ scottjoyner/stt          ← Speech-to-speech                                 │
│ scottjoyner/auto-assist  ← Auto-assist                                      │
│ scottjoyner/rustdesk     ← Remote desktop (fork)                            │
│ scottjoyner/fleet        ← Fleet management                                 │
│ scottjoyner/minio-audit  ← MinIO audit                                      │
│ scottjoyner/auto-collect ← GPS logger (fork)                                │
│ scottjoyner/benchmark-SSD← SSD benchmarking                                 │
│ scottjoyner/llm-geometry ← LLM geometry                                     │
│ scottjoyner/consult      ← Consulting                                        │
│ scottjoyner/generated_text← Text generation                                 │
│ scottjoyner/G1a          ← Gen 1a                                           │
│ scottjoyner/tigerchain   ← Tigerchain                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Build

```
Build Targets by Service:

┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Compose Services (docker-compose.yml)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ signal-cli     → bbernhard/signal-cli-rest-api:latest (pull from Docker Hub)│
│ nginx          → nginx:alpine (pull from Docker Hub)                        │
│ neo4j          → neo4j:5.24 (pull from Docker Hub)                          │
│ nextcloud      → nextcloud:latest (pull from Docker Hub)                    │
│ db             → mariadb:10.6 (pull from Docker Hub)                        │
│ redis          → redis:alpine (pull from Docker Hub)                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Auto-Ingest (content_os)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Source: /home/scott/git/auto-ingest/                                        │
│ Build: Python package (content_os.cli, content_os.core, content_os.models)  │
│ Test: pytest (unit, integration, docker)                                    │
│ Deploy: Direct file copy + import path update                               │
│ Config: CONTENT_OS_LLM_* env vars                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Paperclip                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Source: /home/scott/git/paperclip/ (S drive + local)                        │
│ Build: pnpm build (ui + server + packages)                                  │
│ Test: pnpm test (unit + e2e)                                                │
│ Deploy: Docker container or direct Express.js                               │
│ Config: .env, database connection, adapter keys                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Hermes Agent                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Source: /home/scott/git/hermes-agent/                                       │
│ Build: Python venv (.venv)                                                  │
│ Test: scripts/run_tests.sh (CI-parity, xdist -n 4)                          │
│ Deploy: hermes-cli install / pip install                                    │
│ Config: ~/.hermes/config.yaml, ~/.hermes/.env                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Test

```
Test Strategy by Service:

┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Services                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Pre-deploy: docker compose config (validate syntax)                         │
│ Post-deploy: docker compose ps (verify all running)                         │
│ Health: curl to exposed ports (80, 443, 7474)                              │
│ Backup: neo4j backup before upgrade (neo4j-bkps on NAS)                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Auto-Ingest                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Unit tests: content_os/test/ (pytest)                                       │
│ Integration: test/docker/ (pytest, docker-compose)                          │
│ Data validation: Neo4j graph integrity check                                │
│ Content verification: proof-backed runs                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Paperclip                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Unit tests: packages/*/src/__tests__/ (jest)                                │
│ E2E tests: tests/e2e/ (Playwright)                                          │
│ Smoke tests: scripts/smoke/                                                   │
│ Adapter tests: claude-local, codex-local validation                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Hermes Agent                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Full suite: scripts/run_tests.sh (CI-parity)                                │
│ Directory: tests/agent/, tests/gateway/, tests/tools/, tests/optional/      │
│ Workers: -n 4 (CI parity)                                                   │
│ Coverage: ~17k tests across ~900 files                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Stage

```
Staging Strategy:

┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Compose Services                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Staging: docker compose -f docker-compose.yml down && up                    │
│ Rollback: docker compose down && docker pull old                            │
│ Data safety: NAS backups before any change                                  │
│ Neo4j: backup to /media/scott/NAS/fileserver/neo4j-bkps/ before upgrade    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Auto-Ingest                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Staging: content_os/ runs in dry-run mode (no auto-publish)                 │
│ Validation: proof-backed content runs                                       │
│ Human review: approved runs only                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Paperclip                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Staging: separate Paperclip instance on same server                         │
│ DB: separate PostgreSQL schema                                                │
│ Test: run heartbeat cycle against staging                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Hermes Agent                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Staging: hermes-cli gateway on alternate port                               │
│ Config: ~/.hermes/config.yaml (override for staging)                        │
│ Test: run gateway with staging config, verify sessions                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5. Deploy

```
Deployment Methods by Service:

┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Compose Services (Primary)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Command: docker compose -f /home/scott/docker-compose/docker-compose.yml up │
│          -d --pull always                                                   │
│ Health check: curl -f http://localhost:80/health                            │
│ Rollback: docker compose down && docker pull <old-image> && docker compose  │
│          up -d                                                              │
│ Schedule: cron job for automated updates (with manual approval)             │
│ Network: internal (bridge) + external (bridge)                              │
│ Data persistence: 9 named Docker volumes + S drive mount for Neo4j         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Neo4j (Special)                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Pre-deploy: neo4j-admin dump --to=/media/scott/NAS/fileserver/neo4j-bkps/   │
│ Post-deploy: neo4j-admin restore --from=/path/to/backup                     │
│ Data path: /media/scott/S/neo4j/data (S drive, NOT Docker volume)          │
│ Logs: /media/scott/S/neo4j/logs                                             │
│ Import: /media/scott/S/neo4j/import                                          │
│ Backup retention: neo4j-v1.dump (5.1GB), neo4j-2025-09-26T05-43-25.backup │
│          (5.7GB)                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Auto-Ingest                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Deploy: content_os/ code updates (direct file copy)                         │
│ Config: CONTENT_OS_LLM_* environment variables                              │
│ Data: NAS fileserver (dashcam, bodycam, headcam, audio, transcriptions)    │
│ Workflow: captured → idea_review → brief_ready → drafting → verification →  │
│           human_review → approved → scheduler_ready → scheduled → published │
│ Safety: human approval gates at verification and approved stages            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Paperclip                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Deploy: docker compose or direct Express.js restart                         │
│ Source: /media/scott/S/paperclip/ (S drive) + /home/scott/git/paperclip/    │
│ DB: PostgreSQL (connection via env vars)                                      │
│ Adapters: claude-local, codex-local, process, http                          │
│ Config: .env, skill definitions, agent configurations                       │
│ Heartbeat: scheduler → adapter invocation → agent work → result capture     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Hermes Agent                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Deploy: hermes-cli install / pip install                                    │
│ Config: ~/.hermes/config.yaml (settings), ~/.hermes/.env (API keys)         │
│ Skills: ~/.hermes/skills/ (loaded at runtime)                               │
│ Memory: ~/.hermes/memory/ (persistent user memory)                          │
│ Logs: ~/.hermes/logs/ (agent.log, errors.log, gateway.log)                  │
│ Gateway: hermes_cli.main gateway run --replace                              │
│ Cron: hermes cronjob (scheduled agent runs)                                 │
│ Session: SQLite with FTS5 search (hermes_state.py)                          │
│ Platform: Telegram, Discord, Slack, Signal, Home Assistant, Matrix, SMS     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6. Verify

```
Verification by Service:

┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Services                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ docker compose ps → all 6 services running                                  │
│ curl http://localhost:80/ → nginx responds                                  │
│ curl http://localhost:7474/ → Neo4j responds                                │
│ docker compose logs --tail=50 → no errors                                   │
│ NAS backup exists → /media/scott/NAS/fileserver/neo4j-bkps/                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Auto-Ingest                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ content_os.cli health check                                                   │
│ Neo4j graph integrity (node/edge counts match expected)                       │
│ File system: NAS files accessible                                              │
│ Quality API: transcript_service responds                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Paperclip                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Express.js API health endpoint                                                │
│ PostgreSQL connection test                                                    │
│ Adapter connectivity (claude-local, codex-local)                              │
│ Heartbeat cycle test                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Hermes Agent                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ hermes-cli health check                                                       │
│ Gateway session store (SQLite) accessible                                     │
│ Skill system loaded                                                           │
│ Tool registry registered                                                      │
│ Platform connections (Telegram/Discord/Slack)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7. Monitor

```
Monitoring by Service:

┌─────────────────────────────────────────────────────────────────────────────┐
│ System Monitoring                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ CPU: 24 cores (LM Studio + Hermes + Neo4j are heavy)                        │
│ RAM: 91 GB total, 48 GB used, 43 GB available                               │
│ Swap: 8 GB (2.2 GB used)                                                    │
│ Disk: nvme1n1p6 (root), nvme0n1p3 (S drive), /dev/sda2 (NAS)               │
│ Network: 192.168.1.241/24 + Tailscale                                       │
│ Docker: container health checks (Neo4j has built-in healthcheck)             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Service Monitoring                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Signal CLI: REST API port 8400 health check                                 │
│ Neo4j: 7474/7687 port checks, heap usage (4G max)                          │
│ Nextcloud: 8081 port check, NAS mount status                                │
│ Paperclip: API health, PostgreSQL connection                                │
│ Hermes: gateway process, session store, skill loading                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┤
│ Log Monitoring                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Agent logs: ~/.hermes/logs/agent.log (INFO+)                                │
│ Errors: ~/.hermes/logs/errors.log (WARNING+)                                │
│ Gateway: ~/.hermes/logs/gateway.log                                          │
│ Docker: docker compose logs (nginx, neo4j, nextcloud)                       │
│ System: journalctl, dmesg                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │  Code    │    │  Build   │    │  Test    │    │  Deploy  │            │
│  │  (Git)   │───▶│  (Local) │───▶│  (pytest)│───▶│  (Docker │            │
│  └──────────┘    └──────────┘    └──────────┘    │  + Docker│            │
│       ▲                  │                         │  Compose)│            │
│       │                  ▼                         └──────────┘            │
│  ┌──────────┐    ┌──────────┐                                             │
│  │  Verify  │◀───│  Stage   │                                             │
│  │  (curl)  │    │  (NAS    │                                             │
│  └──────────┘    │  backup) │                                             │
│       ▲          └──────────┘                                             │
│       │                  │                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Monitor  │◀───│  Docker  │◀───│  Neo4j   │◀───│  Signal  │            │
│  │ (logs)   │    │  Compose │    │  (S drv) │    │  CLI     │            │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Auto-    │    │ Paperclip│    │ Hermes   │    │ Nextcloud│            │
│  │ Ingest   │    │ (S drv)  │    │ Agent    │    │ (NAS)    │            │
│  │ (NAS)    │    │          │    │ (hermes) │    │          │            │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Rollback Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ROLLBACK STRATEGY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Docker Services:                                                           │
│  1. docker compose down                                                     │
│  2. docker pull <previous-image>                                            │
│  3. docker compose up -d                                                    │
│  4. Verify all services running                                              │
│                                                                             │
│  Neo4j:                                                                     │
│  1. docker compose down                                                     │
│  2. Restore from /media/scott/NAS/fileserver/neo4j-bkps/                    │
│  3. docker compose up -d                                                    │
│  4. Verify graph integrity                                                   │
│                                                                             │
│  Auto-Ingest:                                                               │
│  1. Restore content_os/ from last known good version                        │
│  2. Verify file system mounts                                                │
│  3. Verify Neo4j data integrity                                              │
│                                                                             │
│  Paperclip:                                                                 │
│  1. Restore /media/scott/S/paperclip/ from last backup                      │
│  2. Restart Express.js service                                               │
│  3. Verify API health                                                        │
│                                                                             │
│  Hermes Agent:                                                              │
│  1. hermes-cli install <previous-version>                                   │
│  2. Restore ~/.hermes/config.yaml from backup                               │
│  3. Restart gateway                                                          │
│  4. Verify platform connections                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Safety Checklist

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA SAFETY CHECKLIST                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Before ANY deployment:                                                     │
│  □ Verify NAS mount: /media/scott/NAS/fileserver/ is mounted                │
│  □ Verify S drive mount: /media/scott/S/ is mounted                         │
│  □ Check disk space: df -h (ensure >20% free)                              │
│  □ Check RAM: free -h (ensure >10GB available)                             │
│  □ Backup Neo4j: neo4j-admin dump → neo4j-bkps/                            │
│  □ Verify docker compose config: docker compose config                     │
│  □ Check signal-cli config: ~/.local/share/signal-cli/                     │
│  □ Verify hermes config: ~/.hermes/config.yaml                             │
│  □ Check platform connections: Telegram/Discord/Slack                       │
│                                                                             │
│  After deployment:                                                          │
│  □ All Docker services running: docker compose ps                           │
│  □ Neo4j accessible: curl http://localhost:7474/                            │
│  ✓ Signal CLI accessible: curl http://localhost:8400/                       │
│  ✓ Nextcloud accessible: curl http://localhost:8081/                        │
│  ✓ Paperclip API health: curl http://localhost:<port>/health                │
│  ✓ Hermes gateway running: hermes-cli status                                │
│  ✓ NAS files accessible: ls /media/scott/NAS/fileserver/                    │
│  ✓ S drive files accessible: ls /media/scott/S/                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
