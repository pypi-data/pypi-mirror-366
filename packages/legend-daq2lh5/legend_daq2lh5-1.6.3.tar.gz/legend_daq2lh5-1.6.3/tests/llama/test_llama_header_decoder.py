import datetime

import pytest

from daq2lh5.llama.llama_header_decoder import LLAMAHeaderDecoder
from daq2lh5.llama.llama_streamer import LLAMAStreamer


def test_read_header(test_data_path):
    streamer = LLAMAStreamer()
    streamer.open_stream(test_data_path)
    header = streamer.header_decoder
    assert isinstance(header, LLAMAHeaderDecoder)
    # following data is specific to the particular test file:
    assert header.version_major == 2
    assert header.version_minor == 0
    assert header.version_patch == 0
    assert header.length_econf == 88  # 22 words of 4 bytes
    assert header.number_chOpen == 2
    assert header.global_configs["initial_timestamp"] == pytest.approx(
        datetime.datetime(2024, 12, 18, 15, 1, 58).timestamp(), abs=0.1
    )
    assert header.global_configs["initial_timestamp_accuracy"] == pytest.approx(1.0)
    streamer.close_stream()
