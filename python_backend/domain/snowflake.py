import threading
import time

_lock = threading.Lock()
_last_timestamp = -1
_sequence = 0


def generate_snowflake() -> int:
    """Generate a 64-bit integer ID based on Unix Epoch (1970).

    Structure:
      - 41-48 bits: timestamp in milliseconds since 1970
      - 12 bits: sequence counter (supports up to 4096 IDs per millisecond)
    """
    global _last_timestamp, _sequence
    with _lock:
        now_ms = int(time.time() * 1000)
        if now_ms == _last_timestamp:
            _sequence = (_sequence + 1) & 0xFFF
            if _sequence == 0:
                # Sequence exhausted in current ms, wait for next ms
                while now_ms <= _last_timestamp:
                    now_ms = int(time.time() * 1000)
        else:
            _sequence = 0
        _last_timestamp = now_ms

        return (now_ms << 12) | (_sequence & 0xFFF)
