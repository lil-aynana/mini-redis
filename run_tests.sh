#!/bin/bash

set -e

echo "========================================"
echo "        MINI-REDIS TEST SUITE"
echo "========================================"

echo
echo "[1/10] Store tests"
PYTHONPATH=. python3 tests/test_store.py

echo
echo "[2/10] TTL tests"
PYTHONPATH=. python3 tests/test_ttl.py

echo
echo "[3/10] LRU tests"
PYTHONPATH=. python3 tests/test_lru.py

echo
echo "[4/10] WAL tests"
PYTHONPATH=. python3 tests/test_wal.py

echo
echo "[5/10] Concurrent mixed operations"
PYTHONPATH=. python3 tests/test_concurrent_mixed.py

echo
echo "[6/10] Stale replication"
PYTHONPATH=. python3 tests/test_stale_replication.py

echo
echo "[7/10] Protocol errors"
PYTHONPATH=. python3 tests/test_protocol_errors.py

echo
echo "[8/10] Replication load"
PYTHONPATH=. python3 tests/test_replication_load.py

echo
echo "[9/10] TTL + replication"
PYTHONPATH=. python3 tests/test_ttl_replication.py

echo
echo "[10/10] Load distribution"
PYTHONPATH=. python3 tests/test_load_distribution.py

echo
echo "========================================"
echo "       ALL REGRESSION TESTS PASSED"
echo "========================================"
