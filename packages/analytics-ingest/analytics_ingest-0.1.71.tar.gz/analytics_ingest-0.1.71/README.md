# 🚗 Analytics Ingest Client

A lightweight Python library to batch and send automotive telemetry — like signals, DTCs, GPS, and network stats — to a GraphQL backend.

---

## 🔧 Features

* Python 3.11+ support
* Clean, single-class interface: `IcsAnalytics`
* In-memory caching for resolved IDs
* Smart batching (by time, count, or signal limit)
* Async-safe request queuing (1 request at a time)
* Minimal dependencies
* Easy to integrate and test
* Supports Signals, DTCs, GPS, and Network Stats ingestion

---

## 📦 Installation

```bash
pip install analytics-ingest
```

---

## 🚀 Quick Usage

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

# Add a signal
client.add_signal({'name': 'VehicleIdentificationNumber', 'unit': '', 'messageName': 'BusQuery_IDDecoding_F190_VSSAL', 'networkName': 'Cluster_6_TestTool', 'ecuName': '', 'arbId': '', 'fileId': '1234', 'paramType': 'TEXT', 'signalType': 'DID', 'messageDate': '2025-07-15T01:40:00.000000', 'paramId': 'F190', 'data': [{'value': 0.04, 'time': '1970-01-07T18:28:54Z'}]})

# Add DTCs
client.add_dtc({'messageName': 'DTC Message99B049', 'name': 'DTC Message99B049', 'networkName': 'Cluster_6_TestTool', 'ecuName': 'VCU_Android_GAS', 'ecuId': '14DA80F1', 'messageDate': '2025-07-15T01:42:20.385429', 'fileId': '1234', 'data': [{'dtcId': 'B19B0-49', 'description': 'Head-Up Display - Internal Electronic Failure', 'status': '2F', 'time': '2025-07-15T01:42:15.979524'})

# Add GPS
client.add_gps({"time": "2025-07-28T12:34:56.789Z", "latitude": 37.7749, "longitude": -122.4194, "accuracy": 10.5, "altitude": 120.3, "speed": 45.2, "bearing": 75.0, "available": {"accuracy": True, "altitude": True, "bearing": False, "speed": True, "time": True}})

# Add Network Stats
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

# Flush remaining data before exit
client.close()
client.flush()
```

---

## ⚙️ Config Options

Set through constructor or environment variables.

| Param                    | Description               | Default |
| ------------------------ | ------------------------- | ------- |
| `device_id`              | Device ID (required)      | –       |
| `vehicle_id`             | Vehicle ID (required)     | –       |
| `fleet_id`               | Fleet ID (required)       | –       |
| `org_id`                 | Org ID (required)         | –       |
| `graphql_endpoint`       | GraphQL endpoint          | –       |
| `batch_size`             | Max items per batch       | 100     |
| `batch_interval_seconds` | Time-based flush interval | 10      |
| `max_signal_count`       | Max signals before flush  | 100     |

---

## 🛠️ Error Handling & Logging

* Raises exceptions for bad input or backend failures
* Use logging instead of print in production
* Automatically retries failed batches on next interval

---

## 🧪 Testing

Run all tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Build and publish:

```bash
rm -rf dist/
python3 -m build
python -m twine upload dist/*
```

---

## 💡 Improvements & Roadmap

* Full async API support
* Runtime config updates
* More usage examples
* Metrics & monitoring hooks
* Linting/type-checking in CI

---

## 🤝 Contributing

We welcome PRs and issues! Please follow PEP8 and include tests with any changes.

### One-Time Setup

```bash
pip install pre-commit
pre-commit install
```

---

## 🏁 Dev Quick Start

```bash
git clone http://lustra.intrepidcs.corp/ics/wivi/ipa-py-library.git
cd analytics-ingest

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Test ingestion logic:

```bash
PYTHONPATH=src python3 test_auto_flush_by_signal_count.py
```

---

## 📄 License

MIT License
Readme.txt
4 KB
