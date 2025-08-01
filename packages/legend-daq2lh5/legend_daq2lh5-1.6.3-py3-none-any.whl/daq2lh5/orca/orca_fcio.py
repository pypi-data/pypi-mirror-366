from __future__ import annotations

import copy
import logging
from typing import Any

from fcio import FCIO, Tags

from daq2lh5.fc.fc_config_decoder import FCConfigDecoder
from daq2lh5.fc.fc_event_decoder import FCEventDecoder
from daq2lh5.fc.fc_eventheader_decoder import FCEventHeaderDecoder, get_fcid, get_key
from daq2lh5.fc.fc_fsp_decoder import (
    FSPConfigDecoder,
    FSPEventDecoder,
    FSPStatusDecoder,
)
from daq2lh5.fc.fc_status_decoder import FCStatusDecoder
from daq2lh5.fc.fc_status_decoder import get_key as get_fc_status_key

from ..raw_buffer import RawBufferList
from .orca_base import OrcaDecoder
from .orca_header import OrcaHeader
from .orca_packet import OrcaPacket

log = logging.getLogger(__name__)


# FCIO streams are stateful and need to be accessible for all decoders.
fcio_stream_library = dict()


def get_fcio_stream(streamid):
    if streamid in fcio_stream_library:
        return fcio_stream_library[streamid]
    else:
        fcio_stream_library[streamid] = FCIO()
        return fcio_stream_library[streamid]


def extract_header_information(header: OrcaHeader):

    fc_hdr_info = {
        "key_list": {},
        "n_adc": {},
        "adc_card_layout": {},
        "wf_len": {},
        "fsp_enabled": {},
        "n_card": {},
    }

    fc_card_info_dict = header.get_object_info(
        [
            "ORFlashCamGlobalTriggerModel",
            "ORFlashCamTriggerModel",
            "ORFlashCamADCModel",
            "ORFlashCamADCStdModel",
        ]
    )

    fc_listener_info_list = header.get_readout_info("ORFlashCamListenerModel")
    for fc_listener_info in fc_listener_info_list:
        fcid = fc_listener_info["uniqueID"]  # it should be called listener_id
        if fcid == 0:
            raise ValueError("got fcid=0 unexpectedly!")
        aux_hw_info = header.get_auxhw_info("ORFlashCamListenerModel", fcid)
        if "fspEnabled" in aux_hw_info:
            fc_hdr_info["fsp_enabled"][fcid] = aux_hw_info["fspEnabled"]
        else:
            fc_hdr_info["fsp_enabled"][fcid] = False

        fc_hdr_info["wf_len"][fcid] = header.get_auxhw_info(
            "ORFlashCamListenerModel", fcid
        )["eventSamples"]
        fc_hdr_info["n_adc"][fcid] = 0
        fc_hdr_info["n_card"][fcid] = 0
        fc_hdr_info["key_list"][fcid] = []
        fc_hdr_info["adc_card_layout"][fcid] = {}
        for child in fc_listener_info["children"]:

            crate = child["crate"]
            card = child["station"]
            card_address = fc_card_info_dict[crate][card]["CardAddress"]
            fc_hdr_info["adc_card_layout"][fcid][card_address] = (
                crate,
                card,
                card_address,
            )
            fc_hdr_info["n_card"][fcid] += 1

            if crate not in fc_card_info_dict:
                raise RuntimeError(f"no crate {crate} in fc_card_info_dict")
            if card not in fc_card_info_dict[crate]:
                raise RuntimeError(f"no card {card} in fc_card_info_dict[{crate}]")

            for fc_input in range(len(fc_card_info_dict[crate][card]["Enabled"])):
                if not fc_card_info_dict[crate][card]["Enabled"][fc_input]:
                    continue

                fc_hdr_info["n_adc"][fcid] += 1
                key = get_key(fcid, card_address, fc_input)

                if key in fc_hdr_info["key_list"][fcid]:
                    log.warning(f"key {key} already in key_list...")
                else:
                    fc_hdr_info["key_list"][fcid].append(key)

    return fc_hdr_info


