# Upstream Python SDK

A Python SDK for seamless integration with the Upstream environmental sensor data platform and CKAN data portal.

> **Note**: This SDK is built on top of the [`upstream-python-api-client`](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client) - an OpenAPI-generated Python client. You can extend the SDK by using the underlying API client directly for advanced use cases or accessing endpoints not yet covered by the high-level SDK interface.

## Overview

The Upstream Python SDK provides a standardized, production-ready toolkit for environmental researchers and organizations to:

- **Authenticate** with Upstream API and CKAN data portals
- **Manage** environmental monitoring campaigns and stations
- **Upload** sensor data efficiently (with automatic chunking for large datasets)
- **Publish** datasets automatically to CKAN for discoverability
- **Automate** data pipelines for continuous sensor networks

## Key Features

### 🔐 **Unified Authentication**

- Seamless integration with Upstream API and Tapis/CKAN
- Automatic token management and refresh
- Secure credential handling

### 📊 **Complete Data Workflow**

```python
from upstream.client import UpstreamClient
from upstream_api_client.models import CampaignsIn, StationCreate
from datetime import datetime, timedelta

# Initialize client with CKAN integration
client = UpstreamClient(
    username="researcher",
    password="password",
    base_url="https://upstream-dso.tacc.utexas.edu",
    ckan_url="https://ckan.tacc.utexas.edu",
    ckan_organization="your-org"
)

# Create campaign
campaign_data = CampaignsIn(
    name="Environmental Monitoring 2024",
    description="Environmental monitoring campaign with multi-sensor stations",
    contact_name="Dr. Jane Smith",
    contact_email="jane.smith@university.edu",
    allocation="TACC",
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=365)
)
campaign = client.create_campaign(campaign_data)

# Create monitoring station
station_data = StationCreate(
    name="Downtown Air Quality Monitor",
    description="Multi-sensor environmental monitoring station",
    contact_name="Dr. Jane Smith",
    contact_email="jane.smith@university.edu",
    start_date=datetime.now()
)
station = client.create_station(campaign.id, station_data)

# Upload sensor data
result = client.upload_csv_data(
    campaign_id=campaign.id,
    station_id=station.id,
    sensors_file="sensors.csv",
    measurements_file="measurements.csv"
)

print(f"Uploaded {result['response']['Total sensors processed']} sensors")
print(f"Added {result['response']['Total measurements added to database']} measurements")

# Publish to CKAN with rich metadata
publication = client.publish_to_ckan(
    campaign_id=campaign.id,
    station_id=station.id
)
print(f"Data published at: {publication['ckan_url']}")
```

### 🚀 **Production-Ready Features**

- **Type-safe interfaces** with Pydantic models and comprehensive validation
- **Rich statistics** - automatic calculation of sensor measurement statistics
- **Comprehensive error handling** with specific exception types (`APIError`, `ValidationError`)
- **CKAN integration** with custom metadata support and automatic resource management
- **Modular architecture** with dedicated managers for campaigns, stations, and sensors
- **Extensive logging** and debugging capabilities
- **Authentication management** with automatic token handling

### 🔄 **CKAN Integration & Publishing**

Seamless data publishing to CKAN portals:

```python
# Publish with custom metadata
publication_result = client.publish_to_ckan(
    campaign_id=campaign_id,
    station_id=station_id,

    # Custom dataset metadata
    dataset_metadata={
        "project_name": "Air Quality Study",
        "funding_agency": "EPA",
        "grant_number": "EPA-2024-001"
    },

    # Custom resource metadata
    resource_metadata={
        "calibration_date": "2024-01-15",
        "quality_control": "Automated + Manual Review",
        "uncertainty_bounds": "±2% of reading"
    },

    # Custom tags for discoverability
    custom_tags=["air-quality", "epa-funded", "quality-controlled"]
)

print(f"Dataset published: {publication_result['ckan_url']}")
```

## Installation

```bash
pip install upstream-sdk
```

For development:

```bash
pip install upstream-sdk[dev]
```

## Demo Notebooks

The SDK includes comprehensive demo notebooks that showcase all features:

### 📓 **UpstreamSDK_Core_Demo.ipynb**

Interactive demonstration of core functionality:

- Authentication and client setup
- Campaign creation and management
- Station setup with sensor configuration
- CSV data upload with comprehensive validation
- Sensor statistics and analytics
- Error handling and best practices

