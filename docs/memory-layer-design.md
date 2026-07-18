# Hermes Agent Knowledge Graph — Memory Layer Design


## Overview

This document defines the schema and architecture for a shared memory layer across the Hermes Agent network. The knowledge graph will serve as a persistent, queryable memory system that every agent can access — enabling cross-agent memory sharing, skill discovery, documentation lookup, and context-aware responses.

## Current Graph State

- **Neo4j 5.24** on `x1-370` (primary)
- **80M+ nodes** currently (PhoneLog: 19.9M, DashcamEmbedding: 4.2M, YOLODetection: 4.1M, Frame: 3.7M, etc.)
- **Vector indexes** already exist for: DashcamEmbedding, DetectedObject, Frame, Segment, GlobalSpeaker, Transcription, Utterance
- **Password**: `knowledge_graph_2026`
- **Data path**: `/media/scott/S/neo4j/data` (S drive)
- **Backups**: `/media/scott/NAS5/fileserver/neo4j-bkps/`

## Design Considerations

### 1. Schema Isolation

**Problem**: The graph already has 80M+ nodes. Adding memory nodes without isolation creates noise in queries.

**Solution**: Use **labels** as logical namespaces. All memory-layer nodes get a `MemoryLayer` base label plus a specific type label. This allows:
- Efficient filtering: `MATCH (n:MemoryLayer:AgentMemory)` 
- No schema conflicts with existing data
- Easy to add more namespaces later (e.g., `IngestLayer`, `NetworkLayer`)

### 2. Embedding Strategy

**Problem**: 80M nodes already consume significant disk space. Adding vector embeddings for memory nodes adds storage overhead.

**Solution**: 
- Use **dimensionality appropriate to the embedding model** (not default 1536)
- Store embeddings as `float[]` arrays (Neo4j native vector type)
- Consider **sparse vs dense** embeddings — use sparse for large text (skills, docs) and dense for semantic search (memories, preferences)
- **Embedding model**: Start with a local model (e.g., `sentence-transformers/all-MiniLM-L6-v2` at 384 dims) to avoid API costs, or OpenAI `text-embedding-3-small` (1536 dims) for quality

### 3. Agent Access Patterns

**Problem**: Each agent on the network needs to query the graph efficiently.

**Solution**:
- **Direct bolt connection** from each agent to the Neo4j instance (port 7687)
- Each agent has a **service account** or uses the existing `neo4j` user
- **Query templates** stored as Cypher procedures or documented patterns
- **Caching layer**: Each agent caches frequently-accessed memories locally (in ~/.hermes/memory/)
- **Sync mechanism**: Cron job to push local memory files → graph periodically

### 4. Data Model for Memories

**Problem**: Current hermes-agent memory uses flat text files in `~/.hermes/memory/`. Need to migrate and extend this.

**Solution**: Map existing memory concepts to graph nodes:

```
UserMemory — persistent user facts and preferences
AgentMemory — agent-specific memories (soul, capabilities, routing)
SystemMemory — system-level knowledge (architecture, procedures, skills)
ContextMemory — temporary/contextual memories (session-specific)
SkillMemory — skill definitions and metadata
DocMemory — documentation, architecture docs, references
```

### 5. Vector Search Integration

**Problem**: How to make vector search accessible to agents?

**Solution**: 
- Create **vector indexes** for searchable node types
- Expose **Cypher procedures** for common search patterns
- Document **query templates** agents can use
- Consider **GDS (Graph Data Science)** for advanced similarity computations

### 6. Synchronization & Freshness

**Problem**: How do memories stay up-to-date across agents?

**Solution**:
- **Push model**: Each agent pushes its local memories → graph (cron or on-demand)
- **Pull model**: Agents pull relevant memories on startup or when needed
- **Hybrid**: Local cache + periodic sync + on-demand refresh
- **Versioning**: Track `updated_at` timestamps; agents detect stale memories

## Schema Design

### Node Labels

```
:MemoryLayer — base label for all memory-layer nodes
:UserMemory — persistent user facts and preferences
:AgentMemory — agent-specific memories
:SystemMemory — system-level knowledge
:ContextMemory — temporary/contextual memories
:SkillMemory — skill definitions
:DocMemory — documentation
:Agent — agent inventory (each agent in the network)
```

