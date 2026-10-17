"""Counts paid model calls, so cost claims are measured instead of estimated.

The counter lives in process memory: run uvicorn with a single worker when
benchmarking, or the numbers are split across processes.
"""
from collections import Counter
import logging

log = logging.getLogger("usage")
calls: Counter = Counter()


def record(kind: str) -> None:
    calls[kind] += 1
    log.info("paid_call kind=%s total=%d", kind, calls[kind])
