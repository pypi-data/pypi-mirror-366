"""
Data models for TSFM Client
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np


class TimeSeriesData(BaseModel):
    """Time series data structure"""
    values: List[float] = Field(..., description="Time series values")
    timestamps: Optional[List[str]] = Field(None, description="Optional timestamps")
    frequency: Optional[str] = Field(None, description="Frequency of the time series (e.g., '1H', '1D')")
    
    @classmethod
    def from_pandas(cls, series: pd.Series, frequency: Optional[str] = None) -> "TimeSeriesData":
        """Create TimeSeriesData from pandas Series"""
        values = series.values.tolist()
        timestamps = None
        
        if hasattr(series.index, 'strftime'):
            timestamps = series.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        elif not pd.api.types.is_numeric_dtype(series.index):
            timestamps = series.index.astype(str).tolist()
        
        return cls(
            values=values,
            timestamps=timestamps,
            frequency=frequency
        )
    
    @classmethod
    def from_list(cls, values: List[float], timestamps: Optional[List[str]] = None, frequency: Optional[str] = None) -> "TimeSeriesData":
        """Create TimeSeriesData from list of values"""
        return cls(
            values=values,
            timestamps=timestamps,
            frequency=frequency
        )
    
    def to_pandas(self) -> pd.Series:
        """Convert to pandas Series"""
        if self.timestamps:
            index = pd.to_datetime(self.timestamps)
        else:
            index = range(len(self.values))
        
        return pd.Series(self.values, index=index)
    
    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array(self.values)


class PredictionRequest(BaseModel):
    """Prediction request structure"""
    data: TimeSeriesData = Field(..., description="Input time series data")
    forecast_horizon: int = Field(12, description="Number of steps to forecast", ge=1, le=96)
    confidence_intervals: bool = Field(False, description="Whether to include confidence intervals")
    quantiles: Optional[List[float]] = Field(None, description="Quantiles to compute")
    
    def model_validate(self):
        """Validate the prediction request"""
        if self.quantiles:
            for q in self.quantiles:
                if not 0 <= q <= 1:
                    raise ValueError("Quantiles must be between 0 and 1")
        
        if len(self.data.values) == 0:
            raise ValueError("Input data cannot be empty")


class PredictionResponse(BaseModel):
    """Prediction response structure"""
    model_name: str = Field(..., description="Name of the model used")
    forecast: List[float] = Field(..., description="Forecasted values")
    confidence_intervals: Optional[Dict[str, Dict[str, List[float]]]] = Field(None, description="Confidence intervals")
    quantiles: Optional[Dict[str, List[float]]] = Field(None, description="Quantile forecasts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_pandas(self) -> pd.DataFrame:
        """Convert forecast to pandas DataFrame"""
        df = pd.DataFrame({
            'forecast': self.forecast
        })
        
        if self.confidence_intervals:
            for level, bounds in self.confidence_intervals.items():
                df[f'lower_{level}'] = bounds['lower']
                df[f'upper_{level}'] = bounds['upper']
        
        if self.quantiles:
            for quantile, values in self.quantiles.items():
                df[quantile] = values
        
        return df
    
    def get_forecast_array(self) -> np.ndarray:
        """Get forecast as numpy array"""
        return np.array(self.forecast)


class UserInfo(BaseModel):
    """User information structure"""
    user_id: str
    name: str
    scopes: List[str]
    daily_limit: int
    minute_limit: int
    model_access: List[str]


class ModelInfo(BaseModel):
    """Model information structure"""
    name: str
    is_loaded: bool
    has_compiled_model: bool


# Exception classes
class TSFMException(Exception):
    """Base exception for TSFM client"""
    pass


class AuthenticationError(TSFMException):
    """Authentication failed"""
    pass


class RateLimitError(TSFMException):
    """Rate limit exceeded"""
    pass


class ModelNotFoundError(TSFMException):
    """Model not found"""
    pass


class APIError(TSFMException):
    """General API error"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code