### Node Properties

#### UserMemory
```cypher
{
  id: string,           // unique identifier
  category: string,     // preference, habit, fact, relationship, location
  source: string,       // where it came from (e.g., "user_correction", "session", "import")
  content: string,      // the actual memory text
  confidence: float,    // 0.0-1.0, how certain we are
  created_at: datetime,
  updated_at: datetime,
  expires_at: datetime, // optional, for temporary memories
  embedding: vector     // 384 or 1536-dim vector
}
```

#### AgentMemory
```cypher
{
  id: string,
  agent_name: string,   // e.g., "destroyer", "optiplex", "x1-370"
  agent_id: string,     // machine identifier
  soul_file: string,    // path to soul file
  model_provider: string,
  model_name: string,
  capabilities: string, // comma-separated list of available tools
  routing_rules: string, // delegation rules
  last_seen: datetime,
  status: string,       // "online", "offline", "unknown"
  embedding: vector
}
```

#### SystemMemory
```cypher
{
  id: string,
  category: string,     // "architecture", "procedure", "configuration", "troubleshooting"
  content: string,
  references: string,   // comma-separated list of referenced files/URLs
  created_at: datetime,
  updated_at: datetime,
  embedding: vector
}
```

#### SkillMemory
```cypher
{
  id: string,
  name: string,
  description: string,
  category: string,
  trigger: string,      // when to use this skill
  path: string,         // skill file path
  created_at: datetime,
  updated_at: datetime,
  embedding: vector
}
```

#### DocMemory
```cypher
{
  id: string,
  title: string,
  content: string,
  path: string,         // file path or URL
  category: string,     // "architecture", "reference", "procedure", "api"
  created_at: datetime,
  updated_at: datetime,
  updated_at: datetime,
  embedding: vector
}
```

#### Agent (Inventory)
```cypher
{
  id: string,
  name: string,
  hostname: string,
  tailnet: string,      // Tailscale tailnet
  model_provider: string,
  model_name: string,
  tools: string,        // available tools
  last_seen: datetime,
  status: string
}
```

### Relationship Types

```cypher
(:UserMemory)-[:BELONGS_TO]->(:Agent)
(:AgentMemory)-[:BELONGS_TO]->(:Agent)
(:SystemMemory)-[:REFERENCES]->(:DocMemory)
(:SkillMemory)-[:PART_OF]->(:SystemMemory)
(:DocMemory)-[:REFERENCES]->(:DocMemory)
(:Agent)-[:HAS_MEMORY]->(:UserMemory)
(:Agent)-[:HAS_MEMORY]->(:AgentMemory)
(:Agent)-[:HAS_SKILL]->(:SkillMemory)
(:Agent)-[:HAS_DOC]->(:DocMemory)
```

### Vector Indexes

```cypher
// For semantic search on memories
CREATE VECTOR INDEX memory_user_search IF NOT EXISTS
  FOR (n:UserMemory) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } }

// For agent discovery
CREATE VECTOR INDEX memory_agent_search IF NOT EXISTS
  FOR (n:AgentMemory) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } }

// For skill discovery
CREATE VECTOR INDEX memory_skill_search IF NOT EXISTS
  FOR (n:SkillMemory) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } }

// For documentation search
CREATE VECTOR INDEX memory_doc_search IF NOT EXISTS
  FOR (n:DocMemory) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 384, `vector.similarity_function`: 'cosine' } }
```

## Query Patterns

### 1. Find relevant user memories for an agent

```cypher
// Agent queries for memories relevant to its user
WITH vector.similarity([0.1, 0.2, ...], m.embedding) AS score
RETURN m.content, score
ORDER BY score DESC
LIMIT 10
```

### 2. Find skills matching a task

```cypher
// When an agent needs to accomplish something
WITH vector.similarity([0.1, 0.2, ...], s.embedding) AS score
RETURN s.name, s.description, score
ORDER BY score DESC
LIMIT 5
```

### 3. Find related documentation

