# Mini-Redis

A Redis-inspired in-memory key-value database built from scratch in Python.

The project starts as a single-node TCP key-value server and progressively evolves into a distributed Redis-like system with persistence, TTL, LRU eviction, consistent hashing, sharding, routing, and replication.

---

## 🚀 Project Goals

The goal of this project is to understand and implement core concepts behind real-world distributed databases and caching systems.

The project focuses on:

- TCP networking
- Client-server architecture
- Concurrency and thread safety
- In-memory data storage
- Write-Ahead Logging (WAL)
- Data recovery
- TTL-based expiration
- LRU cache eviction
- Consistent hashing
- Horizontal sharding
- Request routing
- Replication
- Load testing
- Fault tolerance

---

# 🏗️ Current Architecture

```text
                         Client
                           │
                           │ TCP
                           ▼
                    ┌──────────────┐
                    │   Mini-Redis │
                    │     Node     │
                    │   node.py    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Store     │
                    │  store.py    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          HashMap         TTL           LRU
              │
              ▼
             WAL
              │
              ▼
             Disk
