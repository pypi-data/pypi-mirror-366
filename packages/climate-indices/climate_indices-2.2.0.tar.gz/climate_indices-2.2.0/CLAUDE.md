# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for computing climate indices useful for drought monitoring and climate research. The library implements several standardized climate indices including SPI (Standardized Precipitation Index), SPEI (Standardized Precipitation Evapotranspiration Index), PET (Potential Evapotranspiration), PNP (Percentage of Normal Precipitation), and Palmer drought indices.

## Essential Development Commands

### Testing
- **Run all tests**: `uv run pytest` 
- **Run specific test file**: `uv run pytest tests/test_indices.py`
- **Run with coverage**: `uv run pytest --cov=climate_indices`

### Code Quality
- **Run linting**: `ruff check --fix` (configured in pyproject.toml)
- **Run formatting**: `ruff format .` (120 character line length)
- **Type checking**: `uv run mypy src/climate_indices` (if mypy is installed)

### Building and Installation
- **Install development dependencies**: `uv sync --dev` 
- **Build package**: `uv build`
- **Run CLI**: `uv run climate_indices` or `uv run python -m climate_indices`

### Documentation
- **Build docs**: `cd docs && make html` (Sphinx documentation)
- **Clean docs**: `cd docs && make clean`

## Code Architecture

### Core Module Structure

- **`src/climate_indices/`**: Main package directory
  - **`__main__.py`**: CLI entry point with comprehensive argument parsing and multiprocessing support
  - **`indices.py`**: High-level API for computing climate indices (SPI, SPEI, PET, etc.)
  - **`compute.py`**: Core computational functions and data validation
  - **`utils.py`**: Utility functions for data manipulation and logging
  - **`palmer.py`**: Palmer drought index calculations
  - **`eto.py`**: Evapotranspiration calculations (Thornthwaite, Hargreaves)
  - **`lmoments.py`**: L-moments statistical computations

### Key Design Patterns

#### Multiprocessing Architecture
The CLI uses a sophisticated multiprocessing system with shared memory arrays:
- Input data is loaded into shared memory using `multiprocessing.Array`
- Work is distributed across worker processes using chunk-based splitting
- Results are aggregated back into the main process for output

#### Data Validation and Transformation
- Input validation occurs in `compute._validate_array()`
- Data is automatically reshaped from 1D to 2D arrays based on periodicity
- Unit conversions are handled automatically (inches to mm, Fahrenheit to Celsius)

#### Index Computation Flow
1. **Data Loading**: NetCDF files are opened with xarray and chunked appropriately
2. **Validation**: Dimensions and coordinate variables are validated across datasets
3. **Preprocessing**: Data is converted to appropriate units and shared memory
4. **Parallel Processing**: Index computations are distributed across worker processes
5. **Output**: Results are written to NetCDF files with proper metadata

### Important Data Structures

#### Periodicity Enum
- `Periodicity.monthly`: 12 values per year
- `Periodicity.daily`: 366 values per year (leap year format)

#### Distribution Enum
- `Distribution.gamma`: Gamma distribution fitting for SPI/SPEI
- `Distribution.pearson`: Pearson Type III distribution fitting

#### Input Types
- `InputType.grid`: Gridded data with (lat, lon, time) dimensions
- `InputType.divisions`: US climate division data
- `InputType.timeseries`: 1D time series data

## Testing Framework

- Uses **pytest** with extensive fixture-based testing
- Test fixtures in `tests/conftest.py` provide sample datasets
- Fixtures include precipitation, temperature, and expected output arrays
- Tests cover both monthly and daily periodicities across multiple time scales

## CLI Usage Patterns

The main CLI supports complex workflows:

```bash
# SPI computation example
climate_indices --index spi --periodicity monthly --scales 1 3 6 12 \
  --netcdf_precip precip.nc --var_name_precip prcp \
  --calibration_start_year 1981 --calibration_end_year 2010 \
  --output_file_base output/spi

# Palmer indices (requires precipitation, temperature/PET, and AWC)
climate_indices --index palmers --periodicity monthly \
  --netcdf_precip precip.nc --var_name_precip prcp \
  --netcdf_temp temp.nc --var_name_temp tavg \
  --netcdf_awc awc.nc --var_name_awc awc \
  --calibration_start_year 1951 --calibration_end_year 2010 \
  --output_file_base output/palmer
```

## Development Notes

### Dependency Management
- Project uses uv for dependency management and virtual environments
- Core dependencies: scipy, xarray, dask, h5netcdf
- Development dependencies: pytest, black, ruff, coverage, sphinx-autodoc-typehints

### Python Version Support
- Supports Python 3.10 through 3.13
- Uses type hints throughout codebase
- Configured for modern Python features in pyproject.toml

### Performance Considerations
- Heavy use of NumPy arrays and vectorized operations
- Multiprocessing for large dataset processing
- Shared memory arrays to minimize data copying
- Chunked processing for memory efficiency with large NetCDF files

### Error Handling
- Comprehensive input validation with descriptive error messages
- Logging throughout with configurable levels
- Graceful handling of edge cases (NaN values, missing data)