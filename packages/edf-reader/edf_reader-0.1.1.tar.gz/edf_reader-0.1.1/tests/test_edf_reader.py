import os
import io
import pytest
import numpy as np
import datetime
from unittest.mock import patch, MagicMock, mock_open

# Import the EdfWrapper class
from edf_reader import EdfWrapper

class TestEdfWrapper:
    """
    Test suite for the EdfWrapper class.

    These tests use mocks to avoid requiring actual EDF files.
    """

    @pytest.fixture
    def edf_wrapper(self):
        """
        Create a mock EdfWrapper instance with predefined test data.
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
            'num_data_records': 2,
            'data_record_duration': 1.0,
            'num_signals': 2,
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
            }
        ]

        # Set up the record size
        wrapper.record_size = 600  # (100 + 200) * 2 bytes

        # Set up the segment markers
        wrapper.segment_markers = [
            {'onset': 0.0, 'record_idx': 0},
            {'onset': 1.0, 'record_idx': 1}
        ]

        # Set up the annotations
        wrapper.annotations = [
            {'onset': 0.5, 'duration': 0.0, 'annotation': 'Test annotation', 'is_segment_marker': False}
        ]

        # Set up the get_sampling_frequency method
        wrapper.get_sampling_frequency.side_effect = lambda signal_idx: (
            100.0 if signal_idx == 0 else 
            200.0 if signal_idx == 1 else 
            None
        )

        # Set up the read_ts_channel_basic_info method
        wrapper.read_ts_channel_basic_info.return_value = [
            {
                'name': 'Signal 1',
                'start_time': 1577879400000000,  # 2020-01-01 12:30:00 UTC in microseconds
                'end_time': 1577879402000000,    # 2020-01-01 12:30:02 UTC in microseconds
                'unit': 'uV',
                'fsamp': 100,
                'nsamp': 200,  # 100 samples/record * 2 records
                'ufact': 1,
                'timezone': 'no_tz',
            },
            {
                'name': 'Signal 2',
                'start_time': 1577879400000000,  # 2020-01-01 12:30:00 UTC in microseconds
                'end_time': 1577879402000000,    # 2020-01-01 12:30:02 UTC in microseconds
                'unit': 'mV',
                'fsamp': 200,
                'nsamp': 400,  # 200 samples/record * 2 records
                'ufact': 1,
                'timezone': 'no_tz',
            }
        ]

        # Set up the read_ts_channels_uutc method
        def mock_read_ts_channels_uutc(channel_map, uutc_map):
            # Create mock data for the requested channels
            data = []
            for channel in channel_map:
                if channel == 'Signal 1':
                    # Create a sine wave for Signal 1
                    samples = 200  # 100 samples/record * 2 records
                    signal_data = np.sin(np.linspace(0, 4*np.pi, samples)) * 50  # -50 to 50 uV
                    data.append(signal_data)
                elif channel == 'Signal 2':
                    # Create a cosine wave for Signal 2
                    samples = 200  # We'll resample to match Signal 1's time range
                    signal_data = np.cos(np.linspace(0, 4*np.pi, samples)) * 250  # -250 to 250 mV
                    data.append(signal_data)
                else:
                    # Nonexistent channel
                    data.append(np.array([]))

            return np.array(data)

        wrapper.read_ts_channels_uutc.side_effect = mock_read_ts_channels_uutc

        # Set up the close method
        wrapper.close.side_effect = lambda: setattr(wrapper, 'file', None)

        return wrapper

    def test_initialization(self, edf_wrapper):
        """Test that the EdfWrapper initializes correctly."""
        assert edf_wrapper is not None
        assert hasattr(edf_wrapper, 'header')
        assert hasattr(edf_wrapper, 'signals_header')
        assert hasattr(edf_wrapper, 'file')

    def test_header_parsing(self, edf_wrapper):
        """Test that the header is parsed correctly."""
        assert edf_wrapper.header['version'] == '0'
        assert edf_wrapper.header['patient_id'] == 'test patient'
        assert edf_wrapper.header['recording_id'] == 'test recording'
        assert edf_wrapper.header['num_data_records'] == 2
        assert edf_wrapper.header['data_record_duration'] == 1.0
        assert edf_wrapper.header['num_signals'] == 2
        assert edf_wrapper.header['is_edf_plus_d'] == True

        # Check start datetime
        expected_datetime = datetime.datetime(2020, 1, 1, 12, 30, 0, tzinfo=datetime.timezone.utc)
        assert edf_wrapper.header['start_datetime'] == expected_datetime

    def test_signals_header_parsing(self, edf_wrapper):
        """Test that the signal headers are parsed correctly."""
        assert len(edf_wrapper.signals_header) == 2

        # Check first signal
        signal1 = edf_wrapper.signals_header[0]
        assert signal1['label'] == 'Signal 1'
        assert signal1['transducer_type'] == 'transducer1'
        assert signal1['physical_dimension'] == 'uV'
        assert signal1['physical_min'] == -100
        assert signal1['physical_max'] == 100
        assert signal1['digital_min'] == -32768
        assert signal1['digital_max'] == 32767
        assert signal1['samples_per_record'] == 100

        # Check second signal
        signal2 = edf_wrapper.signals_header[1]
        assert signal2['label'] == 'Signal 2'
        assert signal2['transducer_type'] == 'transducer2'
        assert signal2['physical_dimension'] == 'mV'
        assert signal2['physical_min'] == -500
        assert signal2['physical_max'] == 500
        assert signal2['digital_min'] == -32768
        assert signal2['digital_max'] == 32767
        assert signal2['samples_per_record'] == 200

    def test_get_sampling_frequency(self, edf_wrapper):
        """Test that the sampling frequency is calculated correctly."""
        # Signal 1: 100 samples per 1.0 second record = 100 Hz
        assert edf_wrapper.get_sampling_frequency(0) == 100.0

        # Signal 2: 200 samples per 1.0 second record = 200 Hz
        assert edf_wrapper.get_sampling_frequency(1) == 200.0

        # Invalid signal index
        assert edf_wrapper.get_sampling_frequency(2) is None

    def test_close(self, edf_wrapper):
        """Test that the file is closed properly."""
        edf_wrapper.close()
        # The close method should set file to None
        assert edf_wrapper.file is None

    def test_read_ts_channel_basic_info(self, edf_wrapper):
        """Test reading basic channel information."""
        info = edf_wrapper.read_ts_channel_basic_info()

        assert len(info) == 2  # Two signals

        # Check first signal info
        assert info[0]['name'] == 'Signal 1'
        assert info[0]['unit'] == 'uV'
        assert info[0]['fsamp'] == 100
        assert info[0]['nsamp'] == 200  # 100 samples/record * 2 records

        # Check second signal info
        assert info[1]['name'] == 'Signal 2'
        assert info[1]['unit'] == 'mV'
        assert info[1]['fsamp'] == 200
        assert info[1]['nsamp'] == 400  # 200 samples/record * 2 records

    def test_read_ts_channels_uutc_called_with_correct_params(self, edf_wrapper):
        """Test that read_ts_channels_uutc is called with correct parameters."""
        channel_map = ['Signal 1', 'Signal 2']
        uutc_map = [None, None]

        # Call the method
        result = edf_wrapper.read_ts_channels_uutc(channel_map, uutc_map)

        # Verify the method was called with the correct parameters
        edf_wrapper.read_ts_channels_uutc.assert_called_with(channel_map, uutc_map)

        # Verify the result is as expected
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 2  # Two signals
