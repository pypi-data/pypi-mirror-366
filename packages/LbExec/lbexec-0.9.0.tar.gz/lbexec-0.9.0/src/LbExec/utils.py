###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Utility functions for writing lbexec payloads."""
from __future__ import annotations

__all__ = [
    "read_xml_file_catalog",
    "extract_single_filetype_from_input_file",
    "resolve_input_files",
    "write_summary_xml",
    "get_output_filename",
]

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

from .cli_utils import log_info  # type: ignore
from .options import DataOptions, OptionsBase, SimulationOptions

SUMMARY_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
    <success>True</success>
    <step>finalize</step>
    <usage><stat unit="KB" useOf="MemoryMaximum">0</stat></usage>
    <input>
{input_files}
    </input>
    <output>
{output_files}
    </output>
</summary>
"""
XML_FILE_TEMPLATE = '     <file GUID="" name="{name}" status="full">{n}</file>'


def read_xml_file_catalog(xml_file_catalog):
    """Lookup the LFN->PFN mapping from the XML file catalog."""
    if xml_file_catalog is None:
        return {}

    tree = ET.parse(xml_file_catalog)
    pfn_lookup: dict[str, list[str]] = {}  # type: ignore
    for file in tree.findall("./File"):
        lfns = [x.attrib.get("name") for x in file.findall("./logical/lfn")]
        pfns = [x.attrib.get("name") for x in file.findall("./physical/pfn")]
        if len(lfns) > 1:
            raise NotImplementedError(lfns)
        if lfns:
            lfn = lfns[0]
        elif len(pfns) > 1:
            raise NotImplementedError(pfns)
        else:
            lfn = pfns[0]
        pfn_lookup[f"LFN:{lfn}"] = pfns
    return pfn_lookup


def extract_single_filetype_from_input_file(options):
    def _extract(s):
        filename = s.split("/")[-1]
        parts = filename.split(".")
        if len(parts) >= 3:
            return parts[-2]
        raise NotImplementedError

    filetypes = set(_extract(infile) for infile in options.input_files)
    if len(filetypes) != 1:
        raise NotImplementedError(
            "Multiple input filetypes in input_files, when only one filetype was expected."
        )
    return filetypes.pop()


def resolve_input_files(input_files, file_catalog):
    """Resolve LFNs to PFNs using what was returned from read_xml_file_catalog."""
    resolved = []
    for input_file in input_files:
        if input_file.startswith("LFN:"):
            if input_file in file_catalog:
                print("Resolved", input_file, "to", file_catalog[input_file][0])
                input_file = file_catalog[input_file][0]
            else:
                raise ValueError(f"Could not resolve {input_file}: {file_catalog}")
        resolved.append(input_file)
    return resolved


def write_summary_xml(
    options: OptionsBase,
    output_files: Iterable[str],
    *,
    n_events: dict[str, int] | None = None,
):
    """Write a summary XML file with input and output files."""
    if n_events is None:
        n_events = {}
    match options:
        case SimulationOptions():
            input_files = []
        case DataOptions():
            input_files = options.input_files
        case _:
            raise NotImplementedError(f"Unsupported options type: {type(options)}")
    summary_xml = SUMMARY_XML_TEMPLATE.format(
        input_files="\n".join(
            XML_FILE_TEMPLATE.format(
                name=name if name.startswith("LFN:") else f"PFN:{name}", n=1
            )
            for name in input_files
        ),
        output_files="\n".join(
            XML_FILE_TEMPLATE.format(
                # assume that every input file contributed to each output file
                name=f"PFN:{name}",
                n=n_events.get(name, len(input_files)),
            )
            for name in output_files
        ),
    )
    if options.xml_summary_file:
        log_info(f"Writing XML summary to {options.xml_summary_file}")
        Path(options.xml_summary_file).write_text(summary_xml)


def get_output_filename(key, options, extra_opts, lumi_tree_key=None):
    if not extra_opts.write:
        # assume we write one output filetype
        # if "output_file" contains {stream}, we need to infer the filetype
        # otherwise return options.output_file

        if "{stream}" not in options.output_file_:
            yield options.output_file
        else:
            # get input filetype, substitute it into {stream}, and yield
            yield extract_single_filetype_from_input_file(options)

    for mapstr in extra_opts.write or []:
        fn, rex = mapstr.split("=")
        if re.match(rex, key) or lumi_tree_key == key:
            yield fn