### 📓 **UpstreamSDK_CKAN_Demo.ipynb**

Complete CKAN integration workflow:

- CKAN portal setup and authentication
- Data export and preparation for publishing
- Dataset creation with rich metadata
- Custom metadata support (dataset, resource, and tags)
- Resource management and updates
- Dataset discovery and search capabilities

Both notebooks include detailed explanations, practical examples, and production-ready code patterns.

## Quick Start

### 1. Basic Setup

```python
from upstream.client import UpstreamClient

# Initialize with credentials and CKAN integration
client = UpstreamClient(
    username="your_username",
    password="your_password",
    base_url="https://upstream-dso.tacc.utexas.edu",
    ckan_url="https://ckan.tacc.utexas.edu",
    ckan_organization="your-org"
)

# Test authentication
if client.authenticate():
    print("✅ Connected successfully!")
```

### 2. Create Campaign

```python
from upstream.campaigns import CampaignManager
from upstream_api_client.models import CampaignsIn
from datetime import datetime, timedelta

# Initialize campaign manager
campaign_manager = CampaignManager(client.auth_manager)

campaign_data = CampaignsIn(
    name="Environmental Monitoring 2024",
    description="Multi-sensor environmental monitoring network",
    contact_name="Dr. Jane Smith",
    contact_email="jane.smith@university.edu",
    allocation="TACC",
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=365)
)
campaign = campaign_manager.create(campaign_data)
print(f"Campaign created with ID: {campaign.id}")
```

### 3. Register Monitoring Station

```python
from upstream.stations import StationManager
from upstream_api_client.models import StationCreate
from datetime import datetime

# Initialize station manager
station_manager = StationManager(client.auth_manager)

station_data = StationCreate(
    name="Downtown Air Quality Monitor",
    description="Multi-sensor air quality monitoring station",
    contact_name="Dr. Jane Smith",
    contact_email="jane.smith@university.edu",
    start_date=datetime.now()
)
station = station_manager.create(
    campaign_id=campaign.id,
    station_create=station_data
)
print(f"Station created with ID: {station.id}")
```

### 4. Upload Sensor Data

```python
# Upload from CSV files
result = client.upload_csv_data(
    campaign_id=campaign.id,
    station_id=station.id,
    sensors_file="path/to/sensors.csv",
    measurements_file="path/to/measurements.csv"
)

# Access detailed results
response = result['response']
print(f"Sensors processed: {response['Total sensors processed']}")
print(f"Measurements added: {response['Total measurements added to database']}")
print(f"Processing time: {response['Data Processing time']}")
```

## Data Format Requirements

### Sensors CSV Format

```csv
alias,variablename,units,postprocess,postprocessscript
temp_01,Air Temperature,°C,false,
humidity_01,Relative Humidity,%,false,
PM25_01,PM2.5 Concentration,μg/m³,true,pm25_calibration
wind_speed,Wind Speed,m/s,false,
co2_01,CO2 Concentration,ppm,false,
```

### Measurements CSV Format

```csv
collectiontime,Lat_deg,Lon_deg,temp_01,humidity_01,PM25_01,wind_speed,co2_01
2024-01-15T10:00:00,30.2672,-97.7431,22.5,68.2,15.2,3.2,420
2024-01-15T10:05:00,30.2672,-97.7431,22.7,67.8,14.8,3.5,425
2024-01-15T10:10:00,30.2672,-97.7431,22.9,67.5,16.1,3.1,418
```

## Advanced Usage

### Sensor Analytics and Statistics

```python
# Get sensor statistics after upload
sensors = client.sensors.list(campaign_id=campaign_id, station_id=station_id)

for sensor in sensors.items:
    stats = sensor.statistics
    print(f"Sensor: {sensor.alias} ({sensor.variablename})")
    print(f"  Measurements: {stats.count}")
    print(f"  Range: {stats.min_value:.2f} - {stats.max_value:.2f} {sensor.units}")
    print(f"  Average: {stats.avg_value:.2f} {sensor.units}")
    print(f"  Std Dev: {stats.stddev_value:.3f}")
    print(f"  Last value: {stats.last_measurement_value:.2f}")
    print(f"  Updated: {stats.stats_last_updated}")
```

#### Force Update Sensor Statistics

