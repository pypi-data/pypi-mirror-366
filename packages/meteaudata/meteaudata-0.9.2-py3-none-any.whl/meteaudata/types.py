import copy
import datetime
import inspect
import os
import shutil
import tempfile
import zipfile
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import yaml
from plotly.subplots import make_subplots
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from .displayable import DisplayableBase

# set the default plotly template
pio.templates.default = "plotly_white"

PLOT_COLORS = go.Layout(template="plotly_white").template.layout.colorway


class NamedTempDirectory:
    def __init__(self, name: str):
        self.name: str = name
        self.dir_path: Optional[str] = None

    def __enter__(self):
        self.base_dir = tempfile.gettempdir()
        self.dir_path = os.path.join(self.base_dir, self.name)
        os.makedirs(self.dir_path, exist_ok=True)
        return self.dir_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dir_path is not None:
            shutil.rmtree(self.dir_path)


def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create a relative path for files to keep the directory structure
                relative_path = os.path.relpath(
                    os.path.join(root, file), os.path.join(folder_path, "..")
                )
                zipf.write(os.path.join(root, file), relative_path)


def zip_directory_contents(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        len_dir_path = len(folder_path)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create a relative path for files starting from inside the folder_path
                file_path = os.path.join(root, file)
                relative_path = file_path[len_dir_path:].lstrip(os.sep)
                zipf.write(file_path, relative_path)


def serialize_series(series: pd.Series) -> dict:
    """Serializes a pandas Series to a dictionary.

    Args:
        series: The pandas Series to serialize.

    Returns:
        A dictionary containing the serialized representation of the Series.
    """

    return {
        "name": series.name,
        "index": series.index.to_list(),
        "data": series.to_dict(),
        "dtype": str(series.dtype),
    }


class IndexMetadata(BaseModel, DisplayableBase):
    """Metadata describing the characteristics of a pandas Index.
    
    This class captures essential information about time series indices to enable
    proper reconstruction after serialization. It handles various pandas Index types
    including DatetimeIndex, PeriodIndex, RangeIndex, and CategoricalIndex.
    
    The metadata preserves critical properties like timezone information for datetime
    indices, frequency for time-based indices, and categorical ordering, ensuring
    that reconstructed indices maintain their original behavior and constraints.
    
    """
    type: str = Field(description="Type of pandas Index (e.g., 'DatetimeIndex', 'RangeIndex', 'PeriodIndex')")
    name: Optional[str] = Field(default=None, description="Name assigned to the index, if any")
    frequency: Optional[str] = Field(default=None, description="Frequency string for time-based indices (e.g., 'D', 'H', '15min')")
    time_zone: Optional[str] = Field(default=None, description="Timezone information for datetime indices (e.g., 'UTC', 'America/Toronto')")
    closed: Optional[str] = Field(default=None, description="Which side of intervals are closed for IntervalIndex ('left', 'right', 'both', 'neither')")
    categories: Optional[list[Any]] = Field(default=None, description="List of category values for CategoricalIndex")
    ordered: Optional[bool] = Field(default=None, description="Whether categories have a meaningful order for CategoricalIndex")
    start: Optional[int] = Field(default=None, description="Start value for RangeIndex")
    end: Optional[int] = Field(default=None, description="End value (exclusive) for RangeIndex") 
    step: Optional[int] = Field(default=None, description="Step size for RangeIndex")
    dtype: str = Field(description="Data type of the index values (e.g., 'datetime64[ns]', 'int64')")

    
    @staticmethod
    def extract_index_metadata(index: pd.Index) -> "IndexMetadata":
        metadata = {
            "type": type(index).__name__,
            "name": index.name,
            "dtype": str(index.dtype),
        }

        if hasattr(index, "freqstr"):
            metadata["frequency"] = index.freqstr  # type: ignore

        if isinstance(index, pd.DatetimeIndex):
            metadata["time_zone"] = str(index.tz) if index.tz is not None else None

        if isinstance(index, pd.IntervalIndex):
            metadata["closed"] = index.closed

        if isinstance(index, pd.CategoricalIndex):
            metadata["categories"] = index.categories.tolist()
            metadata["ordered"] = index.ordered  # type: ignore

        if isinstance(index, pd.RangeIndex):
            metadata["start"] = index.start
            metadata["end"] = (
                index.stop
            )  # 'end' is exclusive in RangeIndex, hence using 'stop'
            metadata["step"] = index.step

        return IndexMetadata(**metadata)

    @staticmethod
    def reconstruct_index(index: pd.Index, metadata: "IndexMetadata") -> pd.Index:
        index = index.copy()
        if metadata.type == "DatetimeIndex":
            dt_index = pd.to_datetime(index)
            # is the indez tz-naive or tz-aware?
            if dt_index.tz is None:
                reconstructed_index = (
                    dt_index
                    if metadata.time_zone is None
                    else dt_index.tz_localize(metadata.time_zone)
                )
            else:
                reconstructed_index = (
                    dt_index.tz_convert(metadata.time_zone)
                    if metadata.time_zone is not None
                    else dt_index.tz_localize(None)
                )
            if metadata.frequency:
                dummy_series = pd.Series([0] * len(index), index=index)
                reconstructed_index = dummy_series.asfreq(metadata.frequency).index

        elif metadata.type == "PeriodIndex":
            reconstructed_index = pd.PeriodIndex(index, freq=metadata.frequency)
        elif metadata.type == "IntervalIndex":
            reconstructed_index = pd.IntervalIndex(index, closed=metadata.closed)  # type: ignore
        elif metadata.type == "CategoricalIndex":
            reconstructed_index = pd.CategoricalIndex(
                index, categories=metadata.categories, ordered=metadata.ordered
            )
        elif metadata.type == "RangeIndex":
            if metadata.start is None or metadata.end is None:
                raise ValueError(
                    "Cannot reconstruct RangeIndex without start and end values."
                )
            reconstructed_index = pd.RangeIndex(
                start=metadata.start,
                stop=metadata.end,
                step=metadata.step,  # type: ignore
            )
        elif metadata.type == "Int64Index":
            reconstructed_index = pd.Int64Index(index)  # type: ignore
        elif metadata.type == "Float64Index":
            reconstructed_index = pd.Float64Index(index)  # type: ignore
        else:
            reconstructed_index = pd.Index(index)

        reconstructed_index.name = metadata.name
        return reconstructed_index
    def _get_identifier(self) -> str:
        """Get the key identifier for IndexMetadata."""
        return f"type='{self.type}'"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for IndexMetadata."""
        return {
            'type': self.type,
            'name': self.name,
            'dtype': self.dtype,
            'frequency': self.frequency,
            'time_zone': self.time_zone,
            'closed': self.closed,
            'categories': self.categories,
            'ordered': self.ordered,
            'start': self.start,
            'end': self.end,
            'step': self.step
        }

class ParameterValue(BaseModel, DisplayableBase):
    """Wrapper for complex parameter values in processing functions.
    
    This class provides a structured way to store and display complex parameter
    values like nested dictionaries, lists, or custom objects that are used in
    time series processing functions. It enables recursive display of nested
    structures while maintaining type information.
    
    The wrapper handles numpy arrays by converting them to a serializable format
    and provides formatted display for various data types commonly used in
    environmental data processing workflows.
    
    Attributes:
        value: The actual parameter value of any type
        value_type: String representation of the value's type
    """
    value: Any = Field(description="The actual parameter value of any type")
    value_type: str = Field(description="String representation of the value's Python type")

    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, value: Any, **data):
        super().__init__(value=value, value_type=type(value).__name__, **data)
    
    def _get_identifier(self) -> str:
        return f"type='{self.value_type}'"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Recursively handle nested structures."""
        if isinstance(self.value, dict):
            attrs = {}
            for key, val in self.value.items():
                if self._is_displayable_complex(val):
                    attrs[f"key_{key}"] = ParameterValue(val)
                else:
                    attrs[key] = self._format_simple_parameter_value(val)
            return attrs
        elif isinstance(self.value, (list, tuple)):
            attrs = {
                'length': len(self.value),
                'type': self.value_type
            }
            # Show first few items if they're complex, or a summary if simple
            for i, item in enumerate(self.value[:5]):  # Limit to first 5 items
                if self._is_displayable_complex(item):
                    attrs[f"item_{i}"] = ParameterValue(item)
                else:
                    attrs[f"item_{i}"] = self._format_simple_parameter_value(item)
            
            if len(self.value) > 5:
                attrs['more_items'] = f"... and {len(self.value) - 5} more items"
            
            return attrs
        else:
            # For simple values, just show the value
            return {'value': self._format_simple_parameter_value(self.value)}
    
    def _is_displayable_complex(self, obj: Any) -> bool:
        """Check if an object is complex enough to warrant its own ParameterValue wrapper."""
        if isinstance(obj, dict):
            return len(obj) > 1 or any(
                isinstance(v, (dict, list, tuple)) or (hasattr(v, '__dict__') and not isinstance(v, (str, int, float, bool, datetime))) for v in obj.values()
            )
        elif isinstance(obj, (list, tuple)):
            return len(obj) > 1 or any(isinstance(item, (dict, list, tuple)) for item in obj)
        elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, datetime.datetime)):
            return True
        return False
    
    def _format_simple_parameter_value(self, value: Any) -> str:
        """Format simple parameter values."""
        if isinstance(value, dict) and "__numpy_array__" in value:
            return f"array(shape={value['shape']}, dtype={value['dtype']})"
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (list, tuple)) and len(value) > 3:
            return f"{type(value).__name__}[{len(value)} items]"
        else:
            return str(value)

