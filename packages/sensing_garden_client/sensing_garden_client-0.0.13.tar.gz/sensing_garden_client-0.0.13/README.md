# Sensing Garden Client

A Python client for interacting with the Sensing Garden API.

## Installation

Install from PyPI:

```bash
pip install sensing_garden_client
```

Or install from source:

```bash
git clone https://github.com/daydemir/sensing-garden-client.git
pip install sensing-garden-client/sensing_garden_client
```

## Usage

### Installation

Install from PyPI:

```bash
pip install sensing_garden_client
```

Or for development:

```bash
poetry add sensing_garden_client
```

### Basic Usage

#### Count Endpoints Example

You can efficiently count the number of models, detections, classifications, or videos matching filter parameters without retrieving all data:

```python
# Count models
model_count = sgc.models.count()

# Count detections for a device
count = sgc.detections.count(device_id="device-123")

# Count classifications for a model
class_count = sgc.classifications.count(model_id="model-456")

# Count videos for a device in a time range
video_count = sgc.videos.count(device_id="device-123", start_time="2023-06-01T00:00:00Z", end_time="2023-06-02T00:00:00Z")
```


The modern API provides a more intuitive, object-oriented interface:

```python
import sensing_garden_client

# Initialize the client with the new interface
sgc = sensing_garden_client.SensingGardenClient(
    base_url="https://api.example.com", 
    api_key="your-api-key"  # Only needed for POST operations
)

# Working with models
models = sgc.models.fetch(limit=10)
model = sgc.models.create(
    model_id="model-123",
    name="My Bug Model",
    version="1.0.0"
)

# Working with detections
with open("bug_image.jpg", "rb") as f:
    image_data = f.read()
    
detection = sgc.detections.add(
    device_id="device-123",
    model_id="model-456",
    image_data=image_data,
    bounding_box=[0.1, 0.2, 0.3, 0.4],
    timestamp="2023-06-01T12:34:56Z"
)
detections = sgc.detections.fetch(device_id="device-123")

# Working with classifications
classification = sgc.classifications.add(
    device_id="device-123",
    model_id="model-456",
    image_data=image_data,
    family="Rosaceae",
    genus="Rosa",
    species="Rosa gallica",
    family_confidence=0.95,
    genus_confidence=0.92,
    species_confidence=0.89,
    timestamp="2023-06-01T12:34:56Z",
    bounding_box=[0.1, 0.2, 0.3, 0.4],  # Optional bounding box
    track_id="track-abc123",            # Optional tracking ID
    metadata={"source": "drone", "weather": "sunny"}  # Optional metadata dict
)

# bounding_box, track_id, and metadata are now supported for both detections and classifications.
# The backend stores bounding_box values as Decimal for DynamoDB compatibility.
# All tests have been updated and pass for these features (see CHANGELOG).


    family="Rosaceae",
    genus="Rosa",
    species="Rosa gallica",
    family_confidence=0.95,
    genus_confidence=0.92,
    species_confidence=0.89,
    timestamp="2023-06-01T12:34:56Z"
)
classifications = sgc.classifications.fetch(model_id="model-456")

# Working with videos
with open("plant_video.mp4", "rb") as f:
    video_data = f.read()

video = sgc.videos.upload_video(
    device_id="device-123",
    timestamp="2023-06-01T12:34:56Z",
    video_path_or_data=video_data,
    content_type="video/mp4",
    metadata={"location": "greenhouse-A", "duration_seconds": 120}
)

videos = sgc.videos.fetch(
    device_id="device-123",
    start_time="2023-06-01T00:00:00Z",
    end_time="2023-06-02T00:00:00Z"
)

# Working with environmental data
# Submit environmental sensor readings
environment_reading = sgc.environment.add(
    device_id="device-123",
    location={
        "lat": 40.7128,      # Latitude
        "long": -74.0060,    # Longitude
        "alt": 10.5          # Altitude in meters (optional)
    },
    data={
        "pm1p0": 12.5,              # PM1.0 particulate matter (μg/m³)
        "pm2p5": 25.3,              # PM2.5 particulate matter (μg/m³)
        "pm4p0": 35.8,              # PM4.0 particulate matter (μg/m³)
        "pm10p0": 45.2,             # PM10.0 particulate matter (μg/m³)
        "ambient_humidity": 65.5,    # Relative humidity (%)
        "ambient_temperature": 22.3, # Temperature (°C)
        "voc_index": 150,           # Volatile Organic Compounds index
        "nox_index": 75             # Nitrogen Oxides index
    },
    timestamp="2023-06-01T12:34:56Z"  # Required ISO-8601 formatted timestamp
)

# Fetch environmental data with filters
environment_data = sgc.environment.fetch(
    device_id="device-123",
    start_time="2023-06-01T00:00:00Z",
    end_time="2023-06-02T00:00:00Z",
    limit=100,
    sort_by="timestamp",
    sort_desc=True  # Get newest readings first
)
```

**Note:** The video upload API no longer requires or accepts a `description` field. Only `device_id`, `timestamp`, `video_key`, and optional `metadata` are supported.

### Troubleshooting
If you see errors like `ModuleNotFoundError: No module named 'botocore.vendored.six.moves'`, ensure you are running inside your Poetry-managed environment and update boto3/botocore using:

```sh
poetry update boto3 botocore
```

### Environment Variables

The client can also be configured using environment variables:

```python
import os
import sensing_garden_client

# Set environment variables
os.environ["API_BASE_URL"] = "https://api.example.com"
os.environ["SENSING_GARDEN_API_KEY"] = "your-api-key"

# Initialize the client using environment variables
sgc = sensing_garden_client.SensingGardenClient(
    base_url=os.environ.get("API_BASE_URL"),
    api_key=os.environ.get("SENSING_GARDEN_API_KEY")
)
```

## Features

- Efficient `.count()` methods for all major resources (models, detections, classifications, videos)
- All test helpers use `assert` for pytest compatibility
- Poetry-based test and dependency management


- Modern, intuitive API with domain-specific clients
- GET operations for models, detections, classifications, and videos
- POST operations for submitting detections, classifications, and videos
- Model management operations
- Video upload and retrieval with filtering capabilities
- Backward compatibility with previous API versions

## Dependencies

- `requests`: For API communication