The SDK provides methods to manually trigger statistics recalculation for sensors when needed (e.g., after data corrections or updates):

```python
from upstream.sensors import SensorManager

# Initialize sensor manager
sensor_manager = SensorManager(client.auth_manager)

# Force update statistics for all sensors in a station
update_result = sensor_manager.force_update_statistics(
    campaign_id=campaign_id,
    station_id=station_id
)
print(f"Statistics update completed for all sensors in station {station_id}")

# Force update statistics for a specific sensor
single_update_result = sensor_manager.force_update_single_sensor_statistics(
    campaign_id=campaign_id,
    station_id=station_id,
    sensor_id=sensor_id
)
print(f"Statistics update completed for sensor {sensor_id}")

# Verify updated statistics
updated_sensors = client.sensors.list(campaign_id=campaign_id, station_id=station_id)
for sensor in updated_sensors.items:
    stats = sensor.statistics
    print(f"Updated stats for {sensor.alias}: {stats.stats_last_updated}")
```

**When to use statistics updates:**
- After correcting measurement data
- When statistics appear outdated or inconsistent
- During data quality assurance processes
- After bulk data imports or migrations

### Measurement Data Management

```python
from upstream.measurements import MeasurementManager
from upstream_api_client.models import MeasurementIn
from datetime import datetime

# Initialize measurement manager
measurement_manager = MeasurementManager(client.auth_manager)

# List measurements for a specific sensor
measurements = measurement_manager.list(
    campaign_id=campaign_id,
    station_id=station_id,
    sensor_id=sensor_id,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    limit=100
)

print(f"Found {len(measurements.items)} measurements")

# Get measurements with confidence intervals for visualization
aggregated_data = measurement_manager.get_with_confidence_intervals(
    campaign_id=campaign_id,
    station_id=station_id,
    sensor_id=sensor_id,
    interval="hour",
    interval_value=1,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 2)
)

for measurement in aggregated_data:
    print(f"Time: {measurement.time_bucket}")
    print(f"  Average: {measurement.avg_value}")
    print(f"  Min/Max: {measurement.min_value} - {measurement.max_value}")
    print(f"  Confidence Interval: {measurement.confidence_interval_lower} - {measurement.confidence_interval_upper}")
```

### Error Handling and Validation

```python
from upstream.exceptions import APIError, ValidationError
from upstream.campaigns import CampaignManager
from upstream.stations import StationManager

try:
    # Initialize managers
    campaign_manager = CampaignManager(client.auth_manager)
    station_manager = StationManager(client.auth_manager)

    # Create campaign with validation
    campaign = campaign_manager.create(campaign_data)
    station = station_manager.create(
        campaign_id=str(campaign.id),
        station_create=station_data
    )

except ValidationError as e:
    print(f"Data validation failed: {e}")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Comprehensive Data Upload

```python
# Upload with detailed response handling
result = client.upload_csv_data(
    campaign_id=campaign.id,
    station_id=station.id,
    sensors_file="path/to/sensors.csv",
    measurements_file="path/to/measurements.csv"
)

# Access detailed upload information
response = result['response']
print(f"Sensors processed: {response['Total sensors processed']}")
print(f"Measurements added: {response['Total measurements added to database']}")
print(f"Processing time: {response['Data Processing time']}")
print(f"Files stored: {response['uploaded_file_sensors stored in memory']}")
```

### Automated Data Pipeline

```python
# Complete automated workflow
def automated_monitoring_pipeline():
    try:
        # List existing campaigns and stations
        campaigns = client.list_campaigns(limit=5)
        if campaigns.items:
            campaign = campaigns.items[0]
            stations = client.list_stations(campaign_id=str(campaign.id))

            if stations.items:
                station = stations.items[0]

                # Upload new sensor data
                result = client.upload_csv_data(
                    campaign_id=campaign.id,
                    station_id=station.id,
                    sensors_file="latest_sensors.csv",
                    measurements_file="latest_measurements.csv"
                )

                # Publish to CKAN automatically
                publication = client.publish_to_ckan(
                    campaign_id=campaign.id,
                    station_id=station.id,
                    custom_tags=["automated", "real-time"]
                )

                print(f"Pipeline completed: {publication['ckan_url']}")

    except Exception as e:
        print(f"Pipeline error: {e}")
        # Implement alerting/retry logic