```cypher
// Agent looks up architecture docs
MATCH (doc:DocMemory)
WHERE doc.category = 'architecture'
WITH doc, vector.similarity([0.1, 0.2, ...], doc.embedding) AS score
RETURN doc.title, doc.content, score
ORDER BY score DESC
LIMIT 3
```

### 4. Agent inventory with status

```cypher
MATCH (a:Agent)
RETURN a.name, a.hostname, a.status, a.last_seen, a.model_name
ORDER BY a.last_seen DESC
```

### 5. Cross-agent memory sharing

```cypher
// Agent A shares a memory with Agent B
MATCH (a1:Agent {name: 'agent-a'}), (a2:Agent {name: 'agent-b'})
CREATE (mem:UserMemory {
  id: 'shared:123',
  content: 'User prefers concise responses',
  category: 'preference',
  source: 'agent-a',
  created_at: datetime(),
  updated_at: datetime()
})
CREATE (mem)-[:SHARED_WITH]->(a2)
```

## Synchronization Strategy

### Local → Graph (Push)

```bash
# Each agent runs this periodically
# 1. Read local memory files
# 2. Generate embeddings
# 3. Upsert to graph (MERGE by id)
# 4. Mark as updated
```

### Graph → Local (Pull)

```cypher
// On agent startup or when needed
MATCH (mem:UserMemory)-[:BELONGS_TO]->(agent:Agent {name: 'my-agent'})
WHERE mem.updated_at > agent.last_sync
RETURN mem
```

### Sync Cron Jobs

```
# Push local memories → graph (every 15 minutes)
# Pull graph memories → local cache (on startup)
# Cleanup expired memories (daily)
```

## Implementation Plan

### Phase 1: Schema & Indexes (This Session)
- [ ] Create node labels and properties
- [ ] Create vector indexes
- [ ] Import existing memories from `~/.hermes/memory/`
- [ ] Import existing skills from `~/.hermes/skills/`
- [ ] Import agent inventory from `~/.hermes/souls/`
- [ ] Import key docs from `~/.hermes/` and `/home/scott/git/chat/docs/`

### Phase 2: Agent Integration
- [ ] Create Cypher query templates for each agent
- [ ] Update agent soul files to include graph access config
- [ ] Create sync scripts for each agent
- [ ] Test vector search from agent context

### Phase 3: Automation & Optimization
- [ ] Set up cron jobs for sync
- [ ] Add memory expiration and cleanup
- [ ] Implement GDS similarity computations
- [ ] Add memory importance scoring

### Phase 4: Cross-Agent Features
- [ ] Memory sharing between agents
- [ ] Conflict resolution for shared memories
- [ ] Memory versioning and rollback
- [ ] Memory importance decay over time

## Data Volume Considerations

**Current graph**: ~80M nodes, ~70GB backup
**Memory layer estimate**: 
- User memories: ~100-500 nodes
- Agent memories: ~10-20 nodes
- Skills: ~50-100 nodes
- Docs: ~20-50 nodes
- **Total**: ~200-700 nodes (negligible compared to existing graph)

**Storage impact**: 
- Each embedding: 384 dims × 4 bytes = 1.5 KB
- 700 nodes × 1.5 KB = ~1 MB for embeddings
- Memory content: ~100 KB total
- **Total overhead**: < 2 MB (insignificant)

## Security Considerations

- **Authentication**: Use existing `neo4j` user with password from docker-compose
- **Network**: Bolt port 7687 accessible via Tailscale from all agents
- **Data isolation**: Memory layer nodes are clearly labeled; no risk of polluting auto-ingest queries
- **Write access**: Agents can write their own memories; shared memories require explicit sharing relationship

## Migration from Current Memory System

**Current system**: Flat text files in `~/.hermes/memory/`
**New system**: Graph nodes with vector embeddings

**Migration steps**:
1. Read each memory file
2. Parse metadata (category, confidence, source)
3. Generate embeddings
4. Create graph nodes with MERGE (idempotent)
5. Update `last_sync` timestamp on each agent node

**Rollback**: Keep local files; graph is supplemental. If graph fails, agents fall back to local files.
