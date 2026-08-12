# mini-redis — Day 1: Single-Node Store

A distributed key-value store built from scratch (no Redis dependency) —
this is the Day 1 slice: a single node handling `GET`/`SET`/`DEL`/`EXISTS`
over a real TCP socket, with a thread-safe in-memory store underneath.

Zero external dependencies — pure Python 3 standard library (`socket`,
`threading`). No `pip install` needed.

## Project layout

```
mini-redis/
├── server/
│   ├── store.py     # thread-safe in-memory hashmap (the data layer)
│   └── node.py       # TCP server: parses commands, calls into store.py
├── client/
│   └── client.py      # Python client library — also your test harness
├── tests/
│   ├── test_store.py             # unit tests for store.py (no network)
│   └── test_concurrent_clients.py # 20 real concurrent socket clients
└── README.md
```

## Run it

**Terminal 1 — start a node:**
```bash
cd server
python3 node.py --port 6380 --node-id node1
```

**Terminal 2 — talk to it:**
```bash
cd client
python3 client.py
```
Or manually, with netcat:
```bash
nc localhost 6380
SET foo bar
GET foo
DEL foo
```

## Wire protocol (Day 1 version)

A simplified, human-readable version of Redis' real RESP protocol —
readable enough to test with `nc`, structured enough to extend later.

| Client sends | Server replies | Meaning |
|---|---|---|
| `PING` | `+PONG` | health check |
| `SET key value` | `+OK` | value is everything after the key — spaces allowed |
| `GET key` | `+value` or `$-1` | `$-1` = nil, key not found |
| `DEL key` | `:1` or `:0` | 1 = deleted, 0 = didn't exist |
| `EXISTS key` | `:1` or `:0` | |

Errors: `-ERR <message>`

## Tests

```bash
# Unit tests — store.py logic only, no network involved
python3 tests/test_store.py -v

# Integration test — requires node.py running in another terminal first
python3 tests/test_concurrent_clients.py
```

**Verified so far:**
- 8/8 unit tests passing (GET/SET/DELETE, overwrite, missing-key edge cases, concurrent in-process writes)
- 20 concurrent real socket clients × 50 SET+GET pairs each = 1000 ops, zero errors

## Design notes

- **One thread per connection** in `node.py`. Fine at this scale; a production
  node would likely use an event loop (`asyncio`) to avoid thread overhead at
  high connection counts — a known, deliberate tradeoff for this project.
- **Lock in `store.py`**: without it, concurrent writes from multiple client
  threads can corrupt the underlying dict or produce lost writes. The
  `test_concurrent_writes_do_not_corrupt_state` test in `test_store.py` is
  what actually justifies this — remove the lock and rerun it to see why.

## What's next (Day 2)

- LRU eviction (bounded memory, evict least-recently-used key first)
- TTL / key expiry (lazy check-on-read + active background sweep)
- Write-Ahead Log for crash recovery (kill `-9` the process, restart, data survives)