class Parameters(BaseModel, DisplayableBase):
    """Container for processing function parameters with numpy array support.
    
    This class stores parameters passed to time series processing functions,
    automatically handling complex data types like numpy arrays, nested objects,
    and custom classes. It provides serialization capabilities while preserving
    the ability to reconstruct original parameter values.
    
    The class is particularly useful for maintaining reproducible processing
    pipelines where parameter values need to be stored as metadata alongside
    processed time series data.
    
    """
    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    @model_validator(mode="before")
    @classmethod
    def handle_numpy_arrays(cls, data: Any) -> Any:
        """Prepare data for Pydantic validation."""
        if isinstance(data, dict):
            return {k: cls._prepare_value(v) for k, v in data.items()}
        return data

    @classmethod
    def _prepare_value(cls, value: Any) -> Any:
        """Convert numpy arrays to lists for validation."""
        if isinstance(value, np.ndarray):
            return {
                "__numpy_array__": True,
                "data": value.tolist(),
                "dtype": str(value.dtype),
                "shape": value.shape,
            }
        elif isinstance(value, dict):
            return {k: cls._prepare_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [cls._prepare_value(v) for v in value]
        elif hasattr(value, "__dict__"):
            obj_dict = value.__dict__.copy()
            processed_dict = {k: cls._prepare_value(v) for k, v in obj_dict.items()}
            return processed_dict
        return value

    def as_dict(self) -> dict[str, Any]:
        """Convert to dict, handling special types."""
        data = self.model_dump()
        return self._restore_values(data)

    def _restore_values(self, data: Any) -> Any:
        """Restore special types like numpy arrays from the dict representation."""
        if isinstance(data, dict):
            if data.get("__numpy_array__"):
                # Restore numpy array
                return np.array(data["data"], dtype=data["dtype"])
            return {k: self._restore_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._restore_values(v) for v in data]
        return data

    def _get_identifier(self) -> str:
        """Get the key identifier for Parameters."""
        # Get all non-private attributes from model_extra
        param_attrs = getattr(self, 'model_extra', {})
        param_count = len(param_attrs)
        return f"parameters[{param_count} items]"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for Parameters with nested object support."""
        attrs = {}
        
        # Get parameter count
        param_attrs = getattr(self, 'model_extra', {})
        if param_attrs:
            attrs['parameter_count'] = len(param_attrs)
            
            # Process each parameter
            for field_name, value in param_attrs.items():
                if self._is_displayable_complex(value):
                    # Wrap complex values in ParameterValue for recursive display
                    attrs[f"param_{field_name}"] = ParameterValue(value)
                else:
                    # Show simple values directly
                    attrs[field_name] = self._format_simple_parameter_value(value)
        
        return attrs
    
    def _is_displayable_complex(self, obj: Any) -> bool:
        """Check if a parameter value is complex enough to warrant recursive display."""
        if isinstance(obj, dict):
            # Complex if it has multiple keys or contains nested structures
            if obj.get("__numpy_array__"):
                return False  # Numpy arrays are handled as simple values
            return len(obj) > 1 or any(isinstance(v, (dict, list, tuple)) for v in obj.values())
        elif isinstance(obj, (list, tuple)):
            # Complex if it's long or contains nested structures
            return len(obj) > 3 or any(isinstance(item, (dict, list, tuple)) for item in obj[:3])
        elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, datetime.datetime)):
            return True
        return False
    
    def _format_simple_parameter_value(self, value: Any) -> str:
        """Format simple parameter values for display."""
        if isinstance(value, dict) and "__numpy_array__" in value:
            return f"array(shape={value['shape']}, dtype={value['dtype']})"
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (list, tuple)) and len(value) > 3:
            return f"{type(value).__name__}[{len(value)} items]"
        elif isinstance(value, dict):
            return f"dict[{len(value)} items]"
        else:
            return str(value)

class ProcessingType(Enum):
    """Standardized categories for time series processing operations.
    
    This enumeration defines the standard types of processing operations that can
    be applied to environmental time series data. Each type represents a distinct
    category of data transformation with specific characteristics and purposes
    in environmental monitoring and wastewater treatment analysis.
    
    The processing types enable consistent categorization of operations across
    different processing pipelines and facilitate automated quality control,
    reporting, and method comparison workflows.
    
    """
    
    SORTING = "sorting"  # "Reordering time series data by timestamp or value"
    REMOVE_DUPLICATES = "remove_duplicates"  # "Eliminating duplicate measurements at the same timestamp"
    SMOOTHING = "smoothing"  # "Noise reduction using moving averages, exponential smoothing, or similar techniques"
    FILTERING = "filtering"  # "Signal filtering operations (low-pass, high-pass, band-pass, notch filters)"
    RESAMPLING = "resampling"  # "Changing temporal resolution through upsampling, downsampling, or interpolation"
    GAP_FILLING = "gap_filling"  # "Filling missing data points using interpolation, forecasting, or substitution methods"
    PREDICTION = "prediction"  # "Forecasting future values using statistical or machine learning models"
    TRANSFORMATION = "transformation"  # "Mathematical transformations (log, power, normalization, standardization)"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"  # "Reducing data complexity using PCA, feature selection, or similar techniques"
    FAULT_DETECTION = "fault_detection"  # "Identifying anomalous measurements or sensor malfunctions"
    FAULT_IDENTIFICATION = "fault_identification"  # "Classifying the type or cause of detected faults"
    FAULT_DIAGNOSIS = "fault_diagnosis"  # "Determining root causes and recommending corrective actions for faults"
    OTHER = "other"  # "Custom or specialized processing operations not covered by standard categories"

 

class DataProvenance(BaseModel, DisplayableBase):
    """Information about the source and context of time series data.
    
    This class captures essential metadata about where time series data originated,
    including the source repository, project context, physical location, equipment
    used, and the measured parameter. This information is crucial for data
    traceability and understanding measurement context in environmental monitoring.
    
    Provenance information enables users to assess data quality, understand
    measurement conditions, and make informed decisions about data usage in
    analysis and modeling workflows.
    
    """
    source_repository: Optional[str] = Field(default=None, description="Name or identifier of the data repository or database")
    project: Optional[str] = Field(default=None, description="Project name or identifier under which data was collected")
    location: Optional[str] = Field(default=None, description="Physical location where measurements were taken (e.g., 'Site_A', 'Influent_Tank_1')")
    equipment: Optional[str] = Field(default=None, description="Equipment or instrument used for data collection (e.g., 'pH_probe_001', 'flow_meter')")
    parameter: Optional[str] = Field(default=None, description="Physical/chemical parameter being measured (e.g., 'temperature', 'dissolved_oxygen', 'TSS')")
    purpose: Optional[str] = Field(default=None, description="Purpose or context of the measurement (e.g., 'regulatory_compliance', 'process_optimization')")
    metadata_id: Optional[str] = Field(default=None, description="Unique identifier for linking to external metadata systems")

    
    def _get_identifier(self) -> str:
        """Get the key identifier for DataProvenance."""
        if self.parameter:
            return f"parameter='{self.parameter}'"
        elif self.metadata_id:
            return f"metadata_id='{self.metadata_id}'"
        else:
            return f"location='{self.location}'"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for DataProvenance."""
        return {
            'source_repository': self.source_repository,
            'project': self.project,
            'location': self.location,
            'equipment': self.equipment,
            'parameter': self.parameter,
            'purpose': self.purpose,
            'metadata_id': self.metadata_id
        }


class FunctionInfo(BaseModel, DisplayableBase):
    """Metadata about processing functions applied to time series data.
    
    This class documents the functions used in data processing pipelines,
    capturing essential information for reproducibility including function name,
    version, author, and reference documentation. It can optionally capture
    the actual source code of the function for complete reproducibility.
    
    Function information is critical for understanding how data has been processed
    and for reproducing analysis results. The automatic source code capture
    feature helps maintain processing lineage even when function implementations
    change over time.
    
    """
    name: str = Field(description="Name of the processing function")
    version: str = Field(description="Version identifier of the function (e.g., '1.2.0', 'v2024.1')")
    author: str = Field(description="Author or team responsible for the function implementation")
    reference: str = Field(description="Reference documentation, paper, or URL describing the method")
    source_code: Optional[str] = Field(default=None, description="Complete source code of the function for reproducibility")

    def __init__(self, **data):
        super().__init__(**data)
        if "source_code" not in data:
            self.capture_function_source()

    def capture_function_source(self):
        # Capture the current stack and find the function where the instance was created
        stack = inspect.stack()
        # The 1st element in the stack is this capture_function_source method
        # The 2nd element is the __init__ of this class (if called directly from a function)
        # The 3rd element should therefore be the function from which this instance was created
        try:
            # Get the frame for the caller of __init__
            caller_frame = stack[2]
            # Extract the function object from the frame
            function = caller_frame.frame.f_globals[caller_frame.function]
            # Store the source code of the function
            self.source_code = inspect.getsource(function)
        except IndexError:
            self.source_code = "Could not determine the function source."
        except KeyError:
            self.source_code = "Function not found in globals."
        except Exception as e:
            self.source_code = f"An error occurred: {e}"

    def _get_identifier(self) -> str:
        """Get the key identifier for FunctionInfo."""
        return f"name='{self.name}'"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for FunctionInfo."""
        attrs = {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'reference': self.reference
        }
        
        # Only show source code info if it exists and isn't an error message
        if (self.source_code and 
            not self.source_code.startswith("Could not determine") and
            not self.source_code.startswith("Function not found") and
            not self.source_code.startswith("An error occurred")):
            attrs['has_source_code'] = True
            attrs['source_code_lines'] = len(self.source_code.splitlines())
        else:
            attrs['has_source_code'] = False
        
        return attrs

class ProcessingStep(BaseModel, DisplayableBase):
    """Record of a single data processing operation applied to time series.
    
    This class documents individual steps in a data processing pipeline, capturing
    the type of processing performed, when it was executed, the function used,
    and the parameters applied. Each step maintains a complete audit trail of
    data transformations.
    
    Processing steps are chained together to form a complete processing history,
    enabling full traceability from raw data to final processed results. The
    step_distance field tracks temporal shifts introduced by operations like
    forecasting or lag analysis.
    
    """
    type: ProcessingType = Field(description="Category of processing operation performed")
    description: str = Field(description="Human-readable description of what this processing step accomplished")
    run_datetime: datetime.datetime = Field(description="Timestamp when this processing step was executed")
    requires_calibration: bool = Field(description="Whether this processing step requires calibration data or parameters")
    function_info: FunctionInfo = Field(description="Information about the function used for processing")
    parameters: Optional[Parameters] = Field(default=None, description="Parameters passed to the processing function")
    step_distance: int = Field(default=0, description="Number of time steps shifted (positive for future predictions, negative for lag operations)")
    suffix: str = Field(description="Short identifier appended to time series names (e.g., 'SMOOTH', 'FILT', 'PRED')")
    input_series_names: list[str] = Field(default_factory=list, description="Names of input time series used in this processing step")


    def __str__(self) -> str:
        return f"Processed {self.input_series_names} on {self.run_datetime.strftime('%Y-%m-%d %H:%M:%S')} using function `{self.function_info.name}`. Result has suffix {self.suffix}"

    def _get_identifier(self) -> str:
        """Get the key identifier for ProcessingStep."""
        return f"type='{self.type.value} ({self.suffix})'"
    
    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for ProcessingStep."""
        attrs = {
            'type': self.type.value,
            'description': self.description,
            'suffix': self.suffix,
            'run_datetime': self.run_datetime,
            'requires_calibration': self.requires_calibration,
            'step_distance': self.step_distance,
            'input_series_names': self.input_series_names,
            'function_info': self.function_info,  # This allows drilling into FunctionInfo
        }
        
        # Add parameters if they exist
        if self.parameters:
            attrs['parameters'] = self.parameters
        
        return attrs

class ProcessingConfig(BaseModel):
    steps: list[ProcessingStep]


class TimeSeries(BaseModel, DisplayableBase):
    """Time series data with complete processing history and metadata.
    
    This class represents a single time series with its associated pandas Series
    data, complete processing history, and index metadata. It maintains a full
    audit trail of all transformations applied to the data from its raw state
    to the current processed form.
    
    The class handles serialization of pandas objects and preserves critical
    index information to ensure proper reconstruction. It's the fundamental
    building block for environmental time series analysis workflows.
    
    """
    series: pd.Series = Field(default=pd.Series(dtype=object), description="The pandas Series containing the actual time series data")
    processing_steps: list[ProcessingStep] = Field(default_factory=list, description="Complete history of processing operations applied to this time series")
    index_metadata: Optional[IndexMetadata] = Field(default=None, description="Metadata about the time series index for proper reconstruction")
    values_dtype: str = Field(default="str", description="Data type of the time series values")
    created_on: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp when this TimeSeries object was created")

    model_config: dict = {
        "arbitrary_types_allowed": True,
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        from_serialized = (
            "series" in data and isinstance(data["series"], dict)
        ) or "series" not in data
        self.__post_init_post_parse__(from_serialized)

    def __post_init_post_parse__(self, from_serialized):
        if self.series is not None and not from_serialized:
            self.index_metadata = IndexMetadata.extract_index_metadata(
                self.series.index
            )
            self.values_dtype = str(self.series.dtype)
        elif from_serialized:
            if self.series.empty:
                return
            if self.index_metadata is not None:
                IndexMetadata.reconstruct_index(self.series.index, self.index_metadata)
            if self.values_dtype is not None:
                self.series = self.series.astype(self.values_dtype)  # type: ignore

    @field_validator("series", mode="before")
    def dict_to_series(cls, v):
        if isinstance(v, dict):
            return pd.Series(**v)
        return v

    @field_serializer("series")
    def series_to_dict(series: pd.Series):  # type: ignore
        return serialize_series(series)

    def __eq__(self, other):
        if not isinstance(other, TimeSeries):
            return False
        if not str(self.series.dtype) == str(other.series.dtype):
            return False

        # For numeric data, use np.allclose
        if np.issubdtype(self.series.dtype, np.number):
            if not np.allclose(self.series.values, other.series.values, equal_nan=True):
                return False
        # For non-numeric data (strings, objects, etc.)
        else:
            # Handle NaN/None values separately if needed
            mask_self = pd.isna(self.series)
            mask_other = pd.isna(other.series)

            # Check if NaN patterns match
            if not (mask_self == mask_other).all():
                return False

            # Compare non-NaN values
            if not (self.series[~mask_self] == other.series[~mask_other]).all():
                return False

        if self.index_metadata != other.index_metadata:
            return False
        if self.values_dtype != other.values_dtype:
            return False
        if len(self.processing_steps) != len(other.processing_steps):
            return False
        for i in range(len(self.processing_steps)):
            if self.processing_steps[i] != other.processing_steps[i]:
                return False
        return True

    def metadata_dict(self):
        metadata = {}
        for k, v in self.model_dump().items():
            if k == "processing_steps":
                steps = []
                for step in v:
                    ser_step = step.copy()
                    for k, v in step.items():
                        if k == "type":
                            ser_step[k] = v.value
                    steps.append(ser_step)
                metadata["processing_steps"] = steps
            elif k == "series":
                continue
            else:
                metadata[k] = v
        return metadata

    def load_metadata_from_dict(self, metadata: dict):
        self.processing_steps = [
            ProcessingStep(**step) for step in metadata["processing_steps"]
        ]
        self.index_metadata = IndexMetadata(**metadata["index_metadata"])
        reconstructed_index = IndexMetadata.reconstruct_index(
            self.series.index, self.index_metadata
        )
        self.series.index = reconstructed_index
        self.values_dtype = metadata["values_dtype"]
        self.series = self.series.astype(self.values_dtype)
        return None

    def load_metadata_from_file(self, file_path: str):
        with open(file_path, "r") as f:
            metadata = yaml.safe_load(f)
        self.load_metadata_from_dict(metadata)
        return self

    def load_data_fom_file(self, file_path: str):
        self.series = pd.read_csv(file_path, index_col=0).iloc[:, 0]
        return self

    @staticmethod
    def load(
        data_file_path: Optional[str] = None,
        data: Optional[pd.Series] = None,
        metadata_file_path: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        ts = TimeSeries()
        if data:
            ts.series = data
        elif data_file_path:
            ts.load_data_fom_file(data_file_path)
        if metadata:
            ts.load_metadata_from_dict(metadata)
        elif metadata_file_path:
            ts.load_metadata_from_file(metadata_file_path)
        return ts

    def plot(
        self,
        title: Optional[str] = None,
        y_axis: Optional[str] = None,
        x_axis: Optional[str] = None,
        legend_name: Optional[str] = None,
        start: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
        end: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
    ) -> go.Figure:
        """
        Create an interactive Plotly plot of the time series data.
        
        The plot styling is automatically determined by the processing type of the time series.
        For prediction data, temporal shifting is applied to show future timestamps.
        
        Args:
            title: Plot title. If None, uses the time series name.
            y_axis: Y-axis label. If None, uses the time series name.
            x_axis: X-axis label. If None, uses "Time".
            legend_name: Legend entry name. If None, uses the time series name.
            start: Start date for filtering data (datetime string or object).
            end: End date for filtering data (datetime string or object).
            
        Returns:
            Plotly Figure object with the time series plot.
        """
        processing_type_to_marker = {
            ProcessingType.SORTING: "circle",
            ProcessingType.REMOVE_DUPLICATES: "circle",
            ProcessingType.SMOOTHING: "circle",
            ProcessingType.FILTERING: "circle",
            ProcessingType.RESAMPLING: "circle",
            ProcessingType.GAP_FILLING: "triangle-up",
            ProcessingType.PREDICTION: "square",
            ProcessingType.TRANSFORMATION: "triangle-left",
            ProcessingType.DIMENSIONALITY_REDUCTION: "triangle-right",
            ProcessingType.FAULT_DETECTION: "x",
            ProcessingType.FAULT_IDENTIFICATION: "cross",
            ProcessingType.FAULT_DIAGNOSIS: "star",
            ProcessingType.OTHER: "diamond",
        }
        processing_type_to_mode = {
            ProcessingType.SORTING: "lines+markers",
            ProcessingType.REMOVE_DUPLICATES: "lines+markers",
            ProcessingType.SMOOTHING: "lines",
            ProcessingType.FILTERING: "lines+markers",
            ProcessingType.RESAMPLING: "lines+markers",
            ProcessingType.GAP_FILLING: "lines+markers",
            ProcessingType.PREDICTION: "lines+markers",
            ProcessingType.TRANSFORMATION: "lines+markers",
            ProcessingType.DIMENSIONALITY_REDUCTION: "lines+markers",
            ProcessingType.FAULT_DETECTION: "lines+markers",
            ProcessingType.FAULT_IDENTIFICATION: "lines+markers",
            ProcessingType.FAULT_DIAGNOSIS: "lines+markers",
            ProcessingType.OTHER: "markers",
        }
        split_series_name = self.series.name.split("_")
        if len(split_series_name) > 1:
            signal_name = split_series_name[0]
            series_name = "_".join(split_series_name[1:])
        else:
            signal_name = "<No signal>"
            series_name = self.series.name
        if not legend_name:
            legend_name = str(series_name)
        if not title:
            title = f"Time series plot of {signal_name}"
        if not y_axis:
            y_axis = f"{signal_name} values"
        if not x_axis:
            x_axis = "Time"
        last_step = self.processing_steps[-1] if self.processing_steps else None
        last_type = last_step.type if last_step else ProcessingType.OTHER
        marker = processing_type_to_marker[last_type]
        mode = processing_type_to_mode[last_type]
        # Apply date filtering if specified
        if start is not None or end is not None:
            filtered_series = self.series.copy()
            # Convert string dates to datetime if necessary
            if isinstance(start, str):
                start_date = pd.to_datetime(start)
            if isinstance(end, str):
                end_date = pd.to_datetime(end)

            # Apply filter
            if start_date is not None:
                filtered_series = filtered_series[filtered_series.index >= start_date]
            if end_date is not None:
                filtered_series = filtered_series[filtered_series.index <= end_date]
        else:
            filtered_series = self.series
        index_shift = 0
        for step in self.processing_steps:
            if step.type == ProcessingType.PREDICTION:
                index_shift += step.step_distance
        frequency = self.index_metadata.frequency
        if frequency:
            first_character = frequency[0]
            # check if the first character is a number
            if not first_character.isdigit():
                frequency = "1" + frequency
            x = filtered_series.index + pd.to_timedelta(frequency) * index_shift
        else:
            distance = self.series.index[1] - self.series.index[0]
            x = filtered_series.index + distance * index_shift
        fig = go.Figure(
            go.Scatter(
                x=x,
                y=filtered_series.values,
                name=legend_name,
                mode=mode,
                marker_symbol=marker,
            )
        )
        fig.update_layout(
            title=title,
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            showlegend=True,
        )
        return fig

    def remove_duplicated_steps(self):
        steps = self.processing_steps
        new_steps = []
        for step in steps:
            if step not in new_steps:
                new_steps.append(step)
        self.processing_steps = new_steps
        return self

    def __str__(self):
        return f"{self.series.name}"
    
    def _get_identifier(self) -> str:
        """Get the key identifier for TimeSeries."""
        series_name = getattr(self.series, 'name', 'unnamed')
        return f"series='{series_name}'"

    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for TimeSeries."""
        attrs = {
            'series_name': self.series.name,
            'series_length': len(self.series),
            'values_dtype': self.values_dtype,
            'created_on': self.created_on,
            'processing_steps_count': len(self.processing_steps),
            'processing_steps': self.processing_steps,
            'index_metadata': self.index_metadata
        }
        
        # Add date range if it's a datetime index
        if hasattr(self.series.index, 'min') and len(self.series) > 0:
            try:
                attrs['date_range'] = f"{self.series.index.min()} to {self.series.index.max()}"
            except (TypeError, ValueError):
                attrs['index_range'] = f"{self.series.index.min()} to {self.series.index.max()}"
        

        return attrs


class SignalTransformFunctionProtocol(Protocol):
    """Protocol defining the interface for Signal-level processing functions.
    
    This protocol specifies the required signature for functions that can be used
    with the Signal.process() method. Transform functions take multiple input
    time series and return processed results with complete processing metadata.
    
    Signal transform functions operate within a single measured parameter (Signal)
    and can take multiple time series representing different processing stages
    of that parameter. They are ideal for operations like smoothing, filtering,
    gap filling, and other single-parameter processing tasks.
    
    The protocol ensures consistent interfaces across different processing
    functions while maintaining complete audit trails of all transformations
    applied to environmental monitoring data.
    """

    def __call__(
        self, input_series: list[pd.Series], *args: Any, **kwargs: Any
    ) -> list[tuple[pd.Series, list[ProcessingStep]]]: 
        """Process input time series and return results with processing metadata.
                
                Args:
                    input_series (list[pd.Series]): List of pandas Series to be processed
                    *args: Function-specific positional arguments
                    **kwargs: Function-specific keyword arguments
                    
                Returns:
                    list[tuple[pd.Series, list[ProcessingStep]]]: List of (processed_series, processing_steps) tuples
                """
        ...

class Signal(BaseModel, DisplayableBase):
    """Collection of related time series representing a measured parameter.
    
    A Signal groups multiple time series that represent the same physical
    parameter (e.g., temperature) at different processing stages or from
    different processing paths. This enables comparison between raw and
    processed data, evaluation of different processing methods, and
    maintenance of data lineage.
    
    Signals handle the naming conventions for time series, ensuring consistent
    identification across processing workflows. They support processing
    operations that can take multiple input time series and produce new
    processed versions with complete metadata preservation.
    
    """

    model_config: dict = {"arbitrary_types_allowed": True}
    created_on: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(), description="Timestamp when this Signal was created")
    last_updated: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(), description="Timestamp of the most recent modification to this Signal")
    input_data: Optional[Union[pd.Series, pd.DataFrame, TimeSeries, list[TimeSeries], dict[str, TimeSeries]]] = Field(
        default=None, 
        description="Initial data used to create the Signal (removed after initialization)"
    )
    name: str = Field(default="signal", description="Name identifying this signal with automatic numbering (e.g., 'temperature#1')")
    units: str = Field(default="unit", description="Units of measurement for this parameter (e.g., '°C', 'mg/L', 'NTU')")
    provenance: DataProvenance = Field(
        default_factory=lambda: DataProvenance(
            source_repository="unknown",
            project="unknown", 
            location="unknown",
            equipment="unknown",
            parameter="unknown",
            purpose="unknown",
            metadata_id="unknown",
        ),
        description="Information about the source and context of this signal's data"
    )
    time_series: dict[str, TimeSeries] = Field(
        default_factory=lambda: dict(), 
        description="Dictionary mapping time series names to TimeSeries objects for this signal"
    )

    def __init__(self, **data):
        super().__init__(**data)  # Initialize Pydantic model with given data
        name = data.get("name")
        if name:
            self.update_numbered_signal_name()
        data_input = data.get("input_data", None)
        current_data = data.get("time_series")
        if data_input is None and not current_data:
            default_state = "RAW"
            default_name = f"default_{default_state}"
            data_input = pd.Series(name=default_name, dtype=object)
            self.time_series = {
                default_name: TimeSeries(series=data_input, processing_steps=[])
            }
        if isinstance(data_input, pd.Series):
            new_name = self.new_ts_name(str(data_input.name))
            data_input.name = new_name
            self.time_series = {
                new_name: TimeSeries(series=data_input, processing_steps=[])
            }
        elif isinstance(data_input, pd.DataFrame):
            for col in data_input.columns:
                ser = data_input[col]
                new_name = self.new_ts_name(str(ser.name))
                ser.name = new_name
                self.time_series[new_name] = TimeSeries(
                    series=data_input[col], processing_steps=[]
                )
        elif isinstance(data_input, TimeSeries):
            old_name = data_input.series.name
            new_name = self.new_ts_name(str(old_name))
            data_input.series.name = new_name
            self.time_series = {new_name: data_input}
        elif isinstance(data_input, list) and all(
            isinstance(item, TimeSeries) for item in data_input
        ):
            for ts in data_input:
                new_name = self.new_ts_name(ts.series.name)
                ts.series.name = new_name
                self.time_series[new_name] = ts
        elif isinstance(data_input, dict) and all(
            isinstance(item, TimeSeries) for item in data_input.values()
        ):
            for old_name, ts in data_input.items():
                new_name = self.new_ts_name(old_name)
                ts.series.name = new_name
                self.time_series[new_name] = ts
        elif current_data:
            pass
        else:
            raise ValueError(
                f"Received data of type {type(data_input)}. Valid data types are pd.Series, pd.DataFrame, TimeSeries, list of TimeSeries, or dict of TimeSeries."
            )
        if "last_updated" in data.keys():
            lu = data["last_updated"]
            if isinstance(lu, str):
                format_string = "%Y-%m-%dT%H:%M:%S.%f"
                lu = datetime.datetime.strptime(lu, format_string)
            self.last_updated = lu
        del self.input_data

    def new_ts_name(self, old_name: str) -> str:
        separator = "_"
        if separator not in old_name:
            rest = old_name
        else:
            _, rest = old_name.split(separator, 1)
        number_indicator = "#"
        if number_indicator in rest:
            rest, number_str = rest.split(number_indicator)
            number = int(number_str)
        else:
            number = 1
        return number_indicator.join([separator.join([self.name, rest]), str(number)])

    def add(self, ts: TimeSeries) -> None:
        old_name = ts.series.name
        new_name = self.new_ts_name(str(old_name))
        new_name = self.update_numbered_ts_name(new_name)
        ts.series.name = new_name
        self.time_series[new_name] = ts

    def remove(self, ts_name: str) -> None:
        self.time_series.pop(ts_name)

    @property
    def all_time_series(self):
        return list(self.time_series.keys())

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if (
            name != "last_updated"
        ):  # Avoid updating when the modified field is 'last_updated' itself
            super().__setattr__("last_updated", datetime.datetime.now())

    def update_numbered_signal_name(self):
        if "#" in self.name:
            return
        else:
            self.name = f"{self.name}#1"

    def max_ts_name_number(self, names: list[str]) -> dict[str, int]:
        full_names = list(self.time_series.keys())
        # remove signal by splitting on "_" and keeping only the second part
        names = [name.split("_")[1] for name in full_names]
        names_no_numbers = [name.split("#")[0] for name in names]
        numbers = [name.split("#")[1] for name in names if "#" in name]
        name_numbers = {}
        for name, number in zip(names_no_numbers, numbers):
            if name in name_numbers.keys():
                name_numbers[name] = max(name_numbers[name], number)
            else:
                name_numbers[name] = number
        return name_numbers

    def update_numbered_ts_name(self, name: str) -> str:
        name_max_number = self.max_ts_name_number(self.all_time_series)
        signal_name, name = name.split("_")  # remove the signal name
        if "#" in name:
            name, num = name.split("#")
            num = int(num)
            if name in name_max_number.keys():
                new_num = int(name_max_number[name]) + 1
                return f"{signal_name}_{name}#{new_num}"
            else:
                return f"{signal_name}_{name}#1"
        else:
            if name in name_max_number.keys():
                new_num = int(name_max_number[name]) + 1
                return f"{signal_name}_{name}#{new_num}"
            else:
                return f"{signal_name}_{name}#1"

    def process(
        self,
        input_time_series_names: list[str],
        transform_function: SignalTransformFunctionProtocol,
        *args: Any,
        **kwargs: Any,
    ) -> "Signal":
        """
        Processes the signal data using a transformation function.

        Args:
            input_time_series_names (list[str]): List of names of the input time series to be processed.
            transform_function (SignalTransformFunctionProtocol): The transformation function to be applied.
            *args: Additional positional arguments to be passed to the transformation function.
            **kwargs: Additional keyword arguments to be passed to the transformation function.

        Returns:
            Signal: The updated Signal object after processing.
        """
        if any(
            input_column not in self.all_time_series
            for input_column in input_time_series_names
        ):
            raise ValueError(
                f"One or more input columns not found in the Signal object. Available series are {self.all_time_series}"
            )
        input_series = [
            self.time_series[name].series.copy() for name in input_time_series_names
        ]
        outputs = transform_function(input_series, *args, **kwargs)
        for out_series, new_steps in outputs:
            all_steps = []
            for input_name in input_time_series_names:
                input_steps = self.time_series[input_name].processing_steps
                all_steps.extend(input_steps.copy())
            cleaned_steps = []
            for step in new_steps:
                cleaned_step = self.update_processing_step_input_series_names(step)
                cleaned_steps.append(cleaned_step)
            all_steps.extend(cleaned_steps)
            new_ts = TimeSeries(series=out_series, processing_steps=all_steps)
            new_ts = new_ts.remove_duplicated_steps()
            new_ts_name = str(new_ts.series.name)
            new_ts.series.name = self.update_numbered_ts_name(new_ts_name)
            self.time_series[new_ts.series.name] = new_ts
        return self

    def update_processing_step_input_series_names(self, step: ProcessingStep):
        existing_ts_names = self.all_time_series
        max_ts_name_number = self.max_ts_name_number(existing_ts_names)
        for input_name in step.input_series_names:
            if "#" in input_name:
                signal_name, ts_name = input_name.split("_")
                name, num = ts_name.split("#")
                num = int(num)
                if name in max_ts_name_number.keys():
                    max_num = int(max_ts_name_number[name])
                    new_name = f"{signal_name}_{name}#{max_num}"
                else:
                    new_name = f"{signal_name}_{name}#1"
                step.input_series_names.remove(input_name)
                step.input_series_names.append(new_name)
        return step

    def __repr__(self):
        return f"Signal(name={self.name}, units={self.units}, provenance={self.provenance}, last_updated={self.last_updated}, created_on={self.created_on}, time_series={[ts for ts in self.time_series.keys()]})"

    def __str__(self):
        return f"Signal '{self.name}', units={self.units}, time_series={self.all_time_series}"

    def _to_dataframe(self):
        return pd.DataFrame(
            {ts_name: ts.series for ts_name, ts in self.time_series.items()}
        )

    def rename(self, new_signal_name: str):
        if new_signal_name == self.name:
            return
        new_dico = {}
        for ts_name in self.time_series.keys():
            _, ts_only_name = ts_name.split("_")
            ts = self.time_series[ts_name]
            new_ts_name = f"{new_signal_name}_{ts_only_name}"
            ts.series.name = new_ts_name
            new_dico[new_ts_name] = ts
        self.time_series = new_dico
        self.name = new_signal_name

    def _save_data(self, path: str):
        # combine all time series into a single dataframe
        directory = f"{path}/{self.name}_data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        for ts_name, ts in self.time_series.items():
            file_path = f"{directory}/{ts_name}.csv"
            ts.series.to_csv(file_path)
        return directory

    def metadata_dict(self):
        metadata = self.model_dump()
        # remove the actual data from the metadata
        ts_metadata = {}
        for ts_name, ts in self.time_series.items():
            ts_metadata[ts_name] = ts.metadata_dict()
        metadata["time_series"] = ts_metadata
        return metadata

    def _save_metadata(self, path: str):
        metadata = self.metadata_dict()
        file_path = f"{path}/{self.name}_metadata.yaml"
        with open(file_path, "w") as f:
            yaml.dump(metadata, f)
        return file_path

    def save(self, destination: str, zip: bool = True):
        if not os.path.exists(destination):
            os.makedirs(destination)
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 2: Save metadata file
            self._save_metadata(temp_dir)
            # Prepare the subdirectory for signal data
            self._save_data(temp_dir)
            if not zip:
                # Move the metadata file to the destination
                shutil.move(f"{temp_dir}/{self.name}_metadata.yaml", destination)
                # Move the data directory to the destination
                shutil.move(f"{temp_dir}/{self.name}_data", destination)
            else:
                # Zip the contents of the temporary directory, not the directory itself
                zip_directory_contents(temp_dir, f"{destination}/{self.name}.zip")

    def _load_data_from_directory(self, path: str):
        for file in os.listdir(path):
            if file.endswith(".csv"):
                ts_name = file.split(".")[0]
                self.time_series[ts_name] = TimeSeries.load(
                    data_file_path=f"{path}/{file}"
                )
        return self

    def _load_metadata(self, path: str):
        with open(path, "r") as f:
            metadata = yaml.safe_load(f)
        self.name = metadata["name"]
        self.units = metadata["units"]
        self.provenance = DataProvenance(**metadata["provenance"])
        self.created_on = metadata["created_on"]
        for name, ts_meta in metadata["time_series"].items():
            self.time_series[name] = TimeSeries(
                series=self.time_series[name].series,
                processing_steps=[
                    ProcessingStep(**step) for step in ts_meta["processing_steps"]
                ],
                index_metadata=IndexMetadata(**ts_meta["index_metadata"]),
                values_dtype=ts_meta["values_dtype"],
            )

        self.last_updated = metadata["last_updated"]
        return None

    @staticmethod
    def load_from_directory(source_path: str, signal_name: str) -> "Signal":
        # create a new signal object from data and metadata
        source_p = Path(source_path)
        parent_dir = source_p.parent
        remove_temp_dir = False
        # if provided with a zip file, start by extracting the contents to a temporary directory
        if source_p.is_file() and source_p.suffix == ".zip":
            # Open the zip file
            # Create a temporary directory to extract the contents
            temp_dir = f"{parent_dir}/tmp"
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(source_path, "r") as zip_ref:
                # Extract all the contents into the temporary directory
                zip_ref.extractall(temp_dir)
            source_p = Path(temp_dir)
            remove_temp_dir = True
        elif not source_p.is_dir():
            raise ValueError(
                f"Invalid path {source_path} provided. Must be a directory or a zip file that contain data and metadata files."
            )
        dir_items = os.listdir(source_p)
        data_subdir = f"{signal_name}_data"
        if data_subdir not in dir_items:
            raise ValueError(
                f"Invalid path {source_path} provided. Must contain a directory named {data_subdir} with the data files."
            )
        data_dir = str(source_p / data_subdir)
        metadata_file = f"{source_p}/{signal_name}_metadata.yaml"
        if not os.path.exists(metadata_file):
            raise ValueError(
                f"Invalid path {source_path} provided. Must contain a metadata file named {signal_name}_metadata.yaml."
            )
        signal = Signal._load_from_files(data_dir, metadata_file)
        if remove_temp_dir:
            shutil.rmtree(temp_dir)
        return signal

    @staticmethod
    def _load_from_files(data_directory: str, metadata_file: str) -> "Signal":
        with open(metadata_file, "r") as f:
            metadata = yaml.safe_load(f)
        signal = Signal._load_from_data_dir_and_meta_dict(data_directory, metadata)
        return signal

    @staticmethod
    def _load_from_data_dir_and_meta_dict(
        data_directory: str, metadata: dict
    ) -> "Signal":
        signal = Signal(**metadata)
        ts_metadata = metadata["time_series"]
        for ts_name, ts_meta in ts_metadata.items():
            data_file = f"{data_directory}/{ts_name}.csv"
            if not os.path.exists(data_file):
                raise ValueError(
                    f"Invalid path {data_file} provided. Must contain a data file named {ts_name}.csv."
                )
            ts = TimeSeries.load(data_file_path=data_file, metadata=ts_meta)
            signal.time_series[ts_name] = ts
        signal.last_updated = metadata["last_updated"]
        return signal

    def plot(
        self,
        ts_names: List[str],
        title: Optional[str] = None,
        y_axis: Optional[str] = None,
        x_axis: Optional[str] = None,
        start: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
        end: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
    ) -> go.Figure:
        """
        Create an interactive Plotly plot with multiple time series from this signal.
        
        Each time series is plotted with different colors and appropriate styling based
        on their processing types. Temporal shifting is applied automatically for prediction data.
        
        Args:
            ts_names: List of time series names to plot. Must exist in this signal.
            title: Plot title. If None, uses "Time series plot of {signal_name}".
            y_axis: Y-axis label. If None, uses "{signal_name} ({units})".
            x_axis: X-axis label. If None, uses "Time".
            start: Start date for filtering data (datetime string or object).
            end: End date for filtering data (datetime string or object).
            
        Returns:
            Plotly Figure object with multiple time series traces.
        """
        if not title:
            title = f"Time series plot of {self.name}"
        if not y_axis:
            y_axis = f"{self.name} ({self.units})"
        if not x_axis:
            x_axis = "Time"
        fig = go.Figure()
        for ts_name in ts_names:
            # recover the scatter trace from the plot of the time series
            ts = self.time_series[ts_name]
            ts_fig = ts.plot(legend_name=ts_name, start=start, end=end)
            ts_trace = ts_fig.data[0]
            fig.add_trace(ts_trace)

        fig.update_layout(
            title=title,
            xaxis_title=x_axis,
            yaxis_title=y_axis,
        )
        return fig

    def build_dependency_graph(self, ts_name: str) -> List[Dict[str, Any]]:
        """
        Build a data structure that represents all the processig steps and their dependencies for a given time series.
        """
        dependencies = []
        if ts_name not in self.time_series.keys():
            raise ValueError(f"Time series {ts_name} not found in the signal.")
        ts = self.time_series[ts_name]
        if not ts.processing_steps:
            return dependencies
        last_step = ts.processing_steps[-1]
        input_series_names = last_step.input_series_names
        for input_series_name in input_series_names:
            current_dependency = {
                "step": last_step.function_info.name,
                "type": last_step.type,
                "origin": input_series_name,
                "destination": ts_name,
            }
            dependencies.append(current_dependency)
            dependencies.extend(self.build_dependency_graph(input_series_name))
        return dependencies

    def plot_dependency_graph(self, ts_name: str) -> go.Figure:
        """
        Create a dependency graph visualization showing processing lineage for a time series.
        
        The graph displays time series as colored rectangles connected by lines representing
        processing functions. The flow is temporal from left to right.
        
        Args:
            ts_name: Name of the time series to trace dependencies for.
            
        Returns:
            Plotly Figure object with the dependency graph visualization.
        """
        dependencies = self.build_dependency_graph(ts_name)
        time_series_in_deps = set(
            [dep["origin"] for dep in dependencies]
            + [dep["destination"] for dep in dependencies]
        )
        times_in_deps = {}
        for ts_name in time_series_in_deps:
            if ts_name not in self.time_series.keys():
                times_in_deps[ts_name] = None
            else:
                ts = self.time_series[ts_name]
                times_in_deps[ts_name] = ts.created_on
        min_time = min(times_in_deps.values()) if times_in_deps else self.created_on
        for ts_name, ts_time in times_in_deps.items():
            if ts_time is None:
                times_in_deps[ts_name] = min_time
        ts_times = list(times_in_deps.items())

        sorted_times = sorted(ts_times, key=lambda x: x[1])

        n_ts = len(ts_times)
        # create a plotly figure
        fig = go.Figure()
        # the figure will have nodes (representing Time Series) and arrows (representing processing steps)
        # The x position of the nodes will be determined by the time of creation of the time series
        # The y position of the nodes will be staggered to avoid overlap
        # The nodes will be rectangles with labels in the middle for the ts name
        # The arrows will be lines with labels for the processing step name
        ts_box_positions = {}
        if len(sorted_times) == 0:
            # no time series to plot
            # Add annotation in the middle in a box that says "No dependencies"
            fig.add_annotation(
                x=0.5,
                y=0.5,
                text="(No dependencies)",
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(size=20),
            )
        else:
            for i, (ts_name, ts_time) in enumerate(sorted_times):
                box_positions = {
                    "x0": i,
                    "x1": i + 1,
                    "y0": i / n_ts,
                    "y1": (i + 1) / n_ts,
                    "x_middle": i + 0.5,
                    "y_middle": (i + 0.5) / n_ts,
                }
                fig.add_shape(
                    type="rect",
                    x0=box_positions["x0"] + 0.1,
                    y0=box_positions["y0"] + 0.1,
                    x1=box_positions["x1"] - 0.1,
                    y1=box_positions["y1"] - 0.1,
                    line=dict(color="black", width=2),
                    fillcolor=PLOT_COLORS[i % len(PLOT_COLORS)],
                )
                fig.add_annotation(
                    x=box_positions["x_middle"],
                    y=box_positions["y_middle"],
                    text=ts_name,
                    showarrow=False,
                    # refer to x and y axes in data coordinates
                    xref="x",
                    yref="y",
                )
                ts_box_positions[ts_name] = box_positions
            for i, dep in enumerate(dependencies):
                origin = dep["origin"]
                destination = dep["destination"]
                origin_pos = ts_box_positions[origin]
                destination_pos = ts_box_positions[destination]
                # dependency lines
                fig.add_shape(
                    type="line",
                    x0=origin_pos["x1"] - 0.1,
                    y0=origin_pos["y_middle"],
                    x1=destination_pos["x0"] + 0.1,
                    y1=destination_pos["y_middle"],
                    line=dict(color="black", width=2),
                )
                # dependency labels
                fig.add_annotation(
                    x=(origin_pos["x_middle"] + destination_pos["x_middle"]) / 2,
                    y=(origin_pos["y_middle"] + destination_pos["y_middle"]) / 2,
                    text=dep["step"],
                    showarrow=False,
                    xref="x",
                    yref="y",
                )
        fig.update_layout(
            title=f"Dependency graph for time series {ts_name}",
            xaxis_title="Time",
            yaxis_title="Time Series",
            yaxis_range=[-0.2, 1.2],
            showlegend=False,
            # dont't show the y tick labels
            yaxis=dict(showticklabels=False),
        )
        return fig

        # # create a timeline with a vertical line for each step
        # # build a dict with a color for each type of processing step
        # types_in_graph = set([step["type"] for step in dependencies])
        # colors = {}
        # for i, step_type in enumerate(types_in_graph):
        #     colors[step_type] = PLOT_COLORS[i % len(PLOT_COLORS)]
        # base_date = self.created_on
        # inputs_in_deps = sorted(
        #     list(
        #         set(  # get all the inputs in the dependencies
        #             [
        #                 input_name
        #                 for step in dependencies
        #                 for input_name in step["inputs"]
        #             ]
        #         )
        #     )
        # )
        # n_inputs = len(inputs_in_deps)
        # for i, step in enumerate(dependencies):
        #     x = [step["time"], step["time"]]
        #     y = [0, 1]
        #     fig.add_trace(
        #         go.Scatter(
        #             x=x,
        #             y=y,
        #             mode="lines",
        #             name=step["name"].title(),
        #             line=dict(color=colors[step["type"]]),
        #         )
        #     )
        #     # add a label for the step necxt to the line
        #     fig.add_annotation(
        #         x=step["time"],
        #         y=1,
        #         text=step["name"].title(),
        #         showarrow=False,
        #         yshift=10,
        #     )
        # # add a line for the creation of the signal
        # fig.add_trace(
        #     go.Scatter(
        #         x=[base_date, base_date],
        #         y=[0, 1],
        #         mode="lines",
        #         name="Signal creation",
        #         line=dict(color="black"),
        #     )
        # )
        # fig.add_annotation(
        #     x=base_date,
        #     y=1,
        #     text="Signal creation".title(),
        #     showarrow=False,
        #     yshift=10,
        # )
        # # for each step, create pointed arrows from the last line (either the signal creation or the previous step) to the current step
        # for i, step in enumerate(dependencies):
        #     for input_name in sorted(step["inputs"]):
        #         # determine the x position of the arrow for the input
        #         x = base_date
        #         if i > 0:
        #             x0 = dependencies[i - 1]["time"]
        #         else:
        #             x0 = base_date
        #         x1 = step["time"]
        #         input_index = inputs_in_deps.index(input_name)
        #         y = 1 - (input_index + 1) / (n_inputs + 1)
        #         fig.add_annotation(
        #             xref="x",
        #             yref="y",
        #             axref="x",
        #             ayref="y",
        #             x=x1,
        #             y=y,
        #             ax=x0,
        #             ay=y,
        #             showarrow=True,
        #             arrowhead=2,
        #             arrowsize=1,
        #             arrowwidth=2,
        #             arrowcolor="black",
        #         )
        #         # add a label for the input right above the arrow
        #         fig.add_annotation(
        #             x=x0 + (x1 - x0) / 2,
        #             y=y,
        #             text=input_name,
        #             showarrow=False,
        #             yshift=10,
        #         )
        # fig.update_layout(
        #     title=f"Dependency graph for time series {ts_name}",
        #     xaxis_title="Time",
        #     yaxis_title="Steps",
        #     showlegend=False,
        #     # dont't show the y tick labels
        #     yaxis=dict(showticklabels=False),
        # )
        # return fig

    def __eq__(self, other):
        if not isinstance(other, Signal):
            return False
        if self.name != other.name:
            return False
        if self.units != other.units:
            return False
        if self.provenance != other.provenance:
            return False
        if self.created_on != other.created_on:
            return False
        if self.last_updated != other.last_updated:
            return False
        if len(self.time_series) != len(other.time_series):
            return False
        for k, v in self.time_series.items():
            if k not in other.time_series:
                return False
            if v != other.time_series[k]:
                return False
        return True
    
    def _get_identifier(self) -> str:
        """Get the key identifier for Signal."""
        return f"name='{self.name}'"

    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for Signal."""
        attrs = {
            'name': self.name,
            'units': self.units,
            'provenance': self.provenance,
            'created_on': self.created_on,
            'last_updated': self.last_updated,
            'time_series_count': len(self.time_series),
        }
        # Return actual TimeSeries objects, not their attributes
        for timeseries_name, timeseries in self.time_series.items():
            attrs[f"timeseries_{timeseries_name}"] = timeseries
        return attrs

    
class DatasetTransformFunctionProtocol(Protocol):
    """Protocol defining the interface for Dataset-level processing functions.
    
    This protocol specifies the required signature for functions that can be used
    with the Dataset.process() method. These functions can operate across multiple
    signals and create new signals with cross-parameter relationships.
    
    Dataset transform functions are ideal for operations that require multiple
    parameters simultaneously, such as:
    - Calculating derived parameters (e.g., BOD/COD ratios)
    - Multivariate analysis and modeling
    - Cross-parameter quality control
    - System-wide fault detection
    - Process efficiency calculations
    
    The protocol ensures that new signals created by dataset processing maintain
    proper metadata inheritance and processing lineage from their input signals.
    
    Note:
        New signals created by dataset processing will have their project property
        automatically updated to match the parent dataset's project. The transform
        function is responsible for setting appropriate signal names, units,
        provenance parameters, and purposes.
    """

    def __call__(
        self,
        input_signals: list[Signal],
        input_series_names: list[str],
        *args: Any,
        **kwargs: Any,
    ) -> list[Signal]:
        """Process input signals and return new signals with processing metadata.
        
        Args:
            input_signals (list[Signal]): List of Signal objects containing input data
            input_series_names (list[str]): Specific time series names to use from input signals
            *args: Function-specific positional arguments  
            **kwargs: Function-specific keyword arguments
            
        Returns:
            list[Signal]: List of new Signal objects created by processing
        """
        ...


class Dataset(BaseModel, DisplayableBase):
    """Collection of signals representing a complete monitoring dataset.
    
    A Dataset groups multiple signals that are collected together as part of
    a monitoring project or analysis workflow. It provides project-level
    metadata and enables coordinated processing operations across multiple
    parameters.
    
    Datasets support cross-signal processing operations and maintain consistent
    naming conventions across all contained signals. They provide the highest
    level of organization for environmental monitoring data with complete
    metadata preservation and serialization capabilities.
        
    """
    created_on: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp when this Dataset was created")
    last_updated: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp of the most recent modification to this Dataset")
    name: str = Field(description="Name identifying this dataset")
    description: Optional[str] = Field(default=None, description="Detailed description of the dataset contents and purpose")
    owner: Optional[str] = Field(default=None, description="Person or organization responsible for this dataset")
    signals: dict[str, Signal] = Field(description="Dictionary mapping signal names to Signal objects in this dataset")
    purpose: Optional[str] = Field(default=None, description="Purpose or objective of this dataset (e.g., 'compliance_monitoring', 'research')")
    project: Optional[str] = Field(default=None, description="Project or study name associated with this dataset")


    def __init__(self, **data):
        super().__init__(**data)
        last_updated = self.last_updated
        renamed_dict = {}
        for signal_key, signal in self.signals.items():
            renamed_dict[signal.name] = signal
        self.signals = renamed_dict
        new_dict = {}
        for signal_name, signal in self.signals.items():
            if "#" not in signal_name:
                new_signal_name = self.update_numbered_name(signal_name)
                signal.rename(new_signal_name)
                new_dict[new_signal_name] = signal
            else:
                new_dict[signal_name] = signal
        self.signals = new_dict

        self.last_updated = last_updated
        return

    def max_name_number(self) -> dict[str, int]:
        full_names = self.all_signals
        names_no_numbers = [name.split("#")[0] for name in full_names]
        numbers = [int(name.split("#")[1]) for name in full_names if "#" in name]
        name_numbers = {}
        for name, number in zip(names_no_numbers, numbers):
            if name in name_numbers.keys():
                name_numbers[name] = max(name_numbers[name], number)
            else:
                name_numbers[name] = number
        return name_numbers

    def update_numbered_name(self, name: str) -> str:
        name_max_number = self.max_name_number()
        if "#" in name:
            name, num = name.split("#")
            num = int(num)
            if name in name_max_number.keys():
                new_num = name_max_number[name] + 1
                return f"{name}#{new_num}"
            else:
                return f"{name}#1"
        else:
            if name in name_max_number.keys():
                new_num = name_max_number[name] + 1
                return f"{name}#{new_num}"
            else:
                return f"{name}#1"

    def add(self, signal: Signal) -> "Dataset":
        signal_name = signal.name
        new_name = self.update_numbered_name(signal_name)
        signal.rename(new_name)
        self.signals[new_name] = signal
        return self

    def remove(self, signal_name: str) -> None:
        self.signals.pop(signal_name)

    model_config: dict = {"arbitrary_types_allowed": True}

    @property
    def all_signals(self):
        return list(self.signals.keys())

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if (
            name != "last_updated"
        ):  # Avoid updating when the modified field is 'last_updated' itself
            super().__setattr__("last_updated", datetime.datetime.now())
        else:
            super().__setattr__("last_updated", value)

    def metadata_dict(self):
        metadata = self.model_dump()
        # remove the actual data from the metadata
        metadata["signals"] = {
            signal_name: signal.metadata_dict()
            for signal_name, signal in self.signals.items()
        }
        return metadata

    def save(self, directory: str) -> "Dataset":
        name = self.name
        dir_path = Path(directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # save data and metadata and return a zipped file with both
        dataset_metadata_path = dir_path / (name + ".yaml")

        metadata = self.metadata_dict()
        # save the metadata in the archive
        with open(dataset_metadata_path, "w") as f:
            yaml.dump(metadata, f)
        dir_name = f"{self.name}_data"
        with NamedTempDirectory(name=dir_name) as temp_dir:
            for signal in self.signals.values():
                signal.save(temp_dir, zip=False)
            zip_directory(temp_dir, f"{directory}/{name}.zip")
        with zipfile.ZipFile(f"{directory}/{name}.zip", "a") as zf:
            zf.write(dataset_metadata_path, f"{name}_metadata.yaml")
        os.remove(dataset_metadata_path)
        return self

    def _load_signal(self, dir_path: str, metadata: dict) -> Signal:
        signal = Signal._load_from_data_dir_and_meta_dict(dir_path, metadata)
        return signal

    @staticmethod
    def load(source_path: str, dataset_name: str):
        source_p = Path(source_path)
        parent_dir = source_p.parent
        remove_temp_dir = False
        # if provided with a zip file, start by extracting the contents to a temporary directory
        if source_p.is_file() and source_p.suffix == ".zip":
            # Open the zip file
            # Create a temporary directory to extract the contents
            temp_dir = f"{parent_dir}/tmp"
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(source_path, "r") as zip_ref:
                # Extract all the contents into the temporary directory
                zip_ref.extractall(temp_dir)
            source_p = Path(temp_dir)
            remove_temp_dir = True
        elif not source_p.is_dir():
            raise ValueError(
                f"Invalid path {source_path} provided. Must be a directory or a zip file that contain data and metadata files."
            )
        dir_items = os.listdir(source_p)
        dataset_metadata_file = f"{dataset_name}_metadata.yaml"
        if dataset_metadata_file not in dir_items:
            raise ValueError(
                f"Invalid path {source_path} provided. Must contain a metadata file named {dataset_metadata_file}."
            )
        dataset_metadata_path = source_p / dataset_metadata_file
        with open(dataset_metadata_path, "r") as f:
            metadata = yaml.safe_load(f)
        dataset = Dataset(**metadata)
        dataset_data_dir = f"{dataset_name}_data"
        for signal_name in dataset.signals.keys():
            data_dir_items = os.listdir(f"{source_p}/{dataset_data_dir}")
            signal_dir = f"{signal_name}_data"
            if signal_dir not in data_dir_items:
                raise ValueError(
                    f"Invalid path {source_path} provided. Must contain a directory named {signal_dir} with the data files."
                )
            dataset.signals[signal_name] = dataset._load_signal(
                f"{source_p}/{dataset_data_dir}/{signal_dir}",
                metadata["signals"][signal_name],
            )
        dataset.last_updated = metadata["last_updated"]
        if remove_temp_dir:
            shutil.rmtree(temp_dir)
        return dataset

    def process(
        self,
        input_time_series_names: list[str],
        transform_function: DatasetTransformFunctionProtocol,
        *args: Any,
        **kwargs: Any,
    ) -> "Dataset":
        """
        Processes the dataset data using a transformation function.

        Args:
            input_time_series_names (list[str]): List of names of the input time series to be processed.
            transform_function (DatasetTransformFunctionProtocol): The transformation function to be applied.
            *args: Additional positional arguments to be passed to the transformation function.
            **kwargs: Additional keyword arguments to be passed to the transformation function.

        Returns:
            Dataset: The updated Dataset object after processing. The transformation will produce new Signals with the processed time series data.
        """
        names = []
        for signal in self.signals.values():
            names.extend(signal.all_time_series)

        if any(input_column not in names for input_column in input_time_series_names):
            raise ValueError(
                f"One or more input columns not found in the Dataset object. Available series are {names}"
            )
        split_names = []
        for name in input_time_series_names:
            signal_name, ts_name = name.split("_")
            split_names.append((signal_name, ts_name))
        input_signals = [
            copy.deepcopy(self.signals[signal_name]) for signal_name, _ in split_names
        ]
        output_signals = transform_function(
            input_signals, input_time_series_names, *args, **kwargs
        )
        for out_signal in output_signals:
            out_signal_name = out_signal.name
            new_signal_name = self.update_numbered_name(out_signal_name)
            out_signal.rename(new_signal_name)
            self.signals[new_signal_name] = out_signal
            out_split_names = [x.split("_") for x in out_signal.all_time_series]
            for out_signal_name, out_ts_name in out_split_names:
                out_all_steps = []
                out_full_ts_name = f"{out_signal_name}_{out_ts_name}"
                out_ts = out_signal.time_series[out_full_ts_name]
                new_steps = out_ts.processing_steps
                for input_name in input_time_series_names:
                    in_signal_name, in_ts_name = input_name.split("_")
                    in_full_ts_name = f"{in_signal_name}_{in_ts_name}"
                    input_steps = (
                        self.signals[in_signal_name]
                        .time_series[in_full_ts_name]
                        .processing_steps
                    )
                    out_all_steps.extend(input_steps.copy())
                out_all_steps.extend(new_steps)
                out_new_ts = TimeSeries(
                    series=out_ts.series, processing_steps=out_all_steps
                )
                out_new_ts = out_new_ts.remove_duplicated_steps()
                self.signals[new_signal_name].time_series[out_full_ts_name] = out_new_ts
        return self

    def plot(
        self,
        signal_names: List[str],
        ts_names: List[str],
        title: Optional[str] = None,
        y_axis: Optional[str] = None,
        x_axis: Optional[str] = None,
        start: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
        end: Optional[Union[str, datetime.datetime, pd.Timestamp]] = None,
    ) -> go.Figure:
        """
        Create a multi-subplot visualization comparing time series across signals.
        
        Each signal gets its own subplot with shared x-axis (time). Only time series
        that exist in each signal are plotted. Individual y-axis labels include units.
        
        Args:
            signal_names: List of signal names to plot. Must exist in this dataset.
            ts_names: List of time series names to plot from each signal.
            title: Plot title. If None, uses "Time series plots of dataset {dataset_name}".
            y_axis: Base Y-axis label. If None, uses "Values".
            x_axis: X-axis label. If None, uses "Time".
            start: Start date for filtering data (datetime string or object).
            end: End date for filtering data (datetime string or object).
            
        Returns:
            Plotly Figure object with subplots for each signal.
        """
        if not title:
            title = f"Time series plots of dataset {self.name}"
        if not y_axis:
            y_axis = "Values"
        if not x_axis:
            x_axis = "Time"
        fig = make_subplots(
            rows=len(signal_names), cols=1, shared_xaxes=True, vertical_spacing=0.02
        )
        for i, signal_name in enumerate(signal_names):
            signal = self.signals[signal_name]
            # get the ts_names items that are in the signal
            signal_ts_names = [
                ts_name for ts_name in ts_names if ts_name in signal.all_time_series
            ]
            for ts_name in signal_ts_names:
                ts = signal.time_series[ts_name]
                ts_fig = ts.plot(legend_name=ts_name, start=start, end=end)
                ts_trace = ts_fig.data[0]
                fig.add_trace(ts_trace, row=i + 1, col=1)
        fig.update_layout(
            title=title,
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            showlegend=True,
        )
        # by default the x_axis title appears under the first subplot only. We want it under all subplots
        for i in range(len(signal_names)):
            fig.update_xaxes(title_text=x_axis, row=i + 1, col=1)
            fig.update_yaxes(
                title_text=f"{signal_names[i]} {y_axis} ({self.signals[signal_names[i]].units})",
                row=i + 1,
                col=1,
            )
        return fig

    def __eq__(self, other):
        if not isinstance(other, Dataset):
            return False
        if self.name != other.name:
            return False
        if self.description != other.description:
            return False
        if self.owner != other.owner:
            return False
        if self.purpose != other.purpose:
            return False
        if self.project != other.project:
            return False
        if self.created_on != other.created_on:
            return False
        if self.last_updated != other.last_updated:
            return False
        if len(self.signals) != len(other.signals):
            return False
        for name in self.signals.keys():
            if self.signals[name] != other.signals[name]:
                return False
        return True

    def __str__(self):
        return f"Dataset {self.name}, owner={self.owner}, purpose={self.purpose}, signals={self.all_signals}"

    def _get_identifier(self) -> str:
        """Get the key identifier for Dataset."""
        return f"name='{self.name}'"

    def _get_display_attributes(self) -> Dict[str, Any]:
        """Get attributes to display for Dataset."""
        attrs = {
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'purpose': self.purpose,
            'project': self.project,
            'created_on': self.created_on,
            'last_updated': self.last_updated,
            'signals_count': len(self.signals),
        }

        # Return actual Signal objects, not their attributes
        for signal_name, signal in self.signals.items():
            attrs[f"signal_{signal_name}"] = signal

        return attrs
