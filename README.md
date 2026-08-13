# Mini-Redis

A Redis-inspired distributed in-memory key-value store built from scratch in Python, implementing the core systems behind a distributed cache without relying on Redis itself.

The project evolved from a single-node TCP key-value server into a **three-node distributed system** supporting **WAL-based persistence, TTL and LRU caching, consistent hashing, horizontal sharding, request routing, primary-replica replication, version-based stale-write protection, failover, and node recovery**.

Rather than treating the database or cache as a black box, Mini-Redis explores how these mechanisms work together under **concurrent workloads, node failures, replication lag, and recovery scenarios**.

> **Storage → Persistence → Caching → Sharding → Routing → Replication → Failover → Recovery**
---

## Features

**Core Storage**
- In-memory key-value store over TCP
- Thread-safe concurrent operations
- `SET`, `GET`, `DEL`, `EXISTS`, `EXPIRE`, `VERSION`

**Persistence**
- Write-Ahead Logging (WAL)
- WAL replay for recovery after restart

**Caching**
- TTL-based key expiration
- LRU eviction with configurable capacity

**Distributed System**
- Consistent hashing and horizontal sharding
- Router-based request routing
- Primary-replica replication
- Version-based stale and duplicate replication protection
- Replica failure handling and primary failover
- Node recovery and restart/rejoin

**Testing**
- Unit and regression tests
- Concurrent and load testing
- Replication and stale-write tests
- Primary/replica failure tests
- TTL, WAL, and LRU tests
- Node recovery and rejoin tests
- Protocol validation tests
  
---

## Architecture

A **Router** sits in front of multiple independent Mini-Redis **nodes**. Each node owns a shard of the keyspace (determined by consistent hashing) and is backed by its own `Store`, `WAL`, TTL sweeper, and LRU eviction — plus a replica for fault tolerance.

```text
                         Client
                           │
                           │ TCP
                           ▼
                    ┌──────────────┐
                    │    Router    │
                    │              │
                    │  Hash Ring   │
                    │  Routing     │
                    │  Replication │
                    │  Failover    │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
         ┌───────┐     ┌───────┐     ┌───────┐
         │ Node1 │     │ Node2 │     │ Node3 │
         │ :6380 │     │ :6381 │     │ :6382 │
         └───┬───┘     └───┬───┘     └───┬───┘
             │             │             │
             ▼             ▼             ▼
          ┌──────┐      ┌──────┐      ┌──────┐
          │Store │      │Store │      │Store │
          └──┬───┘      └──┬───┘      └──┬───┘
             │             │             │
        ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
        ▼    ▼    ▼   ▼    ▼    ▼   ▼    ▼    ▼
       WAL  TTL  LRU WAL  TTL  LRU WAL  TTL  LRU
```

**Request flow:**
1. Client sends a command to the Router.
2. Router uses the consistent hash ring to determine the primary node responsible for the key.
3. Router forwards the request to the primary node.
4. For a write, the primary performs the operation and records the mutation in its WAL. The Router then sends a versioned replication request to the replica.
5. If the primary becomes unavailable, the Router detects the failure, removes it from the hash ring, reads from the replica, and promotes the replica for that key.
   
---

## Wire Protocol

| Command | Reply | Meaning |
|---|---|---|
| `PING` | `+PONG` | Health check |
| `SET <key> <value>` | `+OK` | Store/update a value |
| `GET <key>` | `+<value>` / `$-1` | Get value; `$-1` = key not found or expired |
| `DEL <key>` | `:1` / `:0` | Delete key; `1` = deleted, `0` = not found |
| `EXISTS <key>` | `:1` / `:0` | Check whether key exists |
| `EXPIRE <key> <seconds>` | `:1` / `:0` | Set TTL on an existing key |
| `VERSION <key>` | `:<version>` | Get current key version |
| `REPLSET <key> <value> <version>` | `+OK` / `+IGNORED` | Version-aware replica update |
| `-ERR <message>` | — | Invalid command or internal error |

---


**Run a single/multiple nodes:**
```bash
cd server
python3 node.py --port 6380 --node-id node1
python3 node.py --port 6381 --node-id node2
python3 node.py --port 6382 --node-id node3

nc localhost 6380 //for manual tests
```



---

## Project Structure

```
mini-redis/
├── server/
│   ├── store.py          # thread-safe in-memory store (LRU + TTL)
│   ├── node.py            # TCP server: protocol parsing, WAL wiring
│   ├── wal.py               # write-ahead log + crash-recovery replay
│   └── ttl.py                 # active TTL expiry sweeper (background thread)
├── cluster/
│   ├── hash_ring.py          # consistent hashing
│   ├── router.py               # client-facing routing layer
│   └── replication.py            # primary-replica sync, versioning, failover
├── client/
│   └── client.py                   # Python client library
├── tests/
│   ├── test_store.py                  # unit tests: LRU, TTL, core ops
│   ├── test_concurrent_clients.py       # many real socket clients at once
│   ├── test_crash_recovery.py             # kill -9 + WAL replay
│   ├── test_lru_crash_consistency.py        # eviction stays consistent across a crash
│   ├── test_hash_ring.py                       # key distribution + reshuffle-on-resize
│   ├── test_replication.py                       # primary/replica sync + failover
│   └── load_test.py                                 # throughput/latency under concurrent load
├── docker-compose.yml
└── README.md
```

---

Sharding and consistent hashing · replication and failover · durability via write-ahead logging · cache eviction policy design · protocol design · concurrency-safe systems programming · testing distributed failure modes, not just happy paths.
