# Jaeger Interface

This sub-package ships a **thin synchronous wrapper** around the
[Jaeger Query Service](https://www.jaegertracing.io/docs/) HTTP API so
that you can **search for and retrieve traces** directly from Python
with minimal boilerplate. It also provides **client-side span filtering**
capabilities for more granular control over the returned data.

> The client relies on `requests` (already included in the SDK's
> dependencies) and uses *pydantic* for full type-safety.

---

## Installation

`veris-ai` already lists both `requests` and `pydantic` as hard
requirements, so **no additional dependencies are required**.

```bash
pip install veris-ai
```

---

## Quick-start

```python
from veris_ai.jaeger_interface import JaegerClient
import json
from veris_ai.jaeger_interface.models import Trace
# Replace with the URL of your Jaeger Query Service instance
client = JaegerClient("http://localhost:16686")

# --- 1. Search traces --------------------------------------------------
resp = client.search(
    service="veris-agent",
    limit=10,
    # operation="CustomSpanData",
    tags={"veris.session_id":"088b5aaf-84bd-4768-9a62-5e981222a9f2"},
    span_tags={"bt.metadata.model":"gpt-4.1-2025-04-14"}
)

# save to json
with open("resp.json", "w") as f:
    f.write(resp.model_dump_json(indent=2))

# Guard clause
if not resp or not resp.data:
    print("No data found")
    exit(1)

# Print trace ids
for trace in resp.data:
    if isinstance(trace, Trace):
        print("TRACE ID:", trace.traceID, len(trace.spans), "spans")

# --- 2. Retrieve a specific trace -------------------------------------
if isinstance(resp.data, list):
    trace_id = resp.data[0].traceID
else:
    trace_id = resp.data.traceID

detailed = client.get_trace(trace_id)
# save detailed to json
with open("detailed.json", "w") as f:
    f.write(detailed.model_dump_json(indent=2))
```

---

## API Reference

### `JaegerClient`

| Method | Description |
| -------- | ----------- |
| `search(service, *, limit=None, tags=None, operation=None, span_tags=None, **kwargs) -> SearchResponse` | Search for traces with optional span-level filtering. |
| `get_trace(trace_id: str) -> GetTraceResponse` | Fetch a single trace by ID (wrapper around `/api/traces/{id}`). |

### `search()` Parameters

The `search()` method now uses a flattened parameter structure:

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `service` | `str` | Service name to search for. Optional - if not provided, searches across all services. |
| `limit` | `int` | Maximum number of traces to return. |
| `tags` | `Dict[str, Any]` | Trace-level tag filters (AND logic). A trace must have a span matching ALL tags. |
| `operation` | `str` | Filter by operation name. |
| `span_tags` | `Dict[str, Any]` | Span-level tag filters (OR logic). Returns only spans matching ANY of these tags. | 
| `span_operations` | `List[str]` | Span-level operation name filters (OR logic). Returns only spans matching ANY of these operations. |
| `**kwargs` | `Any` | Additional parameters passed directly to Jaeger API. |

### Filter Logic

The interface provides two levels of filtering:

1. **Trace-level filtering** (`tags` parameter):
   - Sent directly to Jaeger API
   - Uses AND logic: all tag key-value pairs must match on a single span
   - Efficient server-side filtering

2. **Span-level filtering** (`span_tags` parameter):
   - Applied client-side after retrieving traces
   - Uses OR logic: spans matching ANY of the provided tags are included
   - Traces with no matching spans are excluded from results
   - Useful for finding spans with specific characteristics across different traces

### Example: Combining Filters

```python
# Find traces in service that have errors, then filter to show only 
# spans with specific HTTP status codes or database errors
traces = client.search(
    service="my-api",
    tags={"error": "true"},  # Trace must contain an error
    span_tags={
        "http.status_code": 500,
        "http.status_code": 503,
        "db.error": "connection_timeout"
    }  # Show only spans with these specific errors
)
```

---

## Compatibility

The implementation targets **Jaeger v1.x** REST endpoints. For clusters
backed by **OpenSearch** storage the same endpoints apply. Should you
need API v3 support feel free to open an issue or contribution—thanks!

---

## License

This package is released under the **MIT license**.