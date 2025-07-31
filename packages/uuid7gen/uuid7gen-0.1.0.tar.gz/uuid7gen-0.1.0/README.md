
# uuid7gen

A lightweight and pure-Python implementation of UUIDv7 for Python versions < 3.11. Fully compatible with [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html), including submillisecond precision.

## Installation

```bash
pip install uuid7gen
```

## Usage


### Generate a single UUIDv7 (with optional submillisecond precision)

```python
from uuid7gen import uuid7

id = uuid7()
print(id)

# Example output (ms precision):
# 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7c

# Generate with submillisecond precision
timestamp_ms = 1620000000123.456  # float, ms since epoch
id_subms = uuid7(timestamp_ms=timestamp_ms)
print(id_subms)

# Example output (subms precision):
# 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7d
```


### Generate a batch of UUIDv7s (supports subms intervals)

```python
from uuid7gen import batch_uuid7

ids = batch_uuid7(5, timestamp_start_ms=1620000000123.0, interval_ms=0.1)
for i, id in enumerate(ids):
    print(f"{i+1}: {id}")

# Example output:
# 1: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7c
# 2: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7d
# 3: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7e
# 4: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7f
# 5: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c80
```

### Visual representations of a UUIDv7

```python
id = uuid7()
print("standard string:", id)
print("bytes:", id.bytes)
print("hex:", id.hex)
print("int:", id.int)
print("urn:", id.urn)

# Example output:
# standard string: 018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7c
# bytes: b'\x01\x8en|{|\x7f|\xbf|||||||'
# hex: 018e6e7c7b7c7f7cbf7c7c7c7c7c7c7c7c
# int: 212345678901234567890123456789012345
# urn: urn:uuid:018e6e7c-7b7c-7f7c-bf7c-7c7c7c7c7c7c
```


---

**Features:**
- RFC 9562 compliant (including submillisecond encoding)
- Python <3.11 compatible
- Batch generation with subms intervals

For more details, see the [documentation](https://github.com/yourname/uuid7gen).