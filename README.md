# Mini-Redis

A Redis-inspired distributed in-memory key-value database built from scratch in Python.

Mini-Redis started as a single-node TCP key-value server and evolved into a distributed storage system with persistence, caching, consistent hashing, sharding, replication, failover, version-based conflict protection, and node recovery.

The project was built incrementally to understand the core systems concepts behind real-world databases, caches, and distributed storage systems.

---

## 🚀 Features

### Core Storage

- In-memory key-value storage
- TCP client-server architecture
- Thread-safe concurrent operations
- `SET`
- `GET`
- `DEL`
- `EXISTS`
- `EXPIRE`
- `VERSION`

### Persistence

- Write-Ahead Logging (WAL)
- WAL replay during startup
- Crash recovery
- Data persistence across server restarts

### Caching

- TTL-based key expiration
- LRU cache eviction
- Configurable maximum key capacity

### Distributed System

- Consistent hashing
- Horizontal sharding
- Request routing
- Primary-replica replication
- Version-based replication
- Stale replication protection
- Replica failure tolerance
- Primary failure detection
- Replica promotion
- Failover
- Node recovery
- Version-aware recovery synchronization

### Testing

- Unit tests
- Concurrent operation tests
- Load tests
- Replication tests
- Failure tests
- Recovery tests
- TTL regression tests
- WAL crash recovery tests
- Protocol validation tests
- Stale replication tests
- Node restart/rejoin tests

---

# 🏗️ Architecture

The system consists of clients, a router, distributed storage nodes, replication, and local storage components.

```text
                         Clients
                            │
                            │ TCP
                            ▼
                     ┌──────────────┐
                     │    Router    │
                     │              │
                     │ Hash Ring     │
                     │ Routing      │
                     │ Failover     │
                     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
          ┌───────┐     ┌───────┐     ┌───────┐
          │ Node1 │     │ Node2 │     │ Node3 │
          └───┬───┘     └───┬───┘     └───┬───┘
              │             │             │
              ▼             ▼             ▼
           Store          Store          Store
              │             │             │
        ┌─────┼─────┐ ┌─────┼─────┐ ┌─────┼─────┐
        ▼     ▼     ▼ ▼     ▼     ▼ ▼     ▼     ▼
       WAL   TTL   LRU WAL   TTL   LRU WAL   TTL   LRU
