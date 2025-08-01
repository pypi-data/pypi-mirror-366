# Analytics Ingest Client

A lightweight Python library to batch and push automotive telemetry data—such as signals, Diagnostic Trouble Codes (DTCs), GPS data, and network statistics—to a GraphQL backend.

---

## 🔧 Features

- Supports Python 3.11+
- Clean, single-class interface: `IcsAnalytics`
- In-memory caching for resolved IDs (message id or configuration)
- Batching support (by interval, count, or signal limit)
- Async-safe request queuing (only 1 request at a time)
- Minimal dependency footprint
- Easy to test and integrate
- Supports signals, DTCs, GPS, and network stats ingestion

---

## 📦 Installation

```bash
pip install analytics-ingest
```

---

## 🚀 Usage

### Basic Example

```python
from analytics_ingest import IcsAnalytics

client = IcsAnalytics(
    device_id=123,
    vehicle_id=456,
    fleet_id=789,
    org_id=1011,
    graphql_endpoint="https://your-backend/graphql",
    batch_size=100,
    batch_interval_seconds=10,
    max_signal_count=100
)

# Add signals (list of dicts)
client.add_signal([
    {'name': 'VehicleIdentificationNumber', 'unit': '', 'messageName': 'BusQuery_IDDecoding_F190_VSSAL', 'networkName': 'Cluster_6_TestTool', 'ecuName': '', 'arbId': '', 'fileId': '1234', 'paramType': 'TEXT', 'signalType': 'DID', 'messageDate': '2025-07-15T01:40:00.000000', 'paramId': 'F190', 'data': [{'value': 0.04, 'time': '1970-01-07T18:28:54Z'}]},
    # ... more signals ...
])

# Add DTCs (list of dicts)
client.add_dtc([{'messageName': 'DTC Message99B049', 'name': 'DTC Message99B049', 'networkName': 'Cluster_6_TestTool', 'ecuName': 'VCU_Android_GAS', 'ecuId': '14DA80F1', 'messageDate': '2025-07-15T01:42:20.385429', 'fileId': '1234', 'data': [{'dtcId': 'B19B0-49', 'description': 'Head-Up Display - Internal Electronic Failure', 'status': '2F', 'time': '2025-07-15T01:42:15.979524'}]} 
# ... more DTCs ...
])

# Add GPS data (dict)
client.add_gps([
    {"time": "2025-07-28T12:34:56.789Z", "latitude": 37.7749, "longitude": -122.4194, "accuracy": 10.5, "altitude": 120.3, "speed": 45.2, "bearing": 75.0, "available": {"accuracy": True, "altitude": True, "bearing": False, "speed": True, "time": True}},
    {"time": "2025-07-28T12:35:56.789Z", "latitude": 37.7750, "longitude": -122.4195}
    # ... more GPS ...
])


# Add network stats (dict)
client.add_network_stats({
    "name": "CAN1",
    "vehicleId": 456,
    "uploadId": 1,
    "totalMessages": 1000,
    "matchedMessages": 950,
    "unmatchedMessages": 50,
    "errorMessages": 0,
    "longMessageParts": 0,
    "rate": 500.0
})

# Graceful shutdown (flushes any remaining data)
client.close()
```

---

## ⚙️ Configuration

You can configure the client via constructor arguments or environment variables (e.g., `GRAPH_ENDPOINT`).

- `device_id`, `vehicle_id`, `fleet_id`, `org_id`: Required identifiers
- `graphql_endpoint`: URL to your GraphQL backend
- `batch_size`: Number of items per batch (default: 100)
- `batch_interval_seconds`: Max seconds between batch sends (default: 10)
- `max_signal_count`: Max signals per batch (default: 100)

---

## 🛠️ Error Handling & Logging

- Uses exceptions for invalid input or backend errors
- Replaceable `print` statements with logging recommended for production
- Retries failed batch sends on next interval

---

## 🧪 Testing

Run all test cases:

```
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Build and upload package:

```
python3 -m build
python -m twine upload dist/*
```

---

## 💡 Improvements & Roadmap

- Add more usage examples and API documentation
- Integrate a logging framework
- Increase test coverage and add integration tests
- Allow dynamic runtime configuration
- Expose a fully async API
- Add metrics and monitoring hooks
- Enforce linting and type checking in CI

---

## 🤝 Contributing

Pull requests and issues are welcome! Please add tests for new features and follow PEP8 style guidelines.

Setup (Only Once)
After cloning the repo, run:

```
pip install pre-commit
pre-commit install

```

---

## 📄 License

MIT License
Readme.txt
4 KB