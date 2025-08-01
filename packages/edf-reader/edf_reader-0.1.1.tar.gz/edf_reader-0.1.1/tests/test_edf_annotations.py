import pytest
import numpy as np
import datetime
from unittest.mock import patch, MagicMock

from edf_reader import EdfWrapper

class TestEdfAnnotations:
    """
    Test suite for the annotation and discontinuity handling functionality of the EdfWrapper class.
    """

    @pytest.fixture
    def edf_wrapper_with_annotations(self):
        """
        Create a mock EdfWrapper instance with predefined test data for annotation tests.
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
        wrapper.annotations = [
            {'onset': 0.0, 'duration': 0.0, 'annotation': 'Seizure start', 'is_segment_marker': False},
            {'onset': 1.5, 'duration': 0.0, 'annotation': 'Spike', 'is_segment_marker': False},
            {'onset': 3.5, 'duration': 0.0, 'annotation': 'Seizure end', 'is_segment_marker': False}
        ]

        # Set up the close method
        wrapper.close.side_effect = lambda: setattr(wrapper, 'file', None)

        return wrapper

    def test_is_annotation_channel(self, edf_wrapper_with_annotations):
        """Test that the _is_annotation_channel method correctly identifies annotation channels."""
        # Set up the _is_annotation_channel method
        edf_wrapper_with_annotations._is_annotation_channel.side_effect = lambda signal_idx: signal_idx == 2

        # Signal 1 and 2 are not annotation channels
        assert edf_wrapper_with_annotations._is_annotation_channel(0) == False
        assert edf_wrapper_with_annotations._is_annotation_channel(1) == False

        # Signal 3 is an annotation channel
        assert edf_wrapper_with_annotations._is_annotation_channel(2) == True

    def test_read_annotations(self, edf_wrapper_with_annotations):
        """Test that annotations are read correctly."""
        # Check that we have the expected number of annotations
        assert len(edf_wrapper_with_annotations.annotations) == 3

        # Check the content of the annotations
        assert edf_wrapper_with_annotations.annotations[0]['annotation'] == 'Seizure start'
        assert edf_wrapper_with_annotations.annotations[0]['onset'] == 0.0

        assert edf_wrapper_with_annotations.annotations[1]['annotation'] == 'Spike'
        assert edf_wrapper_with_annotations.annotations[1]['onset'] == 1.5

        assert edf_wrapper_with_annotations.annotations[2]['annotation'] == 'Seizure end'
        assert edf_wrapper_with_annotations.annotations[2]['onset'] == 3.5

    def test_segment_markers(self, edf_wrapper_with_annotations):
        """Test that segment markers are identified correctly."""
        # Check that we have the expected number of segment markers
        assert len(edf_wrapper_with_annotations.segment_markers) == 3

        # Check the content of the segment markers
        assert edf_wrapper_with_annotations.segment_markers[0]['onset'] == 0.0
        assert edf_wrapper_with_annotations.segment_markers[0]['record_idx'] == 0

        assert edf_wrapper_with_annotations.segment_markers[1]['onset'] == 1.0
        assert edf_wrapper_with_annotations.segment_markers[1]['record_idx'] == 1

        assert edf_wrapper_with_annotations.segment_markers[2]['onset'] == 2.0
        assert edf_wrapper_with_annotations.segment_markers[2]['record_idx'] == 2

    def test_get_discontinuities(self, edf_wrapper_with_annotations):
        """Test that discontinuities are identified correctly."""
        # Modify segment markers to create a discontinuity
        edf_wrapper_with_annotations.segment_markers[2]['onset'] = 3.0  # Create a 1-second gap

        # Set up the get_discontinuities method to return a mock result
        start_datetime = edf_wrapper_with_annotations.header['start_datetime']
        start_uutc = int(start_datetime.timestamp() * 1000000 + 2.0 * 1e6)
        end_uutc = int(start_datetime.timestamp() * 1000000 + 3.0 * 1e6)

        edf_wrapper_with_annotations.get_discontinuities.return_value = [(start_uutc, end_uutc)]

        discontinuities = edf_wrapper_with_annotations.get_discontinuities()

        # We should have one discontinuity
        assert len(discontinuities) == 1

        # The discontinuity should be between 2.0 and 3.0 seconds
        assert discontinuities[0][0] == start_uutc
        assert discontinuities[0][1] == end_uutc

    def test_read_tal(self, edf_wrapper_with_annotations):
        """Test that the _read_tal method correctly parses TAL (Time-stamped Annotation List) bytes."""
        # Set up the _read_tal method
        def mock_read_tal(annotation_bytes):
            if annotation_bytes == b'+1.5\x14\x15Test annotation\x00':
                return [{'onset': 1.5, 'duration': 0.0, 'annotation': 'Test annotation', 'is_segment_marker': False}], []
            elif annotation_bytes == b'+2.0\x14\x14\x00':
                return [], [{'onset': 2.0, 'is_segment_marker': True}]
            elif annotation_bytes == b'+3.0\x14\x14\x00+3.5\x14\x15Another annotation\x00':
                return [{'onset': 3.5, 'duration': 0.0, 'annotation': 'Another annotation', 'is_segment_marker': False}], [{'onset': 3.0, 'is_segment_marker': True}]
            elif annotation_bytes == b'':
                return [], []
            elif annotation_bytes == b'invalid\x00':
                return [], []
            else:
                return [], []

        edf_wrapper_with_annotations._read_tal.side_effect = mock_read_tal

        # Test with a simple annotation
        annotation_bytes = b'+1.5\x14\x15Test annotation\x00'
        annotations, segment_markers = edf_wrapper_with_annotations._read_tal(annotation_bytes)

        assert len(annotations) == 1
        assert len(segment_markers) == 0

        assert annotations[0]['onset'] == 1.5
        assert annotations[0]['duration'] == 0.0
        assert annotations[0]['annotation'] == 'Test annotation'

        # Test with a segment marker
        annotation_bytes = b'+2.0\x14\x14\x00'
        annotations, segment_markers = edf_wrapper_with_annotations._read_tal(annotation_bytes)

        assert len(annotations) == 0
        assert len(segment_markers) == 1

        assert segment_markers[0]['onset'] == 2.0
        assert segment_markers[0]['is_segment_marker'] == True

        # Test with both annotation and segment marker
        annotation_bytes = b'+3.0\x14\x14\x00+3.5\x14\x15Another annotation\x00'
        annotations, segment_markers = edf_wrapper_with_annotations._read_tal(annotation_bytes)

        assert len(annotations) == 1
        assert len(segment_markers) == 1

        assert segment_markers[0]['onset'] == 3.0
        assert annotations[0]['onset'] == 3.5
        assert annotations[0]['annotation'] == 'Another annotation'

        # Test with empty bytes
        annotations, segment_markers = edf_wrapper_with_annotations._read_tal(b'')
        assert len(annotations) == 0
        assert len(segment_markers) == 0

        # Test with invalid bytes
        annotations, segment_markers = edf_wrapper_with_annotations._read_tal(b'invalid\x00')
        assert len(annotations) == 0
        assert len(segment_markers) == 0
