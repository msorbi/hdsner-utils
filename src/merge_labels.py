#!/usr/bin/env python3
# merge two single-class IOB files into a multi-class file
import argparse
import os
import random
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pers-input", type=str, required=True, help="input pers IOB file")
    parser.add_argument("--loc-input", type=str, required=True, help="input loc IOB file")
    parser.add_argument("--output", type=str, required=True, help="output IOB file")
    parser.add_argument("--field-delimiter", type=str, default="\t", help="field delimiter, default TAB")
    args = parser.parse_args()
    return args


def merge_iob_labels(pers_labels, loc_labels):
    """
    Merge two IOB label sequences (PERS and LOC) into a single sequence based on specified rules.

    Parameters:
    - pers_labels: List of IOB labels for the PERS class.
    - loc_labels: List of IOB labels for the LOC class.

    Returns:
    - merged_labels: List of merged IOB labels.
    """
    n = len(pers_labels)
    merged_labels = ['O'] * n
    i = 0

    while i < n:
        # Determine if a PERS span starts at position i
        if pers_labels[i].startswith('B-'):
            pers_start = i
            pers_end = i + 1
            while pers_end < n and pers_labels[pers_end].startswith('I-'):
                pers_end += 1
        else:
            pers_start = pers_end = None

        # Determine if a LOC span starts at position i
        if loc_labels[i].startswith('B-'):
            loc_start = i
            loc_end = i + 1
            while loc_end < n and loc_labels[loc_end].startswith('I-'):
                loc_end += 1
        else:
            loc_start = loc_end = None

        # Decide which span to select based on the rules
        if pers_start is not None and loc_start is not None:
            if pers_start < loc_start:
                selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
            elif loc_start < pers_start:
                selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
            else:  # Starts are equal
                pers_length = pers_end - pers_start
                loc_length = loc_end - loc_start
                if pers_length > loc_length:
                    selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
                elif loc_length > pers_length:
                    selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
                else:
                    selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
        elif pers_start is not None:
            selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
        elif loc_start is not None:
            selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
        else:
            i += 1
            continue

        # Assign labels to the merged sequence
        merged_labels[selected_start] = f'B-{selected_type}'
        for j in range(selected_start + 1, selected_end):
            merged_labels[j] = f'I-{selected_type}'

        # Advance the index to the end of the selected span
        i = selected_end

    return merged_labels

def merge_files(pers_input, loc_input, output, field_delimiter="\t"):
    with open(pers_input, "r") as fp:
        pers = fp.read()
    pers = pers.strip().split("\n\n")
    with open(loc_input, "r") as fp:
        loc = fp.read()
    loc = loc.strip().split("\n\n")
    if len(pers) != len(loc):
        print(f"WARNING: different number of sequences: {pers_input} - {loc_input}")
    output_data = []
    for p,l in zip(pers, loc):
        if field_delimiter not in p:
            output_data.append(p)
            continue
        tokens = [x.split(field_delimiter)[0] for x in p.split("\n")]
        pers_labels = [x.split(field_delimiter)[1] for x in p.split("\n")]
        loc_labels = [x.split(field_delimiter)[1] for x in l.split("\n")]
        if len(pers_labels) != len(loc_labels):
            print(f"WARNING: different number of tokens: {pers_input} - {loc_input}")
        merged_labels = merge_iob_labels(pers_labels, loc_labels)
        output_data.append("\n".join(f"{t}{field_delimiter}{l}" for t,l in zip(tokens, merged_labels)))
    with open(output, "w") as fp:
        fp.write("\n\n".join(output_data) + "\n")

def main():
    args = parse_args()
    kwargs = dict(args._get_kwargs())
    merge_files(**kwargs)

if __name__ == "__main__":
    main()
