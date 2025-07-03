def create_chunks(self, audio_np):
    """Split audio into chunks with overlap...
    First chunk is 5s, subsequent chunks are 20s.
    """
    first_chunk_duration = 5  # seconds
    subsequent_chunk_duration = 20  # seconds
    overlap_duration = self.overlap_duration

    # Convert durations to samples
    first_chunk_size = int(self.target_sample_rate * first_chunk_duration)
    subsequent_chunk_size = int(self.target_sample_rate * subsequent_chunk_duration)
    overlap_size = int(self.target_sample_rate * overlap_duration)

    audio_len_samples = len(audio_np)
    chunks_data = []
    chunk_time_ranges = []

    core_start_sample = 0
    chunk_count = 0

    while core_start_sample < audio_len_samples:
        if chunk_count == 0:
            core_chunk_size = first_chunk_size
        else:
            core_chunk_size = subsequent_chunk_size

        core_end_sample = core_start_sample + core_chunk_size
        actual_end_sample = min(core_end_sample + overlap_size, audio_len_samples)

        chunk = audio_np[core_start_sample:actual_end_sample]
        chunks_data.append(chunk)

        # Calculate time range in seconds
        actual_start_time = core_start_sample / self.target_sample_rate
        actual_end_time = actual_end_sample / self.target_sample_rate
        chunk_time_ranges.append((actual_start_time, actual_end_time))

        # Move start by core chunk size (not actual chunk size)
        core_start_sample += core_chunk_size
        chunk_count += 1

    return chunks_data, chunk_time_ranges