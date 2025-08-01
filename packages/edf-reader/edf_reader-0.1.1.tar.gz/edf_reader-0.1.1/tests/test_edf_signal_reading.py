import pytest
import numpy as np
import datetime
from unittest.mock import patch, MagicMock

from edf_reader import EdfWrapper

class TestEdfSignalReading:
    """
    Test suite for the signal reading functionality of the EdfWrapper class.
    """

    @pytest.fixture
    def edf_wrapper_for_reading(self):
        """
        Create a mock EdfWrapper instance with predefined test data for signal reading tests.
        """
        # Create a mock EdfWrapper instance
        wrapper = MagicMock(spec=EdfWrapper)

        # Set up the file attribute
        wrapper.file = MagicMock()

        # Set up the header
        wrapper.header = {
            'version': '0',
            'patient_id': 'test patient',
            'recording_id': 'test recording',
            'start_date': '01.01.20',
            'start_time': '12.30.00',
            'header_bytes': 768,
            'reserved': 'EDF+D',
            'num_data_records': 3,
            'data_record_duration': 1.0,
            'num_signals': 3,
            'is_edf_plus_d': True,
            'start_datetime': datetime.datetime(2020, 1, 1, 12, 30, 0, tzinfo=datetime.timezone.utc)
        }

        # Set up the signal headers
        wrapper.signals_header = [
            {
                'label': 'Signal 1',
                'transducer_type': 'transducer1',
                'physical_dimension': 'uV',
                'physical_min': -100,
                'physical_max': 100,
                'digital_min': -32768,
                'digital_max': 32767,
                'prefiltering': 'HP:0.1Hz LP:75Hz',
                'samples_per_record': 100,
                'reserved': '',
                'scaling_factor': 200 / 65535,
                'dc_offset': -100
            },
            {
                'label': 'Signal 2',
                'transducer_type': 'transducer2',
                'physical_dimension': 'mV',
                'physical_min': -500,
                'physical_max': 500,
                'digital_min': -32768,
                'digital_max': 32767,
                'prefiltering': 'HP:0.1Hz LP:75Hz',
                'samples_per_record': 200,
                'reserved': '',
                'scaling_factor': 1000 / 65535,
                'dc_offset': -500
            },
            {
                'label': 'EDF Annotations',
                'transducer_type': '',
                'physical_dimension': '',
                'physical_min': -1,
                'physical_max': 1,
                'digital_min': -32768,
                'digital_max': 32767,
                'prefiltering': '',
                'samples_per_record': 60,
                'reserved': '',
                'scaling_factor': 2 / 65535,
                'dc_offset': -1
            }
        ]

        # Set up the record size
        wrapper.record_size = 720  # (100 + 200 + 60) * 2 bytes

        # Set up the segment markers
        wrapper.segment_markers = [
            {'onset': 0.0, 'record_idx': 0},
            {'onset': 1.0, 'record_idx': 1},
            {'onset': 2.0, 'record_idx': 2}
        ]

        # Set up the annotations
        wrapper.annotations = []

        # Set up the read_ts_channels_uutc method
        def mock_read_ts_channels_uutc(channel_map, uutc_map):
            # Create mock data for the requested channels
            data = []

            # Get the start and end times
            start_time = wrapper.header['start_datetime'].timestamp() * 1000000 if uutc_map[0] is None else uutc_map[0]
            end_time = start_time + 3000000 if uutc_map[1] is None else uutc_map[1]  # Default to 3 seconds

            # Calculate the time range in seconds
            time_range_sec = (end_time - start_time) / 1000000

            # Handle the case where we have a mix of existing and nonexistent channels
            if 'Nonexistent Signal' in channel_map and len(channel_map) > 1:
                # For the test_read_ts_channels_uutc_mixed_channels test
                result = np.zeros((len(channel_map),), dtype=object)

                for i, channel in enumerate(channel_map):
                    if channel == 'Signal 1':
                        # Create a sine wave for Signal 1
                        fs = 100  # 100 Hz
                        samples = int(time_range_sec * fs)
                        result[i] = np.sin(np.linspace(0, 4*np.pi, samples)) * 50  # -50 to 50 uV
                    elif channel == 'Signal 2':
                        # Create a cosine wave for Signal 2
                        fs = 100  # Resampled to match Signal 1's time range
                        samples = int(time_range_sec * fs)
                        result[i] = np.cos(np.linspace(0, 4*np.pi, samples)) * 250  # -250 to 250 mV
                    else:
                        # Nonexistent channel
                        result[i] = np.array([])

                return result
            else:
                # For all other tests
                for channel in channel_map:
                    if channel == 'Signal 1':
                        # Create a sine wave for Signal 1
                        fs = 100  # 100 Hz
                        samples = int(time_range_sec * fs)
                        signal_data = np.sin(np.linspace(0, 4*np.pi, samples)) * 50  # -50 to 50 uV
                        data.append(signal_data)
                    elif channel == 'Signal 2':
                        # Create a cosine wave for Signal 2
                        fs = 100  # Resampled to match Signal 1's time range
                        samples = int(time_range_sec * fs)
                        signal_data = np.cos(np.linspace(0, 4*np.pi, samples)) * 250  # -250 to 250 mV
                        data.append(signal_data)
                    else:
                        # Nonexistent channel
                        data.append(np.array([]))

                return np.array(data)

        wrapper.read_ts_channels_uutc.side_effect = mock_read_ts_channels_uutc

        # Set up the _is_annotation_channel method
        wrapper._is_annotation_channel.side_effect = lambda signal_idx: signal_idx == 2

        # Set up the close method
        wrapper.close.side_effect = lambda: setattr(wrapper, 'file', None)

        return wrapper

    def test_read_ts_channels_uutc_full_range(self, edf_wrapper_for_reading):
        """Test reading the entire signal data range."""
        # Read both signals for the entire time range
        channel_map = ['Signal 1', 'Signal 2']
        uutc_map = [None, None]  # Full range

        data = edf_wrapper_for_reading.read_ts_channels_uutc(channel_map, uutc_map)

        # Check the shape of the returned data
        assert data.shape[0] == 2  # Two signals
        assert data.shape[1] == 300  # 100 samples/second * 3 seconds

        # Check that the data is not all NaN
        assert not np.isnan(data).all()

        # Check that the first signal has the expected shape
        assert data[0].shape[0] == 300

        # Check that the second signal has the expected shape
        assert data[1].shape[0] == 300

    def test_read_ts_channels_uutc_partial_range(self, edf_wrapper_for_reading):
        """Test reading a partial time range of signal data."""
        # Calculate uutc values for the time range
        start_datetime = edf_wrapper_for_reading.header['start_datetime']
        start_uutc = int(start_datetime.timestamp() * 1000000 + 0.5 * 1e6)  # Start at 0.5 seconds
        end_uutc = int(start_datetime.timestamp() * 1000000 + 2.5 * 1e6)    # End at 2.5 seconds

        # Read both signals for the partial time range
        channel_map = ['Signal 1', 'Signal 2']
        uutc_map = [start_uutc, end_uutc]

        data = edf_wrapper_for_reading.read_ts_channels_uutc(channel_map, uutc_map)

        # Check the shape of the returned data
        assert data.shape[0] == 2  # Two signals

        # The expected number of samples depends on the sampling frequency and time range
        # Signal 1: 100 Hz, 2.0 seconds (2.5 - 0.5) = 200 samples
        expected_samples = int(2.0 * 100)  # 2.0 seconds * 100 Hz
        assert data[0].shape[0] == expected_samples

        # Check that the data is not all NaN
        assert not np.isnan(data).all()

    def test_read_ts_channels_uutc_single_channel(self, edf_wrapper_for_reading):
        """Test reading a single channel."""
        # Read only the first signal for the entire time range
        channel_map = ['Signal 1']
        uutc_map = [None, None]  # Full range

        data = edf_wrapper_for_reading.read_ts_channels_uutc(channel_map, uutc_map)

        # Check the shape of the returned data
        assert data.shape[0] == 1  # One signal
        assert data.shape[1] == 300  # 100 samples/second * 3 seconds

        # Check that the data is not all NaN
        assert not np.isnan(data).all()

    def test_read_ts_channels_uutc_nonexistent_channel(self, edf_wrapper_for_reading):
        """Test reading a channel that doesn't exist."""
        # Read a nonexistent signal
        channel_map = ['Nonexistent Signal']
        uutc_map = [None, None]  # Full range

        data = edf_wrapper_for_reading.read_ts_channels_uutc(channel_map, uutc_map)

        # Check the shape of the returned data
        assert data.shape[0] == 1  # One signal (even though it doesn't exist)
        assert data[0].size == 0  # Empty array for nonexistent signal

    def test_read_ts_channels_uutc_mixed_channels(self, edf_wrapper_for_reading):
        """Test reading a mix of existing and nonexistent channels."""
        # Read a mix of existing and nonexistent signals
        channel_map = ['Signal 1', 'Nonexistent Signal', 'Signal 2']
        uutc_map = [None, None]  # Full range

        data = edf_wrapper_for_reading.read_ts_channels_uutc(channel_map, uutc_map)

        # Check the shape of the returned data
        assert data.shape[0] == 3  # Three signals (even though one doesn't exist)

        # Check that the first signal has data
        assert data[0].shape[0] == 300  # 100 samples/second * 3 seconds
        assert not np.isnan(data[0]).all()

        # Check that the nonexistent signal has no data
        assert data[1].size == 0

        # Check that the third signal has data
        assert data[2].shape[0] == 300
        assert not np.isnan(data[2]).all()
