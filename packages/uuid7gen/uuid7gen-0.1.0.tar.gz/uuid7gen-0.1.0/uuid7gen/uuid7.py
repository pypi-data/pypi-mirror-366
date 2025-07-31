import time
import os
import uuid
from typing import List, Optional

__all__ = ["uuid7", "batch_uuid7"]

_UUID_VERSION: int = 7
_UUID_VARIANT: int = 0b10  # RFC 4122 variant bits
_EPOCH_START: int = 0  # Unix epoch start


def _get_timestamp_ms() -> int:
    """
    Return current Unix timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def uuid7(timestamp_ms: Optional[int] = None) -> uuid.UUID:
    # Error handling
    if timestamp_ms is not None:
        if not isinstance(timestamp_ms, (int, float)):
            raise TypeError("timestamp_ms must be an int or float representing milliseconds since Unix epoch.")
        if timestamp_ms < 0:
            raise ValueError("timestamp_ms must be non-negative.")
    """
    Generate a UUIDv7 according to RFC 9562 (including submillisecond support).

    Args:
        timestamp_ms: Optional[float] — milliseconds since Unix epoch. Can be float for submillisecond precision.
                      If None, current time is used.

    Returns:
        uuid.UUID instance representing the UUIDv7.

    Notes:
        - If timestamp_ms is a float, up to 12 bits of submillisecond precision are encoded in the UUID as per RFC 9562.
        - The function is compatible with Python <3.11.
    """
    if timestamp_ms is None:
        timestamp_ms = _get_timestamp_ms()

    # RFC 9562: timestamp_ms can be float for subms precision
    ts_int = int(timestamp_ms)
    ts_frac = float(timestamp_ms) - ts_int

    # Mask timestamp to 48 bits
    ts48: int = ts_int & ((1 << 48) - 1)
    ts_bytes: bytes = ts48.to_bytes(6, "big")

    # Generate 10 random bytes for randomness component
    rand_bytes: bytearray = bytearray(os.urandom(10))

    # RFC 9562: encode up to 12 bits of subms precision in first 12 bits of randomness
    # Subms precision: up to 0.999 ms, so 12 bits covers 0-4095
    subms = int(ts_frac * 4096)  # 12 bits
    # Set first 12 bits of rand_bytes
    rand_bytes[0] = (subms >> 4) & 0xFF
    rand_bytes[1] = ((subms & 0xF) << 4) | (rand_bytes[1] & 0x0F)

    # Combine timestamp and random parts
    uuid_bytes: bytearray = bytearray(ts_bytes + rand_bytes)

    # Set UUID version (7) in the upper nibble of byte 6 (index 6)
    uuid_bytes[6] &= 0x0F
    uuid_bytes[6] |= (_UUID_VERSION << 4) & 0xF0

    # Set UUID variant bits (10xx) in byte 8 (index 8)
    uuid_bytes[8] &= 0x3F
    uuid_bytes[8] |= (_UUID_VARIANT << 6) & 0xC0

    return uuid.UUID(bytes=bytes(uuid_bytes))


def batch_uuid7(
    n: int,
    timestamp_start_ms: Optional[int] = None,
    interval_ms: int = 1,
) -> List[uuid.UUID]:
    """
    Generate a batch of n UUIDv7s spaced by interval_ms milliseconds (supports submillisecond intervals).

    Args:
        n: number of UUIDs to generate
        timestamp_start_ms: optional starting timestamp in ms (float for subms, current time if None)
        interval_ms: time spacing between UUID timestamps in ms (can be float for subms)

    Returns:
        List of uuid.UUID objects

    Notes:
        - Submillisecond intervals are supported and encoded as per RFC 9562.
    """
    # Error handling
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer.")
    if timestamp_start_ms is not None:
        if not isinstance(timestamp_start_ms, (int, float)):
            raise TypeError("timestamp_start_ms must be an int or float representing milliseconds since Unix epoch.")
        if timestamp_start_ms < 0:
            raise ValueError("timestamp_start_ms must be non-negative.")
    if not isinstance(interval_ms, (int, float)):
        raise TypeError("interval_ms must be an int or float representing milliseconds.")
    if interval_ms < 0:
        raise ValueError("interval_ms must be non-negative.")

    if timestamp_start_ms is None:
        timestamp_start_ms = _get_timestamp_ms()

    return [uuid7(timestamp_ms=timestamp_start_ms + i * interval_ms) for i in range(n)]