```

### Extending the SDK with the Underlying API Client

The Upstream SDK provides high-level convenience methods, but you can access the full OpenAPI-generated client for advanced use cases.

**📖 Complete API Documentation:** [Documentation for API Endpoints](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/tree/main?tab=readme-ov-file#documentation-for-api-endpoints)

The SDK uses Pydantic models from the [`upstream-python-api-client`](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client) for type-safe data handling and validation.

**📖 Complete Model Documentation:** [Documentation for Models](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/tree/main?tab=readme-ov-file#documentation-for-models)

```python
from upstream.client import UpstreamClient
from upstream_api_client.api.campaigns_api import CampaignsApi
from upstream_api_client.api.measurements_api import MeasurementsApi

# Initialize the SDK client
client = UpstreamClient(username="user", password="pass", base_url="https://upstream-dso.tacc.utexas.edu")
client.authenticate()

# Access the underlying API client for advanced operations
api_client = client.auth_manager.api_client

# Use the generated API classes directly
campaigns_api = CampaignsApi(api_client)
measurements_api = MeasurementsApi(api_client)

# Example: Use advanced filtering not yet available in the SDK
response = measurements_api.get_measurements_api_v1_campaigns_campaign_id_stations_station_id_sensors_sensor_id_measurements_get(
    campaign_id=campaign_id,
    station_id=station_id,
    sensor_id=sensor_id,
    min_measurement_value=20.0,
    max_measurement_value=30.0,
    start_date="2024-01-01T00:00:00",
    end_date="2024-12-31T23:59:59",
    limit=1000,
    page=1
)

print(f"Advanced filtered measurements: {len(response.items)}")
```

This approach allows you to:
- Access all available API endpoints
- Use advanced filtering and pagination options
- Handle complex data transformations
- Implement custom error handling
- Access response metadata and headers

## Use Cases

### 🌪️ **Disaster Response Networks**

- Hurricane monitoring stations with automated data upload
- Emergency response sensor deployment
- Real-time environmental hazard tracking

### 🌬️ **Environmental Research**

- Long-term air quality monitoring
- Climate change research networks
- Urban environmental health studies

### 🌊 **Water Monitoring**

- Stream gauge networks
- Water quality assessment programs
- Flood monitoring and prediction

### 🏭 **Industrial Monitoring**

- Emissions monitoring compliance
- Environmental impact assessment
- Regulatory reporting automation

## API Reference

### UpstreamClient Methods

#### Campaign Management

- **`create_campaign(campaign_in: CampaignsIn)`** - Create a new monitoring campaign
- **`get_campaign(campaign_id: str)`** - Get campaign by ID
- **`list_campaigns(**kwargs)`\*\* - List all campaigns

#### Station Management

- **`create_station(campaign_id: str, station_create: StationCreate)`** - Create a new monitoring station
- **`get_station(station_id: str, campaign_id: str)`** - Get station by ID
- **`list_stations(campaign_id: str, **kwargs)`\*\* - List stations for a campaign

#### Data Upload

- **`upload_csv_data(campaign_id: str, station_id: str, sensors_file: str, measurements_file: str)`** - Upload CSV files with comprehensive response
- **`publish_to_ckan(campaign_id: str, station_id: str, dataset_metadata: dict = None, resource_metadata: dict = None, custom_tags: list = None, **kwargs)`\*\* - Publish to CKAN with custom metadata

#### Sensor Management

- **`sensors.get(sensor_id: int, station_id: int, campaign_id: int)`** - Get sensor by ID with statistics
- **`sensors.list(campaign_id: int, station_id: int, **kwargs)`** - List sensors for a station with filtering options
- **`sensors.update(sensor_id: int, station_id: int, campaign_id: int, sensor_update: SensorUpdate)`** - Update sensor configuration
- **`sensors.delete(sensor_id: int, station_id: int, campaign_id: int)`** - Delete a sensor
- **`sensors.upload_csv_files(campaign_id: int, station_id: int, sensors_file: str, measurements_file: str, chunk_size: int = 1000)`** - Upload CSV files with chunking support
- **`sensors.force_update_statistics(campaign_id: int, station_id: int)`** - Force recalculation of statistics for all sensors in a station
- **`sensors.force_update_single_sensor_statistics(campaign_id: int, station_id: int, sensor_id: int)`** - Force recalculation of statistics for a specific sensor

#### Measurement Management

- **`measurements.create(campaign_id: int, station_id: int, sensor_id: int, measurement_in: MeasurementIn)`** - Create a new measurement
- **`measurements.list(campaign_id: int, station_id: int, sensor_id: int, **filters)`** - List measurements with filtering options
- **`measurements.get_with_confidence_intervals(campaign_id: int, station_id: int, sensor_id: int, **params)`** - Get aggregated measurements with confidence intervals for visualization
- **`measurements.update(campaign_id: int, station_id: int, sensor_id: int, measurement_id: int, measurement_update: MeasurementUpdate)`** - Update a specific measurement
- **`measurements.delete(campaign_id: int, station_id: int, sensor_id: int)`** - Delete all measurements for a sensor

#### Utilities

- **`authenticate()`** - Test authentication and return status
- **`logout()`** - Logout and invalidate tokens
- **`list_campaigns(limit: int = 10, **kwargs)`\*\* - List campaigns with pagination
- **`list_stations(campaign_id: str, **kwargs)`\*\* - List stations for a campaign
- **`get_campaign(campaign_id: str)`** - Get detailed campaign information
- **`get_station(station_id: str, campaign_id: str)`** - Get detailed station information

### Core Classes

- **`UpstreamClient`** - Main SDK interface with CKAN integration
- **`CampaignManager`** - Campaign lifecycle management
- **`StationManager`** - Station creation and management
- **`MeasurementManager`** - Individual measurement data operations
- **`CKANIntegration`** - CKAN portal integration and publishing

### Data Models

The SDK uses Pydantic models from the [`upstream-python-api-client`](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client) for type-safe data handling and validation.

**📖 Complete Model Documentation:** [Documentation for Models](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/tree/main?tab=readme-ov-file#documentation-for-models)

**Key Models:**
- **`CampaignsIn`** - [Campaign creation model](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/blob/main/docs/CampaignsIn.md)
- **`StationCreate`** - [Station configuration model](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/blob/main/docs/StationCreate.md)
- **`MeasurementIn`** - [Individual measurement model](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/blob/main/docs/MeasurementIn.md)
- **`AggregatedMeasurement`** - [Statistical measurement aggregation model](https://github.com/In-For-Disaster-Analytics/upstream-python-api-client/blob/main/docs/AggregatedMeasurement.md)

**Usage Example:**
```python
from upstream_api_client.models import CampaignsIn, StationCreate, MeasurementIn
from datetime import datetime, timedelta

