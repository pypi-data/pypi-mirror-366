# EDF Reader

A lightweight EDF (European Data Format) file reader for Python that can handle discontinuities in EDF+D files.

## Description

EDF Reader is a Python package for reading EDF (European Data Format) files, which are commonly used for storing medical/biological signals like EEG data. This implementation is optimized for performance, especially when reading files over network drives, and can handle discontinuities in EDF+D format files.

Key features:
- Read EDF and EDF+D files
- Parse file headers and signal information
- Read signal data with time-based filtering
- Handle annotations and discontinuities in EDF+D files
- Optimized for performance with network drives

## Installation

You can install the package using pip:

```bash
pip install edf-reader
```

For development installation:

```bash
git clone https://gitlab.com/bbeer_group/development/epycom/edf_reader.git
cd edf_reader
pip install -e .
```

## Usage

Basic usage example:

```python
from edf_reader import EdfWrapper

# Open an EDF file
reader = EdfWrapper('/path/to/your/file.edf')

# Get basic information about the channels
channel_info = reader.read_ts_channel_basic_info()
print(channel_info)

# Read data from specific channels
# The time range is specified in microseconds UTC (uutc)
# [None, None] means the entire recording
data = reader.read_ts_channels_uutc(['Channel1', 'Channel2'], [None, None])

# Check for discontinuities in the recording
discontinuities = reader.get_discontinuities()
print(f"Found {len(discontinuities)} discontinuities")

# Close the file when done
reader.close()
```

## Testing

The package includes a comprehensive test suite using pytest. To run the tests, first install the development dependencies:

```bash
pip install -e .[dev]
```

Then run the tests using pytest:

```bash
pytest
```

Or use the provided test runner script:

```bash
./run_tests.py
```

The tests use mocks to avoid requiring actual EDF files, making them fast and reliable to run in any environment.

## License

This project is licensed under the BSD 3.0 License - see the LICENSE file for details.

## Authors

- Vojtech Travnicek - vojtech.travnicek@fnusa.cz, vojtech.travnicek@wavesurfers.science
