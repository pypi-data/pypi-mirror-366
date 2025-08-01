from __future__ import annotations

import logging
import os

import h5py
import lgdo
from lgdo import lh5

from .. import utils
from ..buffer_processor.buffer_processor import buffer_processor
from ..raw_buffer import RawBuffer, RawBufferLibrary

log = logging.getLogger(__name__)


def lh5_buffer_processor(
    lh5_raw_file_in: str,
    overwrite: bool = False,
    out_spec: dict = None,
    proc_file_name: str = None,
    db_dict: dict = None,
) -> None:
    r"""Process raw buffers from an LH5 file.

    This function performs data processing on an existing raw-level LH5 file
    according to `out_spec`.  It iterates through any valid table in the
    `lh5_raw_file_in` file and checks that either the `group_name` or the
    `out_name` of this table are found in the `out_spec`. If there is a valid
    `proc_spec` entry in the `out_spec`, then the table is stored in a
    :class:`RawBuffer` and the :func:`RawBuffer` is passed to the buffer
    processor. If no `proc_spec` is found, the table is written to the file
    without any modifications.


    Parameters
    ----------
    lh5_raw_file_in
        the path of a file created by :func:`~.build_raw.build_raw`.
    overwrite
        sets whether to overwrite the output file(s) if it (they) already
        exist.
    out_spec
        an `out_spec` for :func:`~.build_raw.build_raw` also containing a
        dictionary named `proc_spec` used for data processing.  See
        :func:`.buffer_processor` for an example of such an `out_spec`.
    proc_file_name
        The path to the processed output file created. If ``None``, uses
        ``{lh5_raw_file_in}_proc.lh5`` as the output filename.

    Notes
    -----
    This function assumes that all raw file data are stored in at most two
    :class:`h5py.Group`\ s, as in e.g. ``ch000/raw`` or ``raw/geds``
    """

    # Initialize the input raw file
    raw_store = lh5.LH5Store()
    lh5_file = raw_store.gimme_file(lh5_raw_file_in, "r")
    if lh5_file is None:
        raise ValueError(f"input file not found: {lh5_raw_file_in}")
        return

    # List the groups in the raw file
    lh5_groups = lh5.ls(lh5_raw_file_in)
    lh5_tables = []

    # check if group points to raw data; sometimes 'raw' is nested, e.g g024/raw
    for tb in lh5_groups:
        # Make sure that the upper level key isn't a dataset
        if isinstance(lh5_file[tb], h5py.Dataset):
            lh5_tables.append(f"{tb}")
        elif "raw" not in tb and lh5.ls(lh5_file, f"{tb}/raw"):
            lh5_tables.append(f"{tb}/raw")
        # Look one layer deeper for a :meth:`lgdo.Table` if necessary
        elif lh5.ls(lh5_file, f"{tb}"):
            # Check to make sure that this isn't a table itself
            maybe_table = lh5.read(f"{tb}", lh5_file)
            if isinstance(maybe_table, lgdo.Table):
                lh5_tables.append(f"{tb}")
                del maybe_table
            # otherwise, go deeper
            else:
                for sub_table in lh5.ls(lh5_file, f"{tb}"):
                    maybe_table = lh5.read(f"{tb}/{sub_table}", lh5_file)
                    if isinstance(maybe_table, lgdo.Table):
                        lh5_tables.append(f"{tb}/{sub_table}")
                    del maybe_table

    if len(lh5_tables) == 0:
        raise RuntimeError(f"could not find any valid LH5 table in {lh5_raw_file_in}")

    # Initialize the processed file
    # Get the proc_file_name if the user doesn't pass one
    if proc_file_name is None:
        proc_file_name = lh5_raw_file_in
        i_ext = proc_file_name.rfind(".")
        if i_ext != -1:
            proc_file_name = proc_file_name[:i_ext]
        proc_file_name += "_proc.lh5"
    # clear existing output files
    if overwrite:
        if os.path.isfile(proc_file_name):
            os.remove(proc_file_name)
    raw_store.gimme_file(proc_file_name, "a")

    # Do key expansion on the out_spec
    allowed_exts = [ext for exts in utils.__file_extensions__.values() for ext in exts]
    if isinstance(out_spec, str) and any(
        [out_spec.endswith(ext) for ext in allowed_exts]
    ):
        out_spec = utils.load_dict(out_spec)
    if isinstance(out_spec, dict):
        RawBufferLibrary(config=out_spec)

    # Write everything in the raw file to the new file, check for proc_spec under either the group name, out_name, or the name
    for tb in lh5_tables:
        lgdo_obj = lh5.read(f"{tb}", lh5_file)

        # Find the out_name.
        # If the top level group has an lgdo table in it, then the out_name is group
        if len(tb.split("/")) == 1:
            out_name = tb.split("/")[0]
            group_name = "/"  # There is no group name
        # We are only considering nested groups of the form key1/key2/, so key2 is the out name
        else:
            out_name = tb.split("/")[-1]  # the out_name is the last key
            group_name = tb.split("/")[0]  # the group name is the first key

        for decoder_name in out_spec.keys():
            # Check to see if the group name is in the out_spec's dict
            # This is used if there is key expansion
            if group_name in out_spec[decoder_name].keys():
                # Check to see if that group in the out_spec has a `proc_spec` key:
                if "proc_spec" in out_spec[decoder_name][group_name].keys():
                    # Recast the lgdo_obj as a RawBuffer
                    rb = RawBuffer(
                        lgdo=lgdo_obj,
                        out_name=out_name,
                        proc_spec=out_spec[decoder_name][group_name]["proc_spec"],
                    )
                    tmp_table = buffer_processor(
                        rb, db_dict=db_dict[tb] if db_dict is not None else None
                    )
                    # Update the lgdo_obj to be written to the processed file
                    lgdo_obj = tmp_table
                else:
                    pass

            # If there is no key expansion, and no out_name in the out_spec, then the out_name could be in the out_spec's keys, i.e. the name
            elif out_name in out_spec[decoder_name].keys():
                # Check to see if that group in the out_spec has a `proc_spec` key:
                if "proc_spec" in out_spec[decoder_name][out_name].keys():
                    # Recast the lgdo_obj as a RawBuffer
                    rb = RawBuffer(
                        lgdo=lgdo_obj,
                        out_name=out_name,
                        proc_spec=out_spec[decoder_name][out_name]["proc_spec"],
                    )
                    tmp_table = buffer_processor(rb)
                    # Update the lgdo_obj to be written to the processed file
                    lgdo_obj = tmp_table
                else:
                    pass

            # Lastly, having an out_name specified in the out_spec could override the name key. Check for it
            elif (
                (len(list(out_spec[decoder_name].keys())) == 1)
                and (
                    "out_name"
                    in out_spec[decoder_name][list(out_spec[decoder_name].keys())[0]]
                )
                and (
                    out_name
                    == out_spec[decoder_name][list(out_spec[decoder_name].keys())[0]][
                        "out_name"
                    ]
                )
            ):
                # if out_name is a key, check that the out_name matches and use that
                if (
                    "proc_spec"
                    in out_spec[decoder_name][
                        list(out_spec[decoder_name].keys())[0]
                    ].keys()
                ):
                    # Recast the lgdo_obj as a RawBuffer
                    rb = RawBuffer(
                        lgdo=lgdo_obj,
                        out_name=out_name,
                        proc_spec=out_spec[decoder_name][
                            list(out_spec[decoder_name].keys())[0]
                        ]["proc_spec"],
                    )
                    tmp_table = buffer_processor(rb)
                    # Update the lgdo_obj to be written to the processed file
                    lgdo_obj = tmp_table
                else:
                    pass
            else:
                pass

        # Write the (possibly processed) lgdo_obj to a file
        lh5.write(lgdo_obj, out_name, lh5_file=proc_file_name, group=group_name)