# See official documentation for complete field specifications
campaign = CampaignsIn(
    name="Environmental Monitoring 2024",
    allocation="TACC-allocation-id",
    # ... see CampaignsIn.md for all fields
)
```

### Exceptions

- **`APIError`** - API-specific errors with detailed messages
- **`ValidationError`** - Data validation and format errors
- **`AuthManager`** - Authentication and token management

## Configuration

### Configuration File

```yaml
# config.yaml
upstream:
  username: your_username
  password: your_password
  base_url: https://upstream-dso.tacc.utexas.edu

ckan:
  url: https://ckan.tacc.utexas.edu
  organization: your-organization
  api_key: your_ckan_api_key # Optional for read-only
  timeout: 30

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/In-For-Disaster-Analytics/upstream-python-sdk.git
cd upstream-python-sdk
pip install -e .[dev]
pre-commit install
```

### Running Tests

```bash
pytest                          # Run all tests
pytest tests/test_auth.py       # Run specific test file
pytest --cov=upstream           # Run with coverage
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://upstream-python-sdk.readthedocs.io](https://upstream-python-sdk.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/In-For-Disaster-Analytics/upstream-python-sdk/issues)

## Citation

If you use this SDK in your research, please cite:

```bibtex
@software{upstream_python_sdk,
  title={Upstream Python SDK: Environmental Sensor Data Integration},
  author={In-For-Disaster-Analytics Team},
  year={2024},
  url={https://github.com/In-For-Disaster-Analytics/upstream-python-sdk},
  version={1.0.0}
}
```

## Related Projects

- **[Upstream Platform](https://github.com/In-For-Disaster-Analytics/upstream-docker)** - Main platform repository
- **[CKAN Integration](https://ckan.tacc.utexas.edu)** - Data portal for published datasets

---

**Built for the environmental research community** 🌍
**Enabling automated, reproducible, and discoverable environmental data workflows**
