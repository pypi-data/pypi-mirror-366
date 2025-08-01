import datetime
import numpy as np
import time
import os
import io



class EdfWrapper():
    """
    A class to read EDF and EDF+D (European Data Format with discontinuous recordings) files.
    This implementation optimizes file access patterns for better network performance.
    This implementation reads directly from binary without external dependencies.
    """

    def __init__(self, file, buffer_size=8192):
        """
        Initialize the EDF reader with the file path and keep the file open

        Args:
            file_path: Path to the EDF file
            buffer_size: Buffer size for reads (bytes)
        """

        self.file_path = file
        self.header = {}
        self.signals_header = []
        self.segment_markers = []
        self.segment_marker_indices = []
        self.annotations = []
        self.buffer_size = buffer_size


        # Cache for reducing network I/O
        self._file_cache = {}

        # Open the file and keep it open
        self.file = open(self.file_path, 'rb')

        self._read_header()
        self.read_annotations()


    def __del__(self):
        """
        Destructor to ensure the file is closed when the object is deleted
        """
        if hasattr(self, 'file') and self.file:
            self.file.close()

    def close(self):
        """
        Explicitly close the file
        """
        if hasattr(self, 'file') and self.file:
            self.file.close()
            self.file = None

    def _read_header(self):
        """
        Read the EDF header information from the file
        """
        # Seek to the beginning of the file
        self.file.seek(0)

        # Read entire fixed header at once (256 bytes)
        header_bytes = self.file.read(256)
        header_io = io.BytesIO(header_bytes)

        # Parse header in memory
        version = header_io.read(8).decode('ascii').strip()
        patient_id = header_io.read(80).decode('ascii').strip()
        recording_id = header_io.read(80).decode('ascii').strip()
        start_date = header_io.read(8).decode('ascii').strip()
        start_time = header_io.read(8).decode('ascii').strip()
        header_bytes_count = int(header_io.read(8).decode('ascii').strip())
        reserved = header_io.read(44).decode('ascii').strip()
        num_data_records = int(header_io.read(8).decode('ascii').strip())
        data_record_duration = float(header_io.read(8).decode('ascii').strip())
        num_signals = int(header_io.read(4).decode('ascii').strip())

        # Store in header dictionary
        self.header = {
            'version': version,
            'patient_id': patient_id,
            'recording_id': recording_id,
            'start_date': start_date,
            'start_time': start_time,
            'header_bytes': header_bytes_count,
            'reserved': reserved,
            'num_data_records': num_data_records,
            'data_record_duration': data_record_duration,
            'num_signals': num_signals,
            'is_edf_plus_d': '+' in reserved,  # Check if it's EDF+D format
        }

        # Parse start date and time
        try:
            day, month, year = int(start_date[:2]), int(start_date[3:5]), int(start_date[6:])
            if year < 85:  # EDF+ specification: 1985-2084
                year += 2000
            else:
                year += 1900

            hour, minute, second = int(start_time[:2]), int(start_time[3:5]), int(start_time[6:])
            self.header['start_datetime'] = datetime.datetime(year, month, day, hour, minute, second).replace(
                tzinfo=datetime.timezone.utc)
        except ValueError:
            self.header['start_datetime'] = None

        # Calculate and read entire variable header section at once
        variable_header_size = (num_signals * 16) + (num_signals * 80) + (num_signals * 8) + \
                               (num_signals * 8) + (num_signals * 8) + (num_signals * 8) + \
                               (num_signals * 8) + (num_signals * 80) + (num_signals * 8) + \
                               (num_signals * 32)

        variable_header_bytes = self.file.read(variable_header_size)
        var_header_io = io.BytesIO(variable_header_bytes)

        # Pre-allocate arrays for all signal headers
        labels = []
        transducer_types = []
        physical_dimensions = []
        physical_mins = []
        physical_maxs = []
        digital_mins = []
        digital_maxs = []
        prefiltering = []
        samples_per_record = []
        reserved_signal = []

        # Read all labels at once
        for _ in range(num_signals):
            labels.append(var_header_io.read(16).decode('ascii').strip())

        # Read all transducer types at once
        for _ in range(num_signals):
            transducer_types.append(var_header_io.read(80).decode('ascii').strip())

        # Continue reading rest of variable header blocks
        for _ in range(num_signals):
            physical_dimensions.append(var_header_io.read(8).decode('ascii').strip())

        for _ in range(num_signals):
            physical_mins.append(float(var_header_io.read(8).decode('ascii').strip()))

        for _ in range(num_signals):
            physical_maxs.append(float(var_header_io.read(8).decode('ascii').strip()))

        for _ in range(num_signals):
            digital_mins.append(int(var_header_io.read(8).decode('ascii').strip()))

        for _ in range(num_signals):
            digital_maxs.append(int(var_header_io.read(8).decode('ascii').strip()))

        for _ in range(num_signals):
            prefiltering.append(var_header_io.read(80).decode('ascii').strip())

        for _ in range(num_signals):
            samples_per_record.append(int(var_header_io.read(8).decode('ascii').strip()))

        for _ in range(num_signals):
            reserved_signal.append(var_header_io.read(32).decode('ascii').strip())

        # Store signal headers
        for i in range(num_signals):
            self.signals_header.append({
                'label': labels[i],
                'transducer_type': transducer_types[i],
                'physical_dimension': physical_dimensions[i],
                'physical_min': physical_mins[i],
                'physical_max': physical_maxs[i],
                'digital_min': digital_mins[i],
                'digital_max': digital_maxs[i],
                'prefiltering': prefiltering[i],
                'samples_per_record': samples_per_record[i],
                'reserved': reserved_signal[i],
                'scaling_factor': (physical_maxs[i] - physical_mins[i]) / (digital_maxs[i] - digital_mins[i]),
                'dc_offset': physical_mins[i] - (physical_maxs[i] - physical_mins[i]) * digital_mins[i] / (
                        digital_maxs[i] - digital_mins[i])
            })

        # Precalculate record size for faster access later
        self.record_size = sum(s['samples_per_record'] * 2 for s in self.signals_header)

        if self.header['num_data_records'] == -1:
            try:
                file_size = os.path.getsize(self.file_path)
                data_bytes = file_size - self.header['header_bytes']
                # if data_bytes % self.record_size != 0:
                #     raise ValueError("EDF file data section is not aligned with record size.")
                self.header['num_data_records'] = data_bytes // self.record_size
            except Exception as e:
                raise RuntimeError(f"Failed to infer number of records from file size: {e}")

    def _is_annotation_channel(self, signal_idx):
        """
        Check if the signal is an annotation channel (EDF+)

        Args:
            signal_idx: Index of the signal in signals_header

        Returns:
            bool: True if it's an annotation channel
        """
        signal = self.signals_header[signal_idx]
        return signal['label'] == 'EDF Annotations'

    def _read_tal(self, annotation_bytes):
        """
        Process TAL (Time-stamped Annotation List) bytes

        Args:
            annotation_bytes: Bytes containing the annotations

        Returns:
            tuple: (annotations, segment markers)
        """
        annotations = []
        segment_info = []

        if not annotation_bytes:
            return annotations, segment_info

        try:
            # Decode the entire block at once
            annotation_str = annotation_bytes.decode('utf-8', errors='replace').rstrip('\x00')

            # Split by null terminators to get individual TALs
            tals = annotation_str.split('\x00')

            for tal in tals:
                if not tal:
                    continue

                parts = tal.split('\x14')

                try:
                    # Fast path for common case: just try to parse directly
                    if len(parts) >= 1:
                        onset = float(parts[0])

                        duration = 0.0
                        annotation_text = ''

                        if len(parts) > 1:
                            duration_annotation = parts[1].split('\x15', 1)
                            if duration_annotation[0]:
                                duration = float(duration_annotation[0])

                            if len(duration_annotation) > 1:
                                annotation_text = duration_annotation[1].strip()

                        entry = {
                            'onset': onset,
                            'duration': duration,
                            'annotation': annotation_text,
                            'is_segment_marker': '\x14\x14' in tal
                        }

                        if entry['is_segment_marker']:
                            segment_info.append(entry)
                        else:
                            annotations.append(entry)

                except (ValueError, IndexError):
                    continue  # Skip problematic TAL entries
        except Exception:
            # Fallback if there's an issue with the entire block
            pass

        return annotations, segment_info

    def _read_chunk(self, offset, size):
        """
        Read a chunk of data with optional caching

        Args:
            offset: File offset
            size: Bytes to read

        Returns:
            bytes: The data read
        """
        # Check if we have this chunk in cache
        cache_key = f"{offset}:{size}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]

        # If not in cache, read from file
        self.file.seek(offset)
        data = self.file.read(size)

        # Selectively cache small chunks
        if size <= self.buffer_size:
            self._file_cache[cache_key] = data

        return data

    def read_annotations(self):
        """
        Read all annotations from the file in an optimized way.
        Uses a single large read operation for all annotation data.
        """
        self._file_cache.clear()  # Clear cache before new operation

        # For standard EDF (non-EDF+D), create synthetic segments
        if not self.header.get('is_edf_plus_d'):
            segment_markers = [{'record_idx': i, 'onset': v} for i, v in zip(np.arange(self.header['num_data_records']),
                                                                             np.arange(
                                                                                 self.header['num_data_records']) *
                                                                             self.header['data_record_duration'])]
            self.annotations, self.segment_markers = [], segment_markers
            return

        # Find annotation channel
        annotation_idx = -1
        for i, signal in enumerate(self.signals_header):
            if signal['label'] == 'EDF Annotations':
                annotation_idx = i
                break

        if annotation_idx == -1:
            self.annotations, self.segment_markers = [], []
            return

        # Get annotation channel parameters
        samples_per_record = self.signals_header[annotation_idx]['samples_per_record']
        num_records = self.header['num_data_records']
        annotation_bytes_per_record = samples_per_record * 2  # 2 bytes per sample (int16)

        # Calculate offsets once
        data_offset = self.header['header_bytes']
        record_size = self.record_size
        signal_offset = sum(self.signals_header[i]['samples_per_record'] * 2 for i in range(annotation_idx))

        # Pre-allocate annotation data buffer
        annotation_data = bytearray()

        # Use larger buffer reads for network drives - read all annotation data in fewer operations
        if num_records <= 10:
            # For small files, read all in one go
            self.file.seek(data_offset + signal_offset)

            for i in range(num_records):
                annotation_data.extend(self.file.read(annotation_bytes_per_record))
                if i < num_records - 1:  # Skip seek on last record
                    self.file.seek(record_size - annotation_bytes_per_record, 1)
        else:
            # For larger files, use a multi-record buffer approach
            buffer_records = max(1, min(100, num_records // 10))  # Read ~10% of records at once, max 100
            total_reads = (num_records + buffer_records - 1) // buffer_records

            for read_idx in range(total_reads):
                start_record = read_idx * buffer_records
                end_record = min(start_record + buffer_records, num_records)
                records_to_read = end_record - start_record

                # Position at start of first record's annotation data
                chunk_offset = data_offset + (start_record * record_size) + signal_offset

                # Read all annotation data for this chunk
                for rec_idx in range(records_to_read):
                    pos = chunk_offset + (rec_idx * record_size)
                    chunk = self._read_chunk(pos, annotation_bytes_per_record)
                    annotation_data.extend(chunk)

        # Process annotations in a single pass through the aggregated data
        all_annotations, all_segments, all_indices = [], [], []

        # Process in larger chunks for better performance
        for record_idx in range(num_records):
            start = record_idx * annotation_bytes_per_record
            end = start + annotation_bytes_per_record
            record_bytes = annotation_data[start:end]

            record_annotations, record_segments = self._read_tal(record_bytes)

            # Batch extend the lists
            all_annotations.extend(record_annotations)

            for seg in record_segments:
                seg['record_idx'] = record_idx
                all_indices.append(record_idx)

            all_segments.extend(record_segments)

        # Store results
        self.annotations = all_annotations
        self.segment_markers = all_segments
        self.segment_marker_indices = all_indices

        # Clear cache after operation to free memory
        self._file_cache.clear()

    def read_ts_channel_basic_info(self):
        """
        Quickly read basic information about each channel without loading signal data.
        Properly handles discontinuities in EDF+D files.
        Optimized for speed by using cached annotations and minimal file access.

        Returns:
            list: List of dictionaries containing basic info for each channel
        """

        result = []

        # Convert start datetime to microseconds UTC timestamp
        if self.header['start_datetime']:
            start_utc_micro = int(self.header['start_datetime'].timestamp() * 1000000 +
                                  self.segment_markers[0].get('onset', 0) * 1e6)
        else:
            start_utc_micro = 0

        # For EDF+D files, we need to check annotations to determine the true end time
        actual_end_time = int((self.segment_markers[-1].get('onset', 0) + self.header['data_record_duration'] -
                        self.segment_markers[0].get('onset', 0)) * 1e6 + start_utc_micro)


        # Process each channel (excluding annotation channels)
        for i, signal in enumerate(self.signals_header):
            if self._is_annotation_channel(i):
                continue

            # Calculate sampling frequency - ensure integer result
            fsamp = int(np.round(signal['samples_per_record'] / self.header['data_record_duration']))

            # Calculate total number of samples
            nsamp = signal['samples_per_record'] * self.header['num_data_records']

            # Calculate nominal duration (without considering discontinuities)
            nominal_duration_micro = int((nsamp / fsamp) * 1000000)

            # For EDF+D files, use the actual end time from annotations if available
            if self.header['is_edf_plus_d'] and actual_end_time:
                end_utc_micro = actual_end_time
            else:
                # For continuous recordings or if no annotations available
                end_utc_micro = start_utc_micro + nominal_duration_micro

            # Create channel info dictionary
            channel_info = {
                'name': signal['label'],
                'start_time': start_utc_micro,
                'end_time': end_utc_micro,
                'unit': signal['physical_dimension'],
                'fsamp': fsamp,
                'nsamp': nsamp,
                'ufact': 1,
                'timezone': 'no_tz',
            }

            result.append(channel_info)

        return result

    def get_sampling_frequency(self, signal_idx):
        """
        Get the sampling frequency of a signal

        Args:
            signal_idx: Index of the signal

        Returns:
            float: Sampling frequency in Hz
        """
        if signal_idx >= len(self.signals_header):
            return None

        samples_per_record = self.signals_header[signal_idx]['samples_per_record']
        record_duration = self.header['data_record_duration']
        return samples_per_record / record_duration

    def read_ts_channels_uutc(self, channel_map, uutc_map):
        # Time conversion
        file_start_uutc = int(self.header['start_datetime'].timestamp() * 1000000 +
                              self.segment_markers[0].get('onset', 0) * 1e6)

        start_uutc, end_uutc = uutc_map
        if start_uutc is None:
            start_uutc = file_start_uutc
        if end_uutc is None:
            end_uutc = int((self.segment_markers[-1].get('onset', 0) + self.header['data_record_duration'] -
                            self.segment_markers[0].get('onset', 0)) * 1e6 + file_start_uutc)

        relative_start_sec = (start_uutc - file_start_uutc) / 1e6
        relative_end_sec = (end_uutc - file_start_uutc) / 1e6
        relative_shift_sec = self.segment_markers[0].get('onset', 0)

        # Map channel labels to indices once
        signal_indices = {}
        for label in channel_map:
            for j, s in enumerate(self.signals_header):
                if s['label'] == label:
                    signal_indices[label] = j
                    break

        # Pre-calculate sampling frequencies for all needed signals
        frequencies = {idx: self.get_sampling_frequency(idx) for idx in signal_indices.values()}

        # Initialize output arrays with proper sizes
        channel_data = []
        for i, label in enumerate(channel_map):
            if label in signal_indices:
                fs = frequencies[signal_indices[label]]
                total_samples = int(round((relative_end_sec - relative_start_sec) * fs))
                channel_data.append(np.full(total_samples, np.nan))
            else:
                channel_data.append(np.array([]))

        # Create a mapping of data indices to signal indices for faster access
        channel_indices = [(i, signal_indices[label]) for i, label in enumerate(channel_map) if label in signal_indices]

        if not channel_indices:
            return channel_data

        # Constants
        record_size = self.record_size
        data_offset = self.header['header_bytes']

        # Pre-calculate segment data
        segments = self.segment_markers if self.header.get('is_edf_plus_d') else [
            {'onset': i * self.header['data_record_duration'], 'record_idx': i}
            for i in range(self.header['num_data_records'])
        ]

        # Pre-calculate signal offsets to avoid repeated calculations
        signal_offsets = {}
        for _, signal_idx in channel_indices:
            signal_offsets[signal_idx] = sum(
                self.signals_header[i]['samples_per_record'] * 2 for i in range(signal_idx))

        # Filter segments that overlap with our time range
        relevant_segments = [
            segment for segment in segments
            if segment.get('onset', 0) - relative_shift_sec + self.header['data_record_duration'] > relative_start_sec
               and segment.get('onset', 0) - relative_shift_sec < relative_end_sec
               and 0 <= segment.get('record_idx', 0) < self.header['num_data_records']
        ]

        # Process segments in batch when possible
        for segment in relevant_segments:

            seg_start = segment.get('onset', 0) - relative_shift_sec
            seg_end = seg_start + self.header['data_record_duration']
            record_idx = segment.get('record_idx', 0)

            # Calculate overlap
            overlap_start = max(seg_start, relative_start_sec)
            overlap_end = min(seg_end, relative_end_sec)

            # Read and process all channels for this segment
            for data_idx, signal_idx in channel_indices:
                signal = self.signals_header[signal_idx]
                fs = frequencies[signal_idx]

                # Calculate position and read data
                data_pos = data_offset + record_idx * record_size + signal_offsets[signal_idx]

                # Read data
                self.file.seek(data_pos)
                raw_data = self.file.read(signal['samples_per_record'] * 2)
                values = np.frombuffer(raw_data, dtype=np.int16)  # Much faster than struct.unpack
                physical_values = values * signal['scaling_factor'] + signal['dc_offset']

                # Calculate indices with better precision
                output_start_idx = int(np.round((overlap_start - relative_start_sec) * fs))
                output_end_idx = int(np.round((overlap_end - relative_start_sec) * fs))

                data_start_idx = int(np.round((overlap_start - seg_start) * fs))
                data_end_idx = int(np.round((overlap_end - seg_start) * fs))

                # Bounds checking to prevent the shape error
                if (data_end_idx - data_start_idx) > (output_end_idx - output_start_idx):
                    data_end_idx = data_start_idx + (output_end_idx - output_start_idx)

                if (output_end_idx - output_start_idx) > (data_end_idx - data_start_idx):
                    output_end_idx = output_start_idx + (data_end_idx - data_start_idx)

                # Copy data with proper bounds checking
                if (output_start_idx >= 0 and
                        output_end_idx <= len(channel_data[data_idx]) and
                        data_start_idx >= 0 and
                        data_end_idx <= len(physical_values)):
                    channel_data[data_idx][output_start_idx:output_end_idx] = physical_values[
                                                                              data_start_idx:data_end_idx]
                else:
                    print('Incorrect data parsing in EDF reader.')

        return np.array(channel_data)

    def get_discontinuities(self):

        if not self.header.get('is_edf_plus_d'):
            return []

        file_start_uutc = int(self.header['start_datetime'].timestamp() * 1000000 +
                                  self.segment_markers[0].get('onset', 0)*1e6)
        relative_shift_sec = self.segment_markers[0].get('onset', 0)
        seg_starts = [segment.get('onset', 0) for segment in self.segment_markers]

        discontinuities = np.diff(np.array(seg_starts))
        disc_index = np.where(discontinuities > self.header['data_record_duration'])
        if len(disc_index)==0:
            return []
        else:
            # get starts and ends of discontinuities
            disc_starts =  [self.segment_markers[i].get('onset', 0) + self.header['data_record_duration'] - relative_shift_sec for i in disc_index[0]]
            disc_ends = [self.segment_markers[i+1].get('onset', 0) - relative_shift_sec  for i in disc_index[0]]

            disc_starts = [int(file_start_uutc+t*1e6) for t in disc_starts]
            disc_ends = [int(file_start_uutc+t*1e6) for t in disc_ends]

            return list(zip(disc_starts, disc_ends))

# Example usage
if __name__ == "__main__":
    # Specify the file path for testing
    edf_file = "/mnt/ssd4tb/Duke_viewer/GRE_2023_FERj_Inter_24h_1024_Part3.edf"

    print(f"Opening file: {edf_file}")
    start_time = time.perf_counter()
    reader = EdfWrapper(edf_file)
    end_time = time.perf_counter()
    print(f"EDFReader initialized in {end_time - start_time:.4f} seconds")

    info = reader.read_ts_channel_basic_info()

    print(info)

    print(f"Reading data: {edf_file}")
    start_time = time.perf_counter()
    data = reader.read_ts_channels_uutc(['o1', 'o2'], [None, None])
    print(data)
    end_time = time.perf_counter()
    print(f"Reading data took {end_time - start_time:.4f} seconds")