class ORFCIOConfigDecoder(OrcaDecoder):
    def __init__(self, header: OrcaHeader = None, **kwargs) -> None:

        self.decoder = FCConfigDecoder()
        self.fsp_decoder = None
        self.decoded_values = {}
        self.key_list = {"fc_config": [], "fsp_config": []}
        self.max_rows_in_packet = 0

        super().__init__(header=header, **kwargs)

        # The ConfigDecoder is always required for decoding fcio data.
        # When OrcaStreamer.open_stream is called, we close any open fcio stream
        for fcio_stream in fcio_stream_library.values():
            fcio_stream.close()

    def set_header(self, header: OrcaHeader) -> None:
        self.header = header
        self.fc_hdr_info = extract_header_information(header)
        self.decoded_values["fcid"] = copy.deepcopy(self.decoder.get_decoded_values())

        for fcid in self.fc_hdr_info["fsp_enabled"]:
            self.key_list["fc_config"].append(f"fcid_{fcid}/config")
            if self.fc_hdr_info["fsp_enabled"][fcid]:
                self.fsp_decoder = FSPConfigDecoder()
                self.key_list["fsp_config"].append(f"swtid_{fcid}/config")
                self.decoded_values["swtid"] = copy.deepcopy(
                    self.fsp_decoder.get_decoded_values()
                )
        self.max_rows_in_packet = 1

    def get_key_lists(self) -> list[list[str]]:
        return list(self.key_list.values())

    def get_decoded_values(self, key: str = None) -> dict[str, Any]:
        if (
            isinstance(key, str)
            and key.startswith("swtid_")
            and self.fsp_decoder is not None
        ):
            return self.decoded_values["swtid"]
        elif (isinstance(key, str) and key.startswith("fcid_")) or key is None:
            return self.decoded_values["fcid"]
        raise KeyError(f"no decoded values for key {key}")

    def decode_packet(
        self, packet: OrcaPacket, packet_id: int, rbl: RawBufferList
    ) -> bool:

        fcio_stream = get_fcio_stream(packet[2])
        if fcio_stream.is_open():
            raise NotImplementedError(
                f"FCIO stream with stream id {packet[2]} already opened. Update of FCIOConfig is not supported."
            )
        else:
            fcio_stream.open(memoryview(packet[3:]))

        if fcio_stream.config.streamid != packet[2]:
            log.warning(
                f"The expected stream id {packet[2]} does not match the contained stream id "
                f"{fcio_stream.config.streamid}"
            )

        config_rbkd = rbl.get_keyed_dict()

        fcid = fcio_stream.config.streamid & 0xFFFF

        # TODO: the decoders could fetch lgdo's using it's key_list
        fc_key = f"fcid_{fcid}/config"
        any_full = self.decoder.decode_packet(
            fcio_stream, config_rbkd[fc_key], packet_id
        )
        if self.fsp_decoder is not None and self.fc_hdr_info["fsp_enabled"][fcid]:
            fsp_key = f"swtid_{fcid}/config"
            any_full |= self.fsp_decoder.decode_packet(
                fcio_stream, config_rbkd[fsp_key], packet_id
            )

        return bool(any_full)


