# TSFM Python Client

A simple Python client for the TSFM (Time Series Foundation Model) Inference Platform.

## Installation

```bash
git clone git@github.com:S-FM/tsfm-python-client.git
cd tsfm-python-client
poetry install
```

## Quick Start

### 1. Set up your API key

```bash
export TSFM_API_KEY="your_api_key_here"
```

### 2. Make predictions

```python
from tsfm_client import predict

# Simple prediction
data = [10, 12, 13, 15, 17, 16, 18, 20, 22, 25]
response = predict(data=data, forecast_horizon=5)
print(f"Forecast: {response.forecast}")
```

## Supported Models

- **chronos-t5-small**: Fast CPU inference for time series forecasting

## API Reference

### predict() function

```python
predict(
    data: Union[List[float], pd.Series, TimeSeriesData],
    model: str = "chronos-t5-small",
    forecast_horizon: int = 12,
    confidence_intervals: bool = False,
    base_url: str = "http://localhost:8000"
) -> PredictionResponse
```

### TSFMClient class

```python
from tsfm_client import TSFMClient

client = TSFMClient()  # Uses TSFM_API_KEY environment variable

# Make predictions
response = client.predict(data=[1, 2, 3, 4, 5], forecast_horizon=3)

# List models
models = client.list_models()

# Get model info
info = client.get_model_info("chronos-t5-small")

# Health check
health = client.health_check()

client.close()
```

## Examples

### With Pandas

```python
import pandas as pd
from tsfm_client import predict

# Create time series data
dates = pd.date_range('2024-01-01', periods=30, freq='D')
ts_data = pd.Series([100, 102, 98, 105, 107, ...], index=dates)

# Make prediction
response = predict(
    data=ts_data,
    forecast_horizon=7,
    confidence_intervals=True
)
```

### Using Context Manager

```python
from tsfm_client import TSFMClient

with TSFMClient() as client:
    response = client.predict(data=[1, 2, 3, 4, 5])
    print(f"Forecast: {response.forecast}")
```

### Error Handling

```python
from tsfm_client import TSFMClient, AuthenticationError, APIError

try:
    client = TSFMClient()
    response = client.predict(data=[1, 2, 3])
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
```

## Response Format

```python
class PredictionResponse:
    model_name: str
    forecast: List[float]
    confidence_intervals: Optional[Dict]
    metadata: Dict[str, Any]
```

## Requirements

- Python >= 3.11
- Valid TSFM API key
- Running TSFM server