class ORFCIOStatusDecoder(OrcaDecoder):
    def __init__(self, header: OrcaHeader = None, **kwargs) -> None:

        self.decoder = FCStatusDecoder()
        self.fsp_decoder = None
        self.decoded_values = {}
        self.key_list = []
        self.max_rows_in_packet = 0
        super().__init__(header=header, **kwargs)

    def set_header(self, header: OrcaHeader) -> None:
        """Setter for headers. Overload to set card parameters, etc."""
        self.header = header
        self.fc_hdr_info = extract_header_information(header)

        for fcid in self.fc_hdr_info["n_card"]:
            # If the data was taken without a master distribution module,
            # i.e. only one ADC Module the decoder will just not write to the buffer.

            # MDB key
            key_list_fcid = [get_fc_status_key(fcid, 0)]
            # ADC module keys
            key_list_fcid += [
                get_fc_status_key(fcid, 0x2000 + i)
                for i in range(self.fc_hdr_info["n_card"][fcid])
            ]
            self.key_list.append(key_list_fcid)
            self.decoded_values["fcid"] = copy.deepcopy(
                self.decoder.get_decoded_values()
            )
            if self.fc_hdr_info["fsp_enabled"][fcid]:
                self.fsp_decoder = FSPStatusDecoder()
                self.key_list.append([f"swtid_{fcid}/status"])
                self.decoded_values["swtid"] = copy.deepcopy(
                    self.fsp_decoder.get_decoded_values()
                )
        self.max_rows_in_packet = max(self.fc_hdr_info["n_card"].values()) + 1

    def get_key_lists(self) -> list[list[str]]:
        return copy.deepcopy(self.key_list)

    def get_decoded_values(self, key: str = None) -> dict[str, Any]:

        if (
            isinstance(key, str)
            and key.startswith("swtid_")
            and self.fsp_decoder is not None
        ):
            return self.decoded_values["swtid"]
        elif (isinstance(key, str) and key.startswith("fcid_")) or key is None:
            return self.decoded_values["fcid"]
        else:
            raise KeyError(f"no decoded values for key {key}")

    def get_max_rows_in_packet(self) -> int:
        return self.max_rows_in_packet

    def decode_packet(
        self, packet: OrcaPacket, packet_id: int, rbl: RawBufferList
    ) -> bool:
        status_rbkd = rbl.get_keyed_dict()

        fcio_stream = get_fcio_stream(packet[2])
        fcio_stream.set_mem_field(memoryview(packet[3:]))

        any_full = False

        if not fcio_stream.get_record():
            raise OSError(
                f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
            )

        if fcio_stream.tag == Tags.FSPStatus:
            if self.fsp_decoder is not None:
                any_full |= self.fsp_decoder.decode_packet(
                    fcio_stream, status_rbkd, packet_id
                )

            if not fcio_stream.get_record():
                raise OSError(
                    f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
                )

        if fcio_stream.tag == Tags.Status:
            any_full |= self.decoder.decode_packet(fcio_stream, status_rbkd, packet_id)

        return bool(any_full)


class ORFCIOEventHeaderDecoder(OrcaDecoder):
    def __init__(self, header: OrcaHeader = None, **kwargs) -> None:

        self.decoder = FCEventHeaderDecoder()
        self.fsp_decoder = None
        self.decoded_values = {}
        self.key_list = {"fc_eventheader": [], "fsp_eventheader": []}

        super().__init__(header=header, **kwargs)

    def set_header(self, header: OrcaHeader) -> None:
        """Setter for headers. Overload to set card parameters, etc."""
        self.header = header

        self.fc_hdr_info = extract_header_information(header)

        key_list = self.fc_hdr_info["key_list"]
        for fcid in key_list:
            self.key_list["fc_eventheader"].append(f"fcid_{fcid}/evt_hdr")
            self.decoded_values["fcid"] = copy.deepcopy(
                self.decoder.get_decoded_values()
            )
            if self.fc_hdr_info["fsp_enabled"][fcid]:
                self.fsp_decoder = FSPEventDecoder()
                self.key_list["fsp_eventheader"].append(f"swtid_{fcid}/evt_hdr")
                self.decoded_values["swtid"] = copy.deepcopy(
                    self.fsp_decoder.get_decoded_values()
                )

        self.max_rows_in_packet = 1

    def get_key_lists(self) -> list[list[str]]:
        return list(self.key_list.values())

    def get_decoded_values(self, key: str = None) -> dict[str, Any]:
        if (
            isinstance(key, str)
            and key.startswith("swtid_")
            and self.fsp_decoder is not None
        ):
            return self.decoded_values["swtid"]
        elif (isinstance(key, str) and key.startswith("fcid_")) or key is None:
            return self.decoded_values["fcid"]
        raise KeyError(f"no decoded values for key {key}")

    def decode_packet(
        self, packet: OrcaPacket, packet_id: int, rbl: RawBufferList
    ) -> bool:
        evthdr_rbkd = rbl.get_keyed_dict()
        fcio_stream = get_fcio_stream(packet[2])
        fcio_stream.set_mem_field(memoryview(packet[3:]))

        any_full = False

        if not fcio_stream.get_record():
            raise OSError(
                f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
            )

        if fcio_stream.tag == Tags.FSPEvent:
            if self.fsp_decoder is not None:
                any_full |= self.fsp_decoder.decode_packet(
                    fcio_stream, evthdr_rbkd, packet_id, is_header=True
                )

            if not fcio_stream.get_record():
                raise OSError(
                    f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
                )

        if fcio_stream.tag == Tags.EventHeader:
            any_full |= self.decoder.decode_packet(fcio_stream, evthdr_rbkd, packet_id)

        return bool(any_full)


class ORFCIOEventDecoder(OrcaDecoder):
    """Decoder for FlashCam FCIO stream data written by ORCA."""

    def __init__(self, header: OrcaHeader = None, **kwargs) -> None:
        self.decoder = FCEventDecoder()
        self.fsp_decoder = None

        self.key_list = []
        self.decoded_values = {}
        self.max_rows_in_packet = 0

        super().__init__(header=header, **kwargs)

    def set_header(self, header: OrcaHeader) -> None:
        """Setter for headers. Overload to set card parameters, etc."""
        self.header = header
        self.fc_hdr_info = extract_header_information(header)
        key_list = self.fc_hdr_info["key_list"]
        for fcid in key_list:
            self.key_list.append(key_list[fcid])
            self.decoded_values[fcid] = copy.deepcopy(self.decoder.get_decoded_values())
            self.decoded_values[fcid]["waveform"]["wf_len"] = self.fc_hdr_info[
                "wf_len"
            ][fcid]
            if self.fc_hdr_info["fsp_enabled"][fcid]:
                self.fsp_decoder = FSPEventDecoder()
                self.key_list.append([f"swtid_{fcid}/event"])
                self.decoded_values["swtid"] = copy.deepcopy(
                    self.fsp_decoder.get_decoded_values()
                )
        self.max_rows_in_packet = max(self.fc_hdr_info["n_adc"].values())

    def get_key_lists(self) -> list[list[int | str]]:
        return copy.deepcopy(self.key_list)

    def get_max_rows_in_packet(self) -> int:
        return self.max_rows_in_packet

    def get_decoded_values(self, key: int | str = None) -> dict[str, Any]:
        if key is None:
            dec_vals_list = list(self.decoded_values.values())
            if len(dec_vals_list) > 0:
                return dec_vals_list[0]
            raise RuntimeError("decoded_values not built")

        if (
            isinstance(key, str)
            and key.startswith("swtid_")
            and self.fsp_decoder is not None
        ):
            return self.decoded_values["swtid"]
        elif isinstance(key, int):
            fcid = get_fcid(key)
            if fcid in self.decoded_values:
                return self.decoded_values[fcid]

        raise KeyError(f"no decoded values for key {key}")

    def decode_packet(
        self, packet: OrcaPacket, packet_id: int, rbl: RawBufferList
    ) -> bool:
        """Decode the ORCA FlashCam ADC packet."""
        evt_rbkd = rbl.get_keyed_dict()

        fcio_stream = get_fcio_stream(packet[2])
        fcio_stream.set_mem_field(memoryview(packet[3:]))

        any_full = False

        if not fcio_stream.get_record():
            raise OSError(
                f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
            )

        if fcio_stream.tag == Tags.FSPEvent:
            if self.fsp_decoder is not None:
                any_full |= self.fsp_decoder.decode_packet(
                    fcio_stream, evt_rbkd, packet_id
                )

            if not fcio_stream.get_record():
                raise OSError(
                    f"Missing record in FCIO stream {fcio_stream.config.streamid & 0xFFFF}."
                )

        if fcio_stream.tag == Tags.Event or fcio_stream.tag == Tags.SparseEvent:
            any_full |= self.decoder.decode_packet(fcio_stream, evt_rbkd, packet_id)

        return bool(any_full